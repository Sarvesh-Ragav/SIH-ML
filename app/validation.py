"""
PMIS Data Validation Module
==========================

This module provides automated data validation jobs with comprehensive
checks and HTML reporting for data quality monitoring.

Key Features:
- Automated validation of all data sources
- Comprehensive checks for data integrity and business rules
- HTML report generation with visual indicators
- JSON API for programmatic access
- Detailed issue tracking and categorization

Author: Senior ML + Platform Engineer
Date: September 21, 2025
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
import logging
import warnings
import json
from pathlib import Path

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Comprehensive data validator for PMIS.
    
    Performs automated checks on all data sources and generates
    detailed reports with actionable insights.
    """
    
    def __init__(self, data_dir: str = "data/"):
        """
        Initialize the data validator.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.validation_results = {}
        
        logger.info("🔧 Data Validator initialized")
    
    def run_validations(self) -> Dict[str, Any]:
        """
        Run all validation checks.
        
        Returns:
            Dict with validation summary and detailed results
        """
        logger.info("🔄 Running comprehensive data validations...")
        
        start_time = datetime.now()
        
        # Initialize results structure
        self.validation_results = {
            'timestamp': start_time.isoformat(),
            'summary': {
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 0,
                'warnings': 0,
                'critical_issues': 0
            },
            'files_checked': [],
            'issues': {
                'critical': [],
                'warning': [],
                'info': []
            },
            'detailed_results': {}
        }
        
        # Run validation checks
        self._validate_internships()
        self._validate_students()
        self._validate_interactions()
        self._validate_outcomes()
        self._validate_application_stats()
        self._validate_company_metadata()
        self._validate_course_data()
        self._validate_interview_metadata()
        self._validate_alumni_data()
        
        # Calculate summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.validation_results['duration_seconds'] = duration
        self.validation_results['summary']['total_checks'] = (
            self.validation_results['summary']['passed_checks'] + 
            self.validation_results['summary']['failed_checks']
        )
        
        logger.info(f"✅ Validation completed in {duration:.2f}s")
        logger.info(f"📊 Results: {self.validation_results['summary']['passed_checks']}/{self.validation_results['summary']['total_checks']} checks passed")
        
        return self.validation_results
    
    def _validate_internships(self):
        """Validate internship data."""
        logger.info("🔍 Validating internship data...")
        
        file_results = {'checks': [], 'issues': []}
        
        # Check enhanced internships
        enhanced_file = os.path.join(self.data_dir, "internships_enhanced.csv")
        if os.path.exists(enhanced_file):
            df = pd.read_csv(enhanced_file)
            self.validation_results['files_checked'].append('internships_enhanced.csv')
            
            # Check application deadlines
            if 'application_deadline' in df.columns:
                df['application_deadline'] = pd.to_datetime(df['application_deadline'], errors='coerce')
                today = datetime.now().date()
                
                expired_count = sum(df['application_deadline'].dt.date < today)
                if expired_count > 0:
                    issue = {
                        'type': 'warning',
                        'category': 'deadlines',
                        'message': f'{expired_count} internships have expired deadlines',
                        'count': expired_count,
                        'file': 'internships_enhanced.csv'
                    }
                    self.validation_results['issues']['warning'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['warnings'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('application_deadline_validity')
            
            # Check status coherence
            if 'is_accepting_applications' in df.columns and 'application_deadline' in df.columns:
                incoherent = df[
                    (df['is_accepting_applications'] == True) & 
                    (df['application_deadline'].dt.date < today)
                ]
                
                if len(incoherent) > 0:
                    issue = {
                        'type': 'critical',
                        'category': 'status_coherence',
                        'message': f'{len(incoherent)} internships accepting applications past deadline',
                        'count': len(incoherent),
                        'file': 'internships_enhanced.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('status_coherence')
            
            # Check employee count
            if 'employee_count' in df.columns:
                invalid_counts = df[
                    (df['employee_count'].notna()) & 
                    (df['employee_count'] < 0)
                ]
                
                if len(invalid_counts) > 0:
                    issue = {
                        'type': 'critical',
                        'category': 'employee_count',
                        'message': f'{len(invalid_counts)} companies have negative employee counts',
                        'count': len(invalid_counts),
                        'file': 'internships_enhanced.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('employee_count_validity')
        
        else:
            issue = {
                'type': 'warning',
                'category': 'missing_file',
                'message': 'internships_enhanced.csv not found',
                'file': 'internships_enhanced.csv'
            }
            self.validation_results['issues']['warning'].append(issue)
            file_results['issues'].append(issue)
            self.validation_results['summary']['warnings'] += 1
        
        self.validation_results['detailed_results']['internships'] = file_results
    
    def _validate_students(self):
        """Validate student data."""
        logger.info("🔍 Validating student data...")
        
        file_results = {'checks': [], 'issues': []}
        
        student_file = os.path.join(self.data_dir, "student.csv")
        if os.path.exists(student_file):
            df = pd.read_csv(student_file)
            self.validation_results['files_checked'].append('student.csv')
            
            # Check CGPA ranges
            if 'cgpa' in df.columns:
                invalid_cgpa = df[
                    (df['cgpa'].notna()) & 
                    ((df['cgpa'] < 0) | (df['cgpa'] > 10))
                ]
                
                if len(invalid_cgpa) > 0:
                    issue = {
                        'type': 'critical',
                        'category': 'cgpa_range',
                        'message': f'{len(invalid_cgpa)} students have invalid CGPA (not in 0-10 range)',
                        'count': len(invalid_cgpa),
                        'file': 'student.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('cgpa_range_validity')
            
            # Check for duplicate student IDs
            if 'student_id' in df.columns:
                duplicates = df['student_id'].duplicated().sum()
                
                if duplicates > 0:
                    issue = {
                        'type': 'critical',
                        'category': 'duplicate_ids',
                        'message': f'{duplicates} duplicate student IDs found',
                        'count': duplicates,
                        'file': 'student.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('student_id_uniqueness')
        
        else:
            issue = {
                'type': 'critical',
                'category': 'missing_file',
                'message': 'student.csv not found - core data missing',
                'file': 'student.csv'
            }
            self.validation_results['issues']['critical'].append(issue)
            file_results['issues'].append(issue)
            self.validation_results['summary']['critical_issues'] += 1
        
        self.validation_results['detailed_results']['students'] = file_results
    
    def _validate_interactions(self):
        """Validate interaction data."""
        logger.info("🔍 Validating interaction data...")
        
        file_results = {'checks': [], 'issues': []}
        
        interactions_file = os.path.join(self.data_dir, "interactions.csv")
        if os.path.exists(interactions_file):
            df = pd.read_csv(interactions_file)
            self.validation_results['files_checked'].append('interactions.csv')
            
            # Check rating ranges
            if 'rating' in df.columns:
                invalid_ratings = df[
                    (df['rating'].notna()) & 
                    ((df['rating'] < 1) | (df['rating'] > 5))
                ]
                
                if len(invalid_ratings) > 0:
                    issue = {
                        'type': 'warning',
                        'category': 'rating_range',
                        'message': f'{len(invalid_ratings)} interactions have invalid ratings (not in 1-5 range)',
                        'count': len(invalid_ratings),
                        'file': 'interactions.csv'
                    }
                    self.validation_results['issues']['warning'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['warnings'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('rating_range_validity')
            
            # Check timestamp format
            if 'timestamp' in df.columns:
                try:
                    pd.to_datetime(df['timestamp'], errors='raise')
                    self.validation_results['summary']['passed_checks'] += 1
                except:
                    issue = {
                        'type': 'critical',
                        'category': 'timestamp_format',
                        'message': 'Invalid timestamp format in interactions',
                        'file': 'interactions.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                
                file_results['checks'].append('timestamp_format_validity')
        
        else:
            issue = {
                'type': 'critical',
                'category': 'missing_file',
                'message': 'interactions.csv not found - core data missing',
                'file': 'interactions.csv'
            }
            self.validation_results['issues']['critical'].append(issue)
            file_results['issues'].append(issue)
            self.validation_results['summary']['critical_issues'] += 1
        
        self.validation_results['detailed_results']['interactions'] = file_results
    
    def _validate_outcomes(self):
        """Validate outcome data."""
        logger.info("🔍 Validating outcome data...")
        
        file_results = {'checks': [], 'issues': []}
        
        outcomes_file = os.path.join(self.data_dir, "outcomes.csv")
        if os.path.exists(outcomes_file):
            df = pd.read_csv(outcomes_file)
            self.validation_results['files_checked'].append('outcomes.csv')
            
            # Check success probability ranges
            if 'success_prob' in df.columns:
                invalid_probs = df[
                    (df['success_prob'].notna()) & 
                    ((df['success_prob'] < 0) | (df['success_prob'] > 1))
                ]
                
                if len(invalid_probs) > 0:
                    issue = {
                        'type': 'critical',
                        'category': 'probability_range',
                        'message': f'{len(invalid_probs)} outcomes have invalid success probabilities (not in 0-1 range)',
                        'count': len(invalid_probs),
                        'file': 'outcomes.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('success_prob_range_validity')
        
        else:
            issue = {
                'type': 'warning',
                'category': 'missing_file',
                'message': 'outcomes.csv not found - historical data unavailable',
                'file': 'outcomes.csv'
            }
            self.validation_results['issues']['warning'].append(issue)
            file_results['issues'].append(issue)
            self.validation_results['summary']['warnings'] += 1
        
        self.validation_results['detailed_results']['outcomes'] = file_results
    
    def _validate_application_stats(self):
        """Validate application statistics."""
        logger.info("🔍 Validating application statistics...")
        
        file_results = {'checks': [], 'issues': []}
        
        stats_file = os.path.join(self.data_dir, "application_statistics.csv")
        if os.path.exists(stats_file):
            df = pd.read_csv(stats_file)
            self.validation_results['files_checked'].append('application_statistics.csv')
            
            # Check positions_available >= 0
            if 'positions_available' in df.columns:
                invalid_positions = df[
                    (df['positions_available'].notna()) & 
                    (df['positions_available'] < 0)
                ]
                
                if len(invalid_positions) > 0:
                    issue = {
                        'type': 'critical',
                        'category': 'positions_available',
                        'message': f'{len(invalid_positions)} internships have negative positions_available',
                        'count': len(invalid_positions),
                        'file': 'application_statistics.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('positions_available_validity')
            
            # Check selection_ratio in [0,1]
            if 'selection_ratio' in df.columns:
                invalid_ratios = df[
                    (df['selection_ratio'].notna()) & 
                    ((df['selection_ratio'] < 0) | (df['selection_ratio'] > 1))
                ]
                
                if len(invalid_ratios) > 0:
                    issue = {
                        'type': 'critical',
                        'category': 'selection_ratio',
                        'message': f'{len(invalid_ratios)} internships have invalid selection ratios (not in 0-1 range)',
                        'count': len(invalid_ratios),
                        'file': 'application_statistics.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('selection_ratio_validity')
        
        else:
            issue = {
                'type': 'warning',
                'category': 'missing_file',
                'message': 'application_statistics.csv not found - historical stats unavailable',
                'file': 'application_statistics.csv'
            }
            self.validation_results['issues']['warning'].append(issue)
            file_results['issues'].append(issue)
            self.validation_results['summary']['warnings'] += 1
        
        self.validation_results['detailed_results']['application_stats'] = file_results
    
    def _validate_company_metadata(self):
        """Validate company metadata."""
        logger.info("🔍 Validating company metadata...")
        
        file_results = {'checks': [], 'issues': []}
        
        company_file = os.path.join(self.data_dir, "company_metadata.csv")
        if os.path.exists(company_file):
            df = pd.read_csv(company_file)
            self.validation_results['files_checked'].append('company_metadata.csv')
            
            # Check employee_count >= 0 or None
            if 'employee_count' in df.columns:
                invalid_counts = df[
                    (df['employee_count'].notna()) & 
                    (df['employee_count'] < 0)
                ]
                
                if len(invalid_counts) > 0:
                    issue = {
                        'type': 'critical',
                        'category': 'employee_count',
                        'message': f'{len(invalid_counts)} companies have negative employee counts',
                        'count': len(invalid_counts),
                        'file': 'company_metadata.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('employee_count_validity')
        
        else:
            issue = {
                'type': 'warning',
                'category': 'missing_file',
                'message': 'company_metadata.csv not found - company info unavailable',
                'file': 'company_metadata.csv'
            }
            self.validation_results['issues']['warning'].append(issue)
            file_results['issues'].append(issue)
            self.validation_results['summary']['warnings'] += 1
        
        self.validation_results['detailed_results']['company_metadata'] = file_results
    
    def _validate_course_data(self):
        """Validate course data."""
        logger.info("🔍 Validating course data...")
        
        file_results = {'checks': [], 'issues': []}
        
        course_file = os.path.join(self.data_dir, "internship_skills_courses_migrated.csv")
        if os.path.exists(course_file):
            df = pd.read_csv(course_file)
            self.validation_results['files_checked'].append('internship_skills_courses_migrated.csv')
            
            # Check duration_hours >= 0
            if 'duration_hours' in df.columns:
                invalid_durations = df[
                    (df['duration_hours'].notna()) & 
                    (df['duration_hours'] < 0)
                ]
                
                if len(invalid_durations) > 0:
                    issue = {
                        'type': 'critical',
                        'category': 'duration_hours',
                        'message': f'{len(invalid_durations)} courses have negative duration hours',
                        'count': len(invalid_durations),
                        'file': 'internship_skills_courses_migrated.csv'
                    }
                    self.validation_results['issues']['critical'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['critical_issues'] += 1
                    self.validation_results['summary']['failed_checks'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('duration_hours_validity')
            
            # Check expected_success_boost in [0, 0.2]
            if 'expected_success_boost' in df.columns:
                invalid_boosts = df[
                    (df['expected_success_boost'].notna()) & 
                    ((df['expected_success_boost'] < 0) | (df['expected_success_boost'] > 0.2))
                ]
                
                if len(invalid_boosts) > 0:
                    issue = {
                        'type': 'warning',
                        'category': 'success_boost_range',
                        'message': f'{len(invalid_boosts)} courses have invalid success boost values (not in 0-0.2 range)',
                        'count': len(invalid_boosts),
                        'file': 'internship_skills_courses_migrated.csv'
                    }
                    self.validation_results['issues']['warning'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['warnings'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('success_boost_range_validity')
        
        else:
            issue = {
                'type': 'warning',
                'category': 'missing_file',
                'message': 'internship_skills_courses_migrated.csv not found - enhanced course data unavailable',
                'file': 'internship_skills_courses_migrated.csv'
            }
            self.validation_results['issues']['warning'].append(issue)
            file_results['issues'].append(issue)
            self.validation_results['summary']['warnings'] += 1
        
        self.validation_results['detailed_results']['course_data'] = file_results
    
    def _validate_interview_metadata(self):
        """Validate interview metadata."""
        logger.info("🔍 Validating interview metadata...")
        
        file_results = {'checks': [], 'issues': []}
        
        interview_file = os.path.join(self.data_dir, "interview_process.csv")
        if os.path.exists(interview_file):
            df = pd.read_csv(interview_file)
            self.validation_results['files_checked'].append('interview_process.csv')
            
            # Check rounds in [0, 10]
            if 'rounds' in df.columns:
                invalid_rounds = df[
                    (df['rounds'].notna()) & 
                    ((df['rounds'] < 0) | (df['rounds'] > 10))
                ]
                
                if len(invalid_rounds) > 0:
                    issue = {
                        'type': 'warning',
                        'category': 'rounds_range',
                        'message': f'{len(invalid_rounds)} interview processes have invalid round counts (not in 0-10 range)',
                        'count': len(invalid_rounds),
                        'file': 'interview_process.csv'
                    }
                    self.validation_results['issues']['warning'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['warnings'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('rounds_range_validity')
            
            # Check expected_timeline_days in [0, 90]
            if 'expected_timeline_days' in df.columns:
                invalid_timelines = df[
                    (df['expected_timeline_days'].notna()) & 
                    ((df['expected_timeline_days'] < 0) | (df['expected_timeline_days'] > 90))
                ]
                
                if len(invalid_timelines) > 0:
                    issue = {
                        'type': 'warning',
                        'category': 'timeline_range',
                        'message': f'{len(invalid_timelines)} interview processes have invalid timelines (not in 0-90 days range)',
                        'count': len(invalid_timelines),
                        'file': 'interview_process.csv'
                    }
                    self.validation_results['issues']['warning'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['warnings'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('timeline_range_validity')
        
        else:
            issue = {
                'type': 'info',
                'category': 'missing_file',
                'message': 'interview_process.csv not found - interview metadata unavailable',
                'file': 'interview_process.csv'
            }
            self.validation_results['issues']['info'].append(issue)
            file_results['issues'].append(issue)
        
        self.validation_results['detailed_results']['interview_metadata'] = file_results
    
    def _validate_alumni_data(self):
        """Validate alumni data."""
        logger.info("🔍 Validating alumni data...")
        
        file_results = {'checks': [], 'issues': []}
        
        alumni_file = os.path.join(self.data_dir, "alumni_success.csv")
        if os.path.exists(alumni_file):
            df = pd.read_csv(alumni_file)
            self.validation_results['files_checked'].append('alumni_success.csv')
            
            # Check year range
            if 'year' in df.columns:
                invalid_years = df[
                    (df['year'].notna()) & 
                    ((df['year'] < 2020) | (df['year'] > 2025))
                ]
                
                if len(invalid_years) > 0:
                    issue = {
                        'type': 'warning',
                        'category': 'year_range',
                        'message': f'{len(invalid_years)} alumni records have invalid years (not in 2020-2025 range)',
                        'count': len(invalid_years),
                        'file': 'alumni_success.csv'
                    }
                    self.validation_results['issues']['warning'].append(issue)
                    file_results['issues'].append(issue)
                    self.validation_results['summary']['warnings'] += 1
                else:
                    self.validation_results['summary']['passed_checks'] += 1
                
                file_results['checks'].append('year_range_validity')
        
        else:
            issue = {
                'type': 'info',
                'category': 'missing_file',
                'message': 'alumni_success.csv not found - alumni stories unavailable',
                'file': 'alumni_success.csv'
            }
            self.validation_results['issues']['info'].append(issue)
            file_results['issues'].append(issue)
        
        self.validation_results['detailed_results']['alumni_data'] = file_results
    
    def render_validation_report(self, summary: Dict[str, Any], out_path: str = "./reports/validation.html") -> str:
        """
        Render validation report as HTML.
        
        Args:
            summary: Validation summary dict
            out_path: Output path for HTML report
            
        Returns:
            Path to generated HTML report
        """
        logger.info(f"🔄 Rendering validation report to {out_path}")
        
        # Ensure reports directory exists
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        # Generate HTML content
        html_content = self._generate_html_report(summary)
        
        # Write to file
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ Validation report saved to {out_path}")
        return out_path
    
    def _generate_html_report(self, summary: Dict[str, Any]) -> str:
        """Generate HTML report content."""
        
        timestamp = summary.get('timestamp', datetime.now().isoformat())
        duration = summary.get('duration_seconds', 0)
        
        # Status color based on issues
        if summary['summary']['critical_issues'] > 0:
            status_color = '#dc3545'  # Red
            status_text = 'CRITICAL ISSUES FOUND'
        elif summary['summary']['warnings'] > 0:
            status_color = '#ffc107'  # Yellow
            status_text = 'WARNINGS FOUND'
        else:
            status_color = '#28a745'  # Green
            status_text = 'ALL CHECKS PASSED'
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PMIS Data Validation Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .header .subtitle {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .status-banner {{
            background-color: {status_color};
            color: white;
            text-align: center;
            padding: 15px;
            font-weight: bold;
            font-size: 1.2em;
        }}
        .content {{
            padding: 30px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .summary-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .issues-section {{
            margin-top: 30px;
        }}
        .issues-section h2 {{
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            color: #333;
        }}
        .issue-group {{
            margin-bottom: 25px;
        }}
        .issue-group h3 {{
            color: #666;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        .issue-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 10px;
        }}
        .critical {{ background-color: #dc3545; color: white; }}
        .warning {{ background-color: #ffc107; color: #333; }}
        .info {{ background-color: #17a2b8; color: white; }}
        .issue-item {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #dee2e6;
        }}
        .issue-item.critical {{ border-left-color: #dc3545; }}
        .issue-item.warning {{ border-left-color: #ffc107; }}
        .issue-item.info {{ border-left-color: #17a2b8; }}
        .issue-message {{
            font-weight: 500;
            margin-bottom: 5px;
        }}
        .issue-details {{
            font-size: 0.9em;
            color: #666;
        }}
        .files-checked {{
            margin-top: 30px;
            background: #e8f5e8;
            border-radius: 6px;
            padding: 20px;
        }}
        .files-checked h3 {{
            color: #155724;
            margin-top: 0;
        }}
        .file-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .file-tag {{
            background: #d4edda;
            color: #155724;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.9em;
            border: 1px solid #c3e6cb;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #dee2e6;
        }}
        .no-issues {{
            text-align: center;
            padding: 40px;
            color: #28a745;
            font-size: 1.2em;
        }}
        .no-issues .icon {{
            font-size: 3em;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ PMIS Data Validation Report</h1>
            <div class="subtitle">Automated Data Quality Assessment</div>
        </div>
        
        <div class="status-banner">
            {status_text}
        </div>
        
        <div class="content">
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Total Checks</h3>
                    <div class="number">{summary['summary']['total_checks']}</div>
                </div>
                <div class="summary-card">
                    <h3>Passed</h3>
                    <div class="number" style="color: #28a745;">{summary['summary']['passed_checks']}</div>
                </div>
                <div class="summary-card">
                    <h3>Failed</h3>
                    <div class="number" style="color: #dc3545;">{summary['summary']['failed_checks']}</div>
                </div>
                <div class="summary-card">
                    <h3>Warnings</h3>
                    <div class="number" style="color: #ffc107;">{summary['summary']['warnings']}</div>
                </div>
                <div class="summary-card">
                    <h3>Critical Issues</h3>
                    <div class="number" style="color: #dc3545;">{summary['summary']['critical_issues']}</div>
                </div>
                <div class="summary-card">
                    <h3>Duration</h3>
                    <div class="number">{duration:.2f}s</div>
                </div>
            </div>
"""
        
        # Add issues sections
        if (summary['issues']['critical'] or summary['issues']['warning'] or summary['issues']['info']):
            html += '<div class="issues-section"><h2>🚨 Issues Found</h2>'
            
            # Critical issues
            if summary['issues']['critical']:
                html += '''
                <div class="issue-group">
                    <h3><span class="issue-badge critical">CRITICAL</span>Critical Issues Requiring Immediate Attention</h3>
                '''
                for issue in summary['issues']['critical']:
                    html += f'''
                    <div class="issue-item critical">
                        <div class="issue-message">{issue['message']}</div>
                        <div class="issue-details">
                            File: {issue['file']} | Category: {issue['category']}
                            {f" | Count: {issue['count']}" if 'count' in issue else ""}
                        </div>
                    </div>
                    '''
                html += '</div>'
            
            # Warning issues
            if summary['issues']['warning']:
                html += '''
                <div class="issue-group">
                    <h3><span class="issue-badge warning">WARNING</span>Warnings - Should Be Addressed</h3>
                '''
                for issue in summary['issues']['warning']:
                    html += f'''
                    <div class="issue-item warning">
                        <div class="issue-message">{issue['message']}</div>
                        <div class="issue-details">
                            File: {issue['file']} | Category: {issue['category']}
                            {f" | Count: {issue['count']}" if 'count' in issue else ""}
                        </div>
                    </div>
                    '''
                html += '</div>'
            
            # Info issues
            if summary['issues']['info']:
                html += '''
                <div class="issue-group">
                    <h3><span class="issue-badge info">INFO</span>Informational - Optional Features</h3>
                '''
                for issue in summary['issues']['info']:
                    html += f'''
                    <div class="issue-item info">
                        <div class="issue-message">{issue['message']}</div>
                        <div class="issue-details">
                            File: {issue['file']} | Category: {issue['category']}
                            {f" | Count: {issue['count']}" if 'count' in issue else ""}
                        </div>
                    </div>
                    '''
                html += '</div>'
            
            html += '</div>'
        else:
            html += '''
            <div class="no-issues">
                <div class="icon">✅</div>
                <div>All validation checks passed successfully!</div>
                <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                    Your data is in excellent condition.
                </div>
            </div>
            '''
        
        # Files checked section
        if summary.get('files_checked'):
            html += f'''
            <div class="files-checked">
                <h3>📁 Files Validated ({len(summary['files_checked'])})</h3>
                <div class="file-list">
            '''
            for file in summary['files_checked']:
                html += f'<span class="file-tag">{file}</span>'
            html += '</div></div>'
        
        html += f'''
        </div>
        
        <div class="footer">
            Generated on {timestamp[:19].replace('T', ' ')} | 
            PMIS Data Validation System v1.0 | 
            <strong>{len(summary.get('files_checked', []))} files validated</strong>
        </div>
    </div>
</body>
</html>
        '''
        
        return html


def run_validations() -> Dict[str, Any]:
    """
    Run all data validation checks.
    
    Returns:
        Dict with validation summary and detailed results
    """
    validator = DataValidator()
    return validator.run_validations()


def render_validation_report(summary: Dict[str, Any], out_path: str = "./reports/validation.html") -> str:
    """
    Render validation report as HTML.
    
    Args:
        summary: Validation summary dict
        out_path: Output path for HTML report
        
    Returns:
        Path to generated HTML report
    """
    validator = DataValidator()
    return validator.render_validation_report(summary, out_path)


if __name__ == "__main__":
    # Demo the data validator
    print("🚀 PMIS Data Validator Demo")
    print("=" * 50)
    
    # Run validations
    results = run_validations()
    
    # Print summary
    print(f"✅ Validation completed in {results['duration_seconds']:.2f} seconds")
    print(f"📊 Summary: {results['summary']['passed_checks']}/{results['summary']['total_checks']} checks passed")
    print(f"⚠️  Warnings: {results['summary']['warnings']}")
    print(f"🚨 Critical Issues: {results['summary']['critical_issues']}")
    print(f"📁 Files Checked: {len(results['files_checked'])}")
    
    # Generate HTML report
    report_path = render_validation_report(results)
    print(f"\n📄 HTML report generated: {report_path}")
    
    # Show some sample issues
    if results['issues']['critical']:
        print(f"\n🚨 Critical Issues:")
        for issue in results['issues']['critical'][:3]:
            print(f"   • {issue['message']}")
    
    if results['issues']['warning']:
        print(f"\n⚠️  Warnings:")
        for issue in results['issues']['warning'][:3]:
            print(f"   • {issue['message']}")
    
    print(f"\n🎯 Demo completed successfully!")
