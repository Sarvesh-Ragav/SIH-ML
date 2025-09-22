"""
Production Data Generator for PMIS ML System
============================================

Generates 5000+ entries across all required datasets for production-ready ML system.
Creates realistic, diverse data with proper relationships and distributions.

Author: ML Engineer
Date: December 2024
"""

import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import json
import os

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker('en_IN')  # Indian locale for realistic data

class ProductionDataGenerator:
    """Generate production-ready datasets for PMIS ML system."""
    
    def __init__(self):
        self.skills_list = [
            'python', 'java', 'javascript', 'react', 'nodejs', 'angular', 'vue',
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis',
            'machine learning', 'deep learning', 'data science', 'statistics',
            'web development', 'mobile development', 'ios', 'android', 'flutter',
            'devops', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'cybersecurity', 'ethical hacking', 'penetration testing',
            'ui/ux design', 'figma', 'adobe xd', 'sketch',
            'project management', 'agile', 'scrum', 'jira',
            'digital marketing', 'seo', 'content writing', 'social media',
            'finance', 'accounting', 'investment banking', 'trading',
            'business analysis', 'consulting', 'strategy', 'operations'
        ]
        
        self.streams = [
            'Computer Science', 'Information Technology', 'Data Science', 
            'Artificial Intelligence', 'Software Engineering', 'Computer Engineering',
            'Electronics and Communication', 'Mechanical Engineering', 'Civil Engineering',
            'Business Administration', 'Finance', 'Marketing', 'Human Resources',
            'Design', 'Graphic Design', 'Product Design', 'Architecture',
            'Psychology', 'Sociology', 'Economics', 'Statistics'
        ]
        
        self.college_tiers = ['Tier-1', 'Tier-2', 'Tier-3']
        
        self.tier1_colleges = [
            'IIT Bombay', 'IIT Delhi', 'IIT Madras', 'IIT Kanpur', 'IIT Kharagpur',
            'IIT Roorkee', 'IIT Guwahati', 'IIT Hyderabad', 'IIT Indore', 'IIT Bhubaneswar',
            'BITS Pilani', 'IIIT Hyderabad', 'IIIT Bangalore', 'NIT Trichy', 'NIT Surathkal'
        ]
        
        self.tier2_colleges = [
            'COEP Pune', 'VJTI Mumbai', 'PICT Pune', 'SPIT Mumbai', 'DJ Sanghvi Mumbai',
            'Thapar University', 'Manipal Institute of Technology', 'SRM University',
            'VIT University', 'Amity University', 'Symbiosis International University',
            'Christ University', 'Jain University', 'RV College of Engineering'
        ]
        
        self.tier3_colleges = [
            'Local Engineering College', 'Regional University', 'State Engineering College',
            'Private Engineering College', 'Community College', 'Technical Institute'
        ]
        
        self.locations = [
            'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Pune', 'Hyderabad', 
            'Kolkata', 'Ahmedabad', 'Jaipur', 'Surat', 'Lucknow', 'Kanpur',
            'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Pimpri-Chinchwad',
            'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik'
        ]
        
        self.domains = [
            'Software Development', 'Data Science', 'Artificial Intelligence', 
            'Machine Learning', 'Web Development', 'Mobile Development', 
            'DevOps', 'Cloud Computing', 'Cybersecurity', 'UI/UX Design',
            'Product Management', 'Digital Marketing', 'Business Analysis',
            'Finance', 'Consulting', 'Operations', 'Human Resources',
            'Content Writing', 'Graphic Design', 'Quality Assurance'
        ]
        
        self.companies = [
            # Tech Giants
            'Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix', 'Uber', 'Airbnb',
            'Spotify', 'Twitter', 'LinkedIn', 'Salesforce', 'Adobe', 'Oracle', 'IBM',
            
            # Indian Tech Companies
            'TCS', 'Infosys', 'Wipro', 'HCL Technologies', 'Tech Mahindra', 'Cognizant',
            'Accenture', 'Capgemini', 'LTI', 'Mindtree', 'Mphasis', 'Hexaware',
            
            # Startups & Unicorns
            'Flipkart', 'Ola', 'Swiggy', 'Zomato', 'Paytm', 'PhonePe', 'Razorpay',
            'Byju\'s', 'Unacademy', 'Cure.fit', 'Urban Company', 'PolicyBazaar',
            'Nykaa', 'Meesho', 'CRED', 'Groww', 'UpGrad', 'Simplilearn',
            
            # Finance & Banking
            'HDFC Bank', 'ICICI Bank', 'SBI', 'Axis Bank', 'Kotak Mahindra Bank',
            'Goldman Sachs', 'JP Morgan', 'Morgan Stanley', 'Deutsche Bank',
            
            # Consulting
            'McKinsey', 'BCG', 'Bain', 'Deloitte', 'PwC', 'EY', 'KPMG',
            
            # E-commerce & Retail
            'Amazon India', 'Myntra', 'Jabong', 'Snapdeal', 'ShopClues',
            
            # Media & Entertainment
            'Hotstar', 'Sony', 'Zee', 'Viacom18', 'Times Group', 'Network18'
        ]
        
        self.industries = [
            'Technology', 'Finance', 'Healthcare', 'E-commerce', 'Education',
            'Media & Entertainment', 'Consulting', 'Manufacturing', 'Retail',
            'Telecommunications', 'Automotive', 'Real Estate', 'Travel & Tourism',
            'Food & Beverage', 'Fashion', 'Gaming', 'Sports', 'Non-profit'
        ]
    
    def generate_students(self, n_students=5000):
        """Generate student dataset with realistic profiles."""
        print(f"🎓 Generating {n_students} student profiles...")
        
        students = []
        for i in range(n_students):
            # Determine college tier and corresponding college
            tier = np.random.choice(self.college_tiers, p=[0.15, 0.35, 0.50])  # Realistic distribution
            
            if tier == 'Tier-1':
                college = np.random.choice(self.tier1_colleges)
                cgpa_mean, cgpa_std = 8.5, 0.8
            elif tier == 'Tier-2':
                college = np.random.choice(self.tier2_colleges)
                cgpa_mean, cgpa_std = 7.8, 0.9
            else:
                college = np.random.choice(self.tier3_colleges)
                cgpa_mean, cgpa_std = 7.2, 1.0
            
            # Generate skills based on stream
            stream = np.random.choice(self.streams)
            if 'Computer' in stream or 'Engineering' in stream:
                skill_pool = [s for s in self.skills_list if s in ['python', 'java', 'javascript', 'react', 'nodejs', 'sql', 'machine learning', 'web development', 'mobile development', 'devops', 'aws', 'cybersecurity']]
            elif 'Business' in stream or 'Finance' in stream:
                skill_pool = [s for s in self.skills_list if s in ['project management', 'business analysis', 'finance', 'accounting', 'digital marketing', 'consulting']]
            elif 'Design' in stream:
                skill_pool = [s for s in self.skills_list if s in ['ui/ux design', 'figma', 'adobe xd', 'graphic design', 'web development']]
            else:
                skill_pool = self.skills_list
            
            num_skills = min(np.random.randint(3, 8), len(skill_pool))
            skills = np.random.choice(skill_pool, size=num_skills, replace=False)
            
            # Generate interests (subset of skills + additional)
            num_interests = min(np.random.randint(2, 5), len(skill_pool))
            interests = np.random.choice(skill_pool, size=num_interests, replace=False)
            
            # Generate experience
            experience_options = ['No experience', '1 project', '2-3 projects', '1 internship', '2+ internships', '1 internship + projects']
            experience = np.random.choice(experience_options, p=[0.20, 0.25, 0.20, 0.15, 0.15, 0.05])
            
            student = {
                'student_id': f'STU_{i+1:05d}',
                'skills': ','.join(skills),
                'cgpa': round(np.random.normal(cgpa_mean, cgpa_std), 2),
                'stream': stream,
                'college_tier': tier,
                'rural_urban': np.random.choice(['rural', 'urban'], p=[0.35, 0.65]),
                'location': np.random.choice(self.locations),
                'gender': np.random.choice(['Male', 'Female', 'Other'], p=[0.60, 0.38, 0.02]),
                'university': college,
                'graduation_year': np.random.choice([2024, 2025, 2026], p=[0.30, 0.50, 0.20]),
                'interests': ','.join(interests),
                'previous_experience': experience,
                'linkedin_url': f'https://linkedin.com/in/student{i+1}',
                'github_url': f'https://github.com/student{i+1}',
                'portfolio_url': f'https://portfolio.com/student{i+1}',
                'phone': fake.phone_number(),
                'email': f'student{i+1}@email.com',
                'created_at': fake.date_time_between(start_date='-2y', end_date='now')
            }
            
            # Ensure CGPA is within valid range
            student['cgpa'] = max(6.0, min(10.0, student['cgpa']))
            
            students.append(student)
        
        df = pd.DataFrame(students)
        print(f"✅ Generated {len(df)} student profiles")
        return df
    
    def generate_internships(self, n_internships=1000):
        """Generate internship dataset with realistic opportunities."""
        print(f"💼 Generating {n_internships} internship opportunities...")
        
        internships = []
        for i in range(n_internships):
            # Select company and determine characteristics
            company = np.random.choice(self.companies)
            
            # Determine company size and stipend based on company type
            if company in ['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix']:
                company_size = 'large'
                stipend_base = 60000
                stipend_std = 15000
            elif company in ['TCS', 'Infosys', 'Wipro', 'HCL Technologies', 'Tech Mahindra']:
                company_size = 'large'
                stipend_base = 35000
                stipend_std = 10000
            elif company in ['Flipkart', 'Ola', 'Swiggy', 'Zomato', 'Paytm']:
                company_size = 'mid'
                stipend_base = 45000
                stipend_std = 12000
            else:
                company_size = np.random.choice(['startup', 'mid', 'large'], p=[0.40, 0.35, 0.25])
                stipend_base = np.random.choice([25000, 35000, 50000], p=[0.30, 0.50, 0.20])
                stipend_std = stipend_base * 0.3
            
            # Generate domain and related skills
            domain = np.random.choice(self.domains)
            
            if domain in ['Software Development', 'Web Development', 'Mobile Development']:
                required_skills = np.random.choice(['python', 'java', 'javascript', 'react', 'nodejs', 'sql'], size=np.random.randint(2, 4), replace=False)
            elif domain in ['Data Science', 'Machine Learning', 'Artificial Intelligence']:
                required_skills = np.random.choice(['python', 'machine learning', 'data science', 'sql', 'statistics', 'r'], size=np.random.randint(2, 4), replace=False)
            elif domain in ['DevOps', 'Cloud Computing']:
                required_skills = np.random.choice(['aws', 'docker', 'kubernetes', 'python', 'linux', 'jenkins'], size=np.random.randint(2, 4), replace=False)
            elif domain in ['UI/UX Design', 'Graphic Design']:
                required_skills = np.random.choice(['figma', 'adobe xd', 'sketch', 'photoshop', 'illustrator'], size=np.random.randint(2, 3), replace=False)
            elif domain in ['Digital Marketing', 'Content Writing']:
                required_skills = np.random.choice(['digital marketing', 'seo', 'content writing', 'social media', 'google analytics'], size=np.random.randint(2, 3), replace=False)
            else:
                required_skills = np.random.choice(self.skills_list, size=np.random.randint(2, 4), replace=False)
            
            # Generate realistic stipend
            stipend = max(10000, int(np.random.normal(stipend_base, stipend_std)))
            
            # Generate duration (most internships are 2-6 months)
            duration = np.random.choice([2, 3, 4, 6, 8], p=[0.10, 0.20, 0.30, 0.30, 0.10])
            
            # Generate positions available
            if company_size == 'large':
                positions = np.random.randint(5, 25)
            elif company_size == 'mid':
                positions = np.random.randint(2, 10)
            else:  # startup
                positions = np.random.randint(1, 5)
            
            # Generate application deadline (1-6 months from now)
            deadline = fake.date_between(start_date='today', end_date='+6m')
            
            internship = {
                'internship_id': f'INT_{i+1:05d}',
                'title': f'{domain} Intern',
                'company': company,
                'domain': domain,
                'location': np.random.choice(self.locations),
                'duration': duration,
                'stipend': stipend,
                'required_skills': ','.join(required_skills),
                'description': self._generate_job_description(domain, company),
                'application_deadline': deadline,
                'positions_available': positions,
                'company_size': company_size,
                'industry': np.random.choice(self.industries),
                'remote_work': np.random.choice(['yes', 'no', 'hybrid'], p=[0.30, 0.40, 0.30]),
                'experience_level': np.random.choice(['entry', 'intermediate', 'advanced'], p=[0.60, 0.30, 0.10]),
                'created_at': fake.date_time_between(start_date='-1y', end_date='now'),
                'is_active': np.random.choice([True, False], p=[0.85, 0.15])
            }
            
            internships.append(internship)
        
        df = pd.DataFrame(internships)
        print(f"✅ Generated {len(df)} internship opportunities")
        return df
    
    def generate_interactions(self, students_df, internships_df, n_interactions=50000):
        """Generate interaction data between students and internships."""
        print(f"🔄 Generating {n_interactions} student-internship interactions...")
        
        interactions = []
        interaction_types = ['view', 'apply', 'shortlist', 'reject']
        interaction_weights = [0.60, 0.25, 0.10, 0.05]  # Most interactions are views
        
        for i in range(n_interactions):
            student_id = np.random.choice(students_df['student_id'])
            internship_id = np.random.choice(internships_df['internship_id'])
            interaction_type = np.random.choice(interaction_types, p=interaction_weights)
            
            # Generate realistic timestamp (last 6 months)
            timestamp = fake.date_time_between(start_date='-6m', end_date='now')
            
            # Generate session info
            session_id = f'SESS_{np.random.randint(1000, 9999)}'
            device_type = np.random.choice(['mobile', 'desktop', 'tablet'], p=[0.60, 0.35, 0.05])
            source = np.random.choice(['search', 'referral', 'direct', 'social'], p=[0.40, 0.25, 0.20, 0.15])
            
            # Generate time spent based on interaction type
            if interaction_type == 'view':
                time_spent = np.random.randint(30, 300)  # 30 seconds to 5 minutes
                page_views = np.random.randint(1, 5)
            elif interaction_type == 'apply':
                time_spent = np.random.randint(300, 1800)  # 5-30 minutes
                page_views = np.random.randint(3, 10)
            else:
                time_spent = np.random.randint(60, 600)  # 1-10 minutes
                page_views = np.random.randint(1, 3)
            
            interaction = {
                'interaction_id': f'INT_{i+1:06d}',
                'student_id': student_id,
                'internship_id': internship_id,
                'interaction_type': interaction_type,
                'timestamp': timestamp,
                'session_id': session_id,
                'device_type': device_type,
                'source': source,
                'time_spent': time_spent,
                'page_views': page_views,
                'ip_address': fake.ipv4(),
                'user_agent': fake.user_agent()
            }
            
            interactions.append(interaction)
        
        df = pd.DataFrame(interactions)
        print(f"✅ Generated {len(df)} interactions")
        return df
    
    def generate_outcomes(self, students_df, internships_df, interactions_df):
        """Generate outcome data for applications."""
        print("📊 Generating application outcomes...")
        
        # Get all applications from interactions
        applications = interactions_df[interactions_df['interaction_type'] == 'apply'].copy()
        
        outcomes = []
        for i, (_, application) in enumerate(applications.iterrows()):
            student_id = application['student_id']
            internship_id = application['internship_id']
            application_date = application['timestamp']
            
            # Generate outcome based on realistic probabilities
            # Success rate is very low (0.1-0.5% as mentioned in your system)
            success_prob = 0.002  # 0.2% success rate
            
            if np.random.random() < success_prob:
                application_status = 'selected'
                selection_date = application_date + timedelta(days=np.random.randint(7, 60))
                interview_rounds = np.random.randint(2, 5)
                final_decision = 'accepted'
                feedback_score = np.random.uniform(4.0, 5.0)
                rejection_reason = None
            else:
                # Different rejection reasons
                rejection_reasons = [
                    'insufficient experience', 'skills mismatch', 'academic performance',
                    'interview performance', 'position filled', 'budget constraints',
                    'timing issues', 'cultural fit', 'technical skills gap'
                ]
                
                application_status = 'rejected'
                selection_date = application_date + timedelta(days=np.random.randint(3, 30))
                interview_rounds = np.random.randint(0, 3)  # Some don't get interviews
                final_decision = 'rejected'
                feedback_score = np.random.uniform(2.0, 4.0)
                rejection_reason = np.random.choice(rejection_reasons)
            
            outcome = {
                'outcome_id': f'OUT_{i+1:06d}',
                'student_id': student_id,
                'internship_id': internship_id,
                'application_status': application_status,
                'application_date': application_date,
                'selection_date': selection_date,
                'interview_rounds': interview_rounds,
                'final_decision': final_decision,
                'feedback_score': round(feedback_score, 1),
                'rejection_reason': rejection_reason,
                'success': 1 if application_status == 'selected' else 0
            }
            
            outcomes.append(outcome)
        
        df = pd.DataFrame(outcomes)
        print(f"✅ Generated {len(df)} application outcomes")
        return df
    
    def generate_companies(self, internships_df):
        """Generate company dataset from unique companies in internships."""
        print("🏢 Generating company profiles...")
        
        unique_companies = internships_df['company'].unique()
        companies = []
        
        for i, company_name in enumerate(unique_companies):
            # Determine industry based on company
            if company_name in ['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple']:
                industry = 'Technology'
                size = 'large'
                reputation_score = np.random.uniform(8.5, 10.0)
            elif company_name in ['TCS', 'Infosys', 'Wipro', 'HCL Technologies']:
                industry = 'Technology'
                size = 'large'
                reputation_score = np.random.uniform(7.0, 8.5)
            elif company_name in ['Flipkart', 'Ola', 'Swiggy', 'Zomato']:
                industry = 'E-commerce'
                size = 'mid'
                reputation_score = np.random.uniform(7.5, 9.0)
            else:
                industry = np.random.choice(self.industries)
                size = np.random.choice(['startup', 'mid', 'large'], p=[0.40, 0.35, 0.25])
                reputation_score = np.random.uniform(5.0, 9.0)
            
            company = {
                'company_id': f'COMP_{i+1:04d}',
                'company_name': company_name,
                'industry': industry,
                'size': size,
                'location': np.random.choice(self.locations),
                'reputation_score': round(reputation_score, 1),
                'growth_rate': round(np.random.uniform(-5.0, 25.0), 1),
                'employee_satisfaction': round(np.random.uniform(3.0, 5.0), 1),
                'founded_year': np.random.randint(1990, 2020),
                'website': f'https://{company_name.lower().replace(" ", "")}.com',
                'linkedin_url': f'https://linkedin.com/company/{company_name.lower().replace(" ", "-")}',
                'description': f'{company_name} is a leading company in {industry} industry.'
            }
            
            companies.append(company)
        
        df = pd.DataFrame(companies)
        print(f"✅ Generated {len(df)} company profiles")
        return df
    
    def _generate_job_description(self, domain, company):
        """Generate realistic job descriptions."""
        descriptions = {
            'Software Development': f"Join {company} as a Software Development Intern and work on cutting-edge projects. You'll collaborate with experienced developers to build scalable applications and learn industry best practices.",
            'Data Science': f"Work with {company}'s data science team to analyze large datasets, build predictive models, and derive actionable insights. Perfect opportunity to apply machine learning in real-world scenarios.",
            'Web Development': f"Develop responsive web applications using modern frameworks at {company}. You'll work on both frontend and backend development, gaining full-stack experience.",
            'Mobile Development': f"Create innovative mobile applications for {company}. Work with iOS/Android development, learn mobile UI/UX principles, and contribute to app store releases.",
            'DevOps': f"Learn cloud infrastructure and deployment automation at {company}. Work with AWS/Azure, Docker, Kubernetes, and CI/CD pipelines.",
            'UI/UX Design': f"Design intuitive user experiences for {company}'s products. Work with design tools, conduct user research, and create wireframes and prototypes.",
            'Digital Marketing': f"Drive digital marketing campaigns for {company}. Learn SEO, social media marketing, content creation, and analytics tools.",
            'Business Analysis': f"Analyze business processes and requirements at {company}. Work with stakeholders, create documentation, and support project management activities."
        }
        
        return descriptions.get(domain, f"Exciting internship opportunity at {company} in {domain}. Gain hands-on experience and work with industry professionals.")
    
    def generate_all_data(self):
        """Generate all datasets for production system."""
        print("🚀 Starting production data generation...")
        print("=" * 60)
        
        # Create data directory if it doesn't exist
        os.makedirs('api_data', exist_ok=True)
        
        # Generate datasets
        students_df = self.generate_students(5000)
        internships_df = self.generate_internships(1000)
        interactions_df = self.generate_interactions(students_df, internships_df, 50000)
        outcomes_df = self.generate_outcomes(students_df, internships_df, interactions_df)
        companies_df = self.generate_companies(internships_df)
        
        # Save datasets
        print("\n💾 Saving datasets...")
        students_df.to_csv('api_data/enhanced_students.csv', index=False)
        internships_df.to_csv('api_data/enhanced_internships.csv', index=False)
        interactions_df.to_csv('api_data/enhanced_interactions.csv', index=False)
        outcomes_df.to_csv('api_data/enhanced_outcomes.csv', index=False)
        companies_df.to_csv('api_data/enhanced_companies.csv', index=False)
        
        # Generate metadata
        metadata = {
            'generation_date': datetime.now().isoformat(),
            'total_students': len(students_df),
            'total_internships': len(internships_df),
            'total_interactions': len(interactions_df),
            'total_outcomes': len(outcomes_df),
            'total_companies': len(companies_df),
            'success_rate': outcomes_df['success'].mean(),
            'data_quality': {
                'students_completeness': (1 - students_df.isnull().sum().sum() / (len(students_df) * len(students_df.columns))) * 100,
                'internships_completeness': (1 - internships_df.isnull().sum().sum() / (len(internships_df) * len(internships_df.columns))) * 100,
                'interactions_completeness': (1 - interactions_df.isnull().sum().sum() / (len(interactions_df) * len(interactions_df.columns))) * 100
            }
        }
        
        with open('api_data/datasets_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Print summary
        print("\n📊 PRODUCTION DATA SUMMARY")
        print("=" * 60)
        print(f"🎓 Students: {len(students_df):,}")
        print(f"💼 Internships: {len(internships_df):,}")
        print(f"🔄 Interactions: {len(interactions_df):,}")
        print(f"📊 Outcomes: {len(outcomes_df):,}")
        print(f"🏢 Companies: {len(companies_df):,}")
        print(f"✅ Success Rate: {outcomes_df['success'].mean()*100:.2f}%")
        print(f"💾 Total Storage: ~{self._estimate_storage_size():.1f} MB")
        
        print(f"\n🎉 Production data generation complete!")
        print(f"📁 All files saved to 'api_data/' directory")
        
        return {
            'students': students_df,
            'internships': internships_df,
            'interactions': interactions_df,
            'outcomes': outcomes_df,
            'companies': companies_df
        }
    
    def _estimate_storage_size(self):
        """Estimate total storage size of generated data."""
        # Rough estimation based on typical CSV sizes
        return 5000 * 0.5 + 1000 * 0.3 + 50000 * 0.1 + 1000 * 0.2 + 100 * 0.1  # MB


def main():
    """Main function to generate production data."""
    generator = ProductionDataGenerator()
    datasets = generator.generate_all_data()
    
    # Validate data quality
    print("\n🔍 DATA QUALITY VALIDATION")
    print("=" * 60)
    
    for name, df in datasets.items():
        completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        duplicates = df.duplicated().sum()
        print(f"{name.capitalize()}: {completeness:.1f}% complete, {duplicates} duplicates")
    
    print(f"\n✅ All datasets ready for production ML system!")
    return datasets


if __name__ == "__main__":
    datasets = main()
