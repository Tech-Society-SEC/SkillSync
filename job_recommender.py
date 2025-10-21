"""
Job Recommendation System
Uses TF-IDF + Cosine Similarity for content-based job recommendations

This module:
1. Creates TF-IDF vectors from job requirements
2. Creates TF-IDF vectors from worker skills
3. Calculates cosine similarity between workers and jobs
4. Recommends top matching jobs
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from pathlib import Path
import pickle


class JobRecommender:
    """Content-based job recommendation system"""
    
    def __init__(
        self, 
        job_listings_path: str = "datasets/job_listings.csv",
        learning_resources_path: str = "datasets/learning_resources.csv"
    ):
        """
        Initialize job recommender
        
        Args:
            job_listings_path: Path to job listings CSV
            learning_resources_path: Path to learning resources CSV
        """
        print("Initializing Job Recommender...")
        
        # Load datasets
        self.jobs_df = self._load_data(job_listings_path)
        self.learning_df = self._load_data(learning_resources_path)
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        # Create job vectors
        if not self.jobs_df.empty:
            self._create_job_vectors()
        
        print("✓ Job Recommender initialized")
    
    def _load_data(self, path: str) -> pd.DataFrame:
        """Load dataset from CSV"""
        if Path(path).exists():
            df = pd.read_csv(path)
            print(f"Loaded {len(df)} records from {Path(path).name}")
            return df
        else:
            print(f"Warning: File not found at {path}")
            return pd.DataFrame()
    
    def _create_job_vectors(self):
        """Create TF-IDF vectors for all jobs"""
        print("Creating TF-IDF vectors for jobs...")
        
        # Combine relevant job fields into text
        self.jobs_df['combined_text'] = (
            self.jobs_df['job_title'] + ' ' + 
            self.jobs_df['category'] + ' ' + 
            self.jobs_df['required_skills'].fillna('')
        )
        
        # Fit TF-IDF vectorizer on job corpus
        self.job_vectors = self.vectorizer.fit_transform(
            self.jobs_df['combined_text']
        )
        
        print(f"✓ Created vectors of shape {self.job_vectors.shape}")
    
    def _create_worker_vector(self, worker_skills: List[str]) -> np.ndarray:
        """
        Create TF-IDF vector for worker skills
        
        Args:
            worker_skills: List of worker's skills
            
        Returns:
            TF-IDF vector
        """
        # Combine skills into text
        skills_text = ' '.join(worker_skills)
        
        # Transform using fitted vectorizer
        worker_vector = self.vectorizer.transform([skills_text])
        
        return worker_vector
    
    def recommend_jobs(
        self, 
        worker_skills: List[str], 
        location: str = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Recommend jobs based on worker skills
        
        Args:
            worker_skills: List of worker's skills
            location: Preferred location (optional)
            top_k: Number of recommendations
            
        Returns:
            List of recommended jobs with scores
        """
        if self.jobs_df.empty or len(worker_skills) == 0:
            return []
        
        # Create worker vector
        worker_vector = self._create_worker_vector(worker_skills)
        
        # Calculate cosine similarity with all jobs
        similarities = cosine_similarity(worker_vector, self.job_vectors)[0]
        
        # Add similarity scores to dataframe
        jobs_with_scores = self.jobs_df.copy()
        jobs_with_scores['match_score'] = similarities
        
        # Filter by location if specified
        if location:
            jobs_with_scores = jobs_with_scores[
                jobs_with_scores['location'].str.contains(location, case=False, na=False)
            ]
        
        # Sort by match score
        top_jobs = jobs_with_scores.nlargest(top_k, 'match_score')
        
        # Format results
        recommendations = []
        for _, job in top_jobs.iterrows():
            recommendations.append({
                'job_id': job['job_id'],
                'job_title': job['job_title'],
                'category': job['category'],
                'required_skills': job['required_skills'],
                'experience_required': job['experience_required'],
                'salary_range': job['salary_range'],
                'location': job['location'],
                'job_type': job['job_type'],
                'match_score': round(job['match_score'], 3),
                'match_percentage': round(job['match_score'] * 100, 1)
            })
        
        return recommendations
    
    def recommend_learning(
        self, 
        worker_skills: List[str],
        target_skills: List[str] = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Recommend learning resources for upskilling
        
        Args:
            worker_skills: Current skills of worker
            target_skills: Skills they want to learn (optional)
            top_k: Number of recommendations
            
        Returns:
            List of learning resources
        """
        if self.learning_df.empty:
            return []
        
        # If target skills specified, recommend for those
        if target_skills:
            search_skills = target_skills
        else:
            # Otherwise, recommend related skills
            search_skills = worker_skills
        
        # Create TF-IDF vectors for learning resources
        learning_texts = (
            self.learning_df['title'] + ' ' + 
            self.learning_df['skill_covered'].fillna('') + ' ' + 
            self.learning_df['category'].fillna('')
        )
        
        learning_vectorizer = TfidfVectorizer(max_features=300, ngram_range=(1, 2))
        learning_vectors = learning_vectorizer.fit_transform(learning_texts)
        
        # Create vector for search skills
        search_text = ' '.join(search_skills)
        search_vector = learning_vectorizer.transform([search_text])
        
        # Calculate similarity
        similarities = cosine_similarity(search_vector, learning_vectors)[0]
        
        # Get top resources
        self.learning_df['relevance_score'] = similarities
        top_resources = self.learning_df.nlargest(top_k, 'relevance_score')
        
        # Format results
        recommendations = []
        for _, resource in top_resources.iterrows():
            recommendations.append({
                'resource_id': resource['resource_id'],
                'title': resource['title'],
                'skill_covered': resource['skill_covered'],
                'resource_type': resource['resource_type'],
                'platform': resource['platform'],
                'language': resource['language'],
                'duration': resource['duration'],
                'difficulty': resource['difficulty'],
                'rating': resource['rating'],
                'is_free': resource['is_free'],
                'relevance_score': round(resource['relevance_score'], 3)
            })
        
        return recommendations
    
    def get_skill_gap_analysis(
        self, 
        worker_skills: List[str],
        target_job_title: str
    ) -> Dict:
        """
        Analyze skill gaps between worker and target job
        
        Args:
            worker_skills: Current skills
            target_job_title: Desired job title
            
        Returns:
            Skill gap analysis
        """
        # Find jobs matching target title
        matching_jobs = self.jobs_df[
            self.jobs_df['job_title'].str.contains(target_job_title, case=False, na=False)
        ]
        
        if matching_jobs.empty:
            return {'error': 'No jobs found for that title'}
        
        # Get required skills from top matching job
        top_job = matching_jobs.iloc[0]
        required_skills = set(top_job['required_skills'].split(', '))
        current_skills = set(worker_skills)
        
        # Calculate gaps
        matched_skills = current_skills & required_skills
        missing_skills = required_skills - current_skills
        extra_skills = current_skills - required_skills
        
        return {
            'target_job': top_job['job_title'],
            'category': top_job['category'],
            'total_required_skills': len(required_skills),
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'extra_skills': list(extra_skills),
            'match_percentage': round(len(matched_skills) / len(required_skills) * 100, 1) if required_skills else 0
        }
    
    def save_model(self, filepath: str):
        """Save trained model and vectorizer"""
        model_data = {
            'vectorizer': self.vectorizer,
            'job_vectors': self.job_vectors,
            'jobs_df': self.jobs_df
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load pre-trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.job_vectors = model_data['job_vectors']
        self.jobs_df = model_data['jobs_df']
        
        print(f"✓ Model loaded from {filepath}")


def main():
    """Demo and testing"""
    print("=" * 70)
    print("Job Recommendation System - Demo")
    print("=" * 70)
    
    # Initialize recommender
    recommender = JobRecommender()
    
    # Test Case 1: Electrician
    print("\n" + "=" * 70)
    print("Test Case 1: Electrician Worker")
    print("=" * 70)
    
    worker_skills_1 = [
        "Electrical Wiring",
        "Fan Installation",
        "Switch Board Repair",
        "Circuit Troubleshooting"
    ]
    
    print(f"\nWorker Skills: {', '.join(worker_skills_1)}")
    print("\nTop 5 Recommended Jobs:")
    
    jobs_1 = recommender.recommend_jobs(worker_skills_1, top_k=5)
    for i, job in enumerate(jobs_1, 1):
        print(f"\n  {i}. {job['job_title']} - {job['location']}")
        print(f"     Match: {job['match_percentage']}%")
        print(f"     Salary: {job['salary_range']}")
        print(f"     Type: {job['job_type']}")
        print(f"     Required Skills: {job['required_skills'][:80]}...")
    
    # Test Case 2: Carpenter
    print("\n\n" + "=" * 70)
    print("Test Case 2: Carpenter Worker")
    print("=" * 70)
    
    worker_skills_2 = [
        "Wood Cutting",
        "Furniture Making",
        "Door Fitting",
        "Wood Polishing"
    ]
    
    print(f"\nWorker Skills: {', '.join(worker_skills_2)}")
    print("\nTop 5 Recommended Jobs:")
    
    jobs_2 = recommender.recommend_jobs(worker_skills_2, location="Chennai", top_k=5)
    for i, job in enumerate(jobs_2, 1):
        print(f"\n  {i}. {job['job_title']} - {job['location']}")
        print(f"     Match: {job['match_percentage']}%")
        print(f"     Salary: {job['salary_range']}")
    
    # Test Case 3: Learning Recommendations
    print("\n\n" + "=" * 70)
    print("Test Case 3: Learning Recommendations")
    print("=" * 70)
    
    print(f"\nWorker wants to upskill in: Electrical Wiring")
    learning = recommender.recommend_learning(["Electrical Wiring"], top_k=5)
    
    print("\nTop 5 Learning Resources:")
    for i, resource in enumerate(learning, 1):
        print(f"\n  {i}. {resource['title']}")
        print(f"     Platform: {resource['platform']} | Language: {resource['language']}")
        print(f"     Duration: {resource['duration']} | Level: {resource['difficulty']}")
        print(f"     Free: {'Yes' if resource['is_free'] else 'No'} | Rating: {resource['rating']}")
    
    # Test Case 4: Skill Gap Analysis
    print("\n\n" + "=" * 70)
    print("Test Case 4: Skill Gap Analysis")
    print("=" * 70)
    
    gap_analysis = recommender.get_skill_gap_analysis(
        worker_skills_1,
        "Electrician"
    )
    
    print(f"\nTarget Job: {gap_analysis['target_job']}")
    print(f"Category: {gap_analysis['category']}")
    print(f"Match: {gap_analysis['match_percentage']}%")
    print(f"\nMatched Skills ({len(gap_analysis['matched_skills'])}):")
    for skill in gap_analysis['matched_skills']:
        print(f"  ✓ {skill}")
    print(f"\nMissing Skills ({len(gap_analysis['missing_skills'])}):")
    for skill in gap_analysis['missing_skills']:
        print(f"  ✗ {skill}")
    
    # Save model
    print("\n\n" + "=" * 70)
    print("Saving Model")
    print("=" * 70)
    recommender.save_model("models/job_recommender.pkl")
    
    print("\n" + "=" * 70)
    print("✓ Job Recommendation Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
