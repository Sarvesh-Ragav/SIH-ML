"""
PMIS Live Application Counts Module
==================================

This module handles real-time application counts with caching and rate limiting.
Supports pluggable fetchers for future external API integrations.

Key Features:
- Cached real-time application counts with TTL
- Rate limiting to prevent API abuse
- Graceful degradation when external sources unavailable
- Pluggable architecture for different data sources

Author: Senior ML + Platform Engineer
Date: September 21, 2025
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from functools import lru_cache
import threading
from collections import defaultdict
import warnings

# Optional requests import for future API integration
try:
    import requests
except ImportError:
    requests = None

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class LiveCountsManager:
    """
    Manages real-time application counts with caching and rate limiting.
    
    Provides a pluggable architecture for different data sources
    with automatic fallback and graceful degradation.
    """
    
    def __init__(self, default_ttl_seconds: int = 300, max_calls_per_minute: int = 60):
        """
        Initialize the live counts manager.
        
        Args:
            default_ttl_seconds: Default cache TTL in seconds
            max_calls_per_minute: Rate limit for external API calls
        """
        self.default_ttl = default_ttl_seconds
        self.max_calls_per_minute = max_calls_per_minute
        
        # In-memory cache with TTL
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_lock = threading.Lock()
        
        # Rate limiting
        self._call_history = defaultdict(list)
        self._rate_limit_lock = threading.Lock()
        
        logger.info(f"🔧 Live Counts Manager initialized (TTL: {default_ttl_seconds}s, Rate Limit: {max_calls_per_minute}/min)")
    
    def get_cached_counts(self, internship_ids: List[str], ttl_seconds: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get cached application counts for internships.
        
        Args:
            internship_ids: List of internship IDs to fetch
            ttl_seconds: Custom TTL, defaults to instance TTL
            
        Returns:
            Dict mapping internship_id to count data
        """
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl
        
        current_time = time.time()
        results = {}
        missing_ids = []
        
        with self._cache_lock:
            for internship_id in internship_ids:
                if internship_id in self._cache:
                    cache_time = self._cache_timestamps.get(internship_id, 0)
                    if current_time - cache_time < ttl_seconds:
                        # Cache hit - add freshness info
                        cached_data = self._cache[internship_id].copy()
                        cached_data['freshness_seconds'] = int(current_time - cache_time)
                        results[internship_id] = cached_data
                        continue
                
                missing_ids.append(internship_id)
        
        # Fetch missing data if any
        if missing_ids:
            logger.info(f"🔄 Fetching live counts for {len(missing_ids)} internships")
            fresh_data = self.fetch_live_counts(missing_ids)
            
            # Update cache
            with self._cache_lock:
                for internship_id, data in fresh_data.items():
                    self._cache[internship_id] = data
                    self._cache_timestamps[internship_id] = current_time
                    
                    # Add freshness info
                    data_with_freshness = data.copy()
                    data_with_freshness['freshness_seconds'] = 0
                    results[internship_id] = data_with_freshness
        
        logger.info(f"📊 Returned live counts for {len(results)}/{len(internship_ids)} internships")
        return results
    
    def fetch_live_counts(self, internship_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch live application counts from external sources.
        
        Args:
            internship_ids: List of internship IDs to fetch
            
        Returns:
            Dict mapping internship_id to count data
        """
        # Check rate limit
        if not self._check_rate_limit():
            logger.warning("⚠️  Rate limit exceeded - returning empty results")
            return {}
        
        # Record this call for rate limiting
        self._record_api_call()
        
        try:
            # Try different fetchers in order
            fetchers = [
                self._fetch_from_api,
                self._fetch_from_mock,  # Fallback to mock data
            ]
            
            for fetcher in fetchers:
                try:
                    result = fetcher(internship_ids)
                    if result:  # Non-empty result
                        logger.info(f"✅ Fetched live counts using {fetcher.__name__}")
                        return result
                except Exception as e:
                    logger.warning(f"⚠️  {fetcher.__name__} failed: {e}")
                    continue
            
            logger.warning("⚠️  All fetchers failed - returning empty results")
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error fetching live counts: {e}")
            return {}
    
    def _fetch_from_api(self, internship_ids: List[str], api_endpoint: str = None) -> Dict[str, Dict[str, Any]]:
        """
        Fetch from external API (future implementation).
        
        Args:
            internship_ids: List of internship IDs
            api_endpoint: API endpoint URL
            
        Returns:
            Dict with live count data
        """
        if api_endpoint is None:
            # No API configured - skip this fetcher
            raise ValueError("No API endpoint configured")
        
        if requests is None:
            raise ValueError("requests module not available for API calls")
        
        # Future implementation would make actual API calls
        # response = requests.post(api_endpoint, json={"internship_ids": internship_ids}, timeout=5)
        # return response.json()
        
        raise ValueError("API fetching not implemented yet")
    
    def _fetch_from_mock(self, internship_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch from mock data source (for testing/demo).
        
        Args:
            internship_ids: List of internship IDs
            
        Returns:
            Dict with mock live count data
        """
        logger.info("🎭 Using mock data for live counts")
        
        import random
        
        results = {}
        current_time = datetime.now().isoformat()
        
        # Generate realistic mock data
        for internship_id in internship_ids:
            # Use internship_id hash for consistent mock data
            seed = hash(internship_id) % 1000
            random.seed(seed)
            
            # Generate realistic application counts based on internship popularity
            base_count = random.randint(10, 500)
            
            # Add some time-based variation
            time_factor = (hash(current_time[:13]) % 20) - 10  # ±10 variation per hour
            current_applicants = max(0, base_count + time_factor)
            
            results[internship_id] = {
                'current_applicants': current_applicants,
                'last_seen': current_time,
                'source': 'mock_data',
                'confidence': 0.8  # Mock data confidence
            }
        
        return results
    
    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.
        
        Returns:
            True if within limits, False otherwise
        """
        current_time = time.time()
        minute_ago = current_time - 60
        
        with self._rate_limit_lock:
            # Clean old entries
            recent_calls = [t for t in self._call_history['api_calls'] if t > minute_ago]
            self._call_history['api_calls'] = recent_calls
            
            return len(recent_calls) < self.max_calls_per_minute
    
    def _record_api_call(self):
        """Record an API call for rate limiting."""
        with self._rate_limit_lock:
            self._call_history['api_calls'].append(time.time())
    
    def clear_cache(self):
        """Clear the entire cache."""
        with self._cache_lock:
            self._cache.clear()
            self._cache_timestamps.clear()
        logger.info("🧹 Live counts cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        current_time = time.time()
        
        with self._cache_lock:
            total_entries = len(self._cache)
            fresh_entries = sum(
                1 for timestamp in self._cache_timestamps.values()
                if current_time - timestamp < self.default_ttl
            )
            
            stats = {
                'total_entries': total_entries,
                'fresh_entries': fresh_entries,
                'stale_entries': total_entries - fresh_entries,
                'cache_hit_rate': fresh_entries / max(1, total_entries),
                'ttl_seconds': self.default_ttl,
                'oldest_entry_age': max([current_time - t for t in self._cache_timestamps.values()], default=0)
            }
        
        with self._rate_limit_lock:
            minute_ago = current_time - 60
            recent_calls = [t for t in self._call_history['api_calls'] if t > minute_ago]
            stats['api_calls_last_minute'] = len(recent_calls)
            stats['rate_limit'] = self.max_calls_per_minute
        
        return stats


# Global instance for easy access
_live_counts_manager = None

def get_live_counts_manager() -> LiveCountsManager:
    """Get or create the global live counts manager."""
    global _live_counts_manager
    if _live_counts_manager is None:
        _live_counts_manager = LiveCountsManager()
    return _live_counts_manager


def get_cached_counts(internship_ids: List[str], ttl_seconds: int = 300) -> Dict[str, Dict[str, Any]]:
    """
    Get cached live application counts.
    
    Args:
        internship_ids: List of internship IDs
        ttl_seconds: Cache TTL in seconds
        
    Returns:
        Dict mapping internship_id to count data
    """
    manager = get_live_counts_manager()
    return manager.get_cached_counts(internship_ids, ttl_seconds)


def fetch_live_counts(internship_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetch live application counts (bypassing cache).
    
    Args:
        internship_ids: List of internship IDs
        
    Returns:
        Dict mapping internship_id to count data
    """
    manager = get_live_counts_manager()
    return manager.fetch_live_counts(internship_ids)


if __name__ == "__main__":
    # Demo the live counts manager
    print("🚀 PMIS Live Counts Manager Demo")
    print("=" * 50)
    
    manager = LiveCountsManager()
    
    # Test with sample internship IDs
    test_ids = ['INT_0001', 'INT_0002', 'INT_0003', 'INT_0004']
    
    print(f"🔄 Fetching live counts for: {test_ids}")
    
    # First fetch (should use fetcher)
    start_time = time.time()
    counts1 = manager.get_cached_counts(test_ids)
    fetch_time = time.time() - start_time
    
    print(f"✅ First fetch completed in {fetch_time:.3f}s")
    print(f"📊 Results: {len(counts1)} internships")
    
    for internship_id, data in counts1.items():
        print(f"   {internship_id}: {data['current_applicants']} applicants (freshness: {data['freshness_seconds']}s)")
    
    # Second fetch (should use cache)
    print(f"\n🔄 Second fetch (should use cache)...")
    start_time = time.time()
    counts2 = manager.get_cached_counts(test_ids)
    cache_time = time.time() - start_time
    
    print(f"✅ Second fetch completed in {cache_time:.3f}s ({cache_time/fetch_time:.1f}x faster)")
    
    # Show cache stats
    stats = manager.get_cache_stats()
    print(f"\n📈 Cache Statistics:")
    print(f"   Total Entries: {stats['total_entries']}")
    print(f"   Fresh Entries: {stats['fresh_entries']}")
    print(f"   Cache Hit Rate: {stats['cache_hit_rate']:.1%}")
    print(f"   API Calls (last minute): {stats['api_calls_last_minute']}")
    print(f"   Rate Limit: {stats['rate_limit']}/min")
    
    print(f"\n🎯 Demo completed successfully!")
