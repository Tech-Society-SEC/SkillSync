"""
SkillSync ML Pipeline - Complete Integration (Voice-First)
Combines all components for end-to-end processing
Primary Input: Voice/Audio → Text → Skills → Jobs
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from pathlib import Path
import time
import logging

# Import custom modules
try:
    from skill_extraction_multilingual import MultilingualSkillExtractor as SkillExtractor
except ImportError:
    try:
        from skill_extraction_improved import ImprovedSkillExtractor as SkillExtractor
    except ImportError:
        from skill_extraction import SkillExtractor

from skill_normalization import SkillNormalizer
from job_recommender import JobRecommender

# Import audio processor
try:
    from audio_processor import AudioProcessor
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Audio processor not available. Install: pip install openai-whisper")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillSyncPipeline:
    """Complete ML pipeline for SkillSync"""
    
    def __init__(
        self,
        use_whisper: bool = False,
        skill_taxonomy_path: str = "datasets/skill_taxonomy.csv",
        job_listings_path: str = "datasets/job_listings.csv",
        learning_resources_path: str = "datasets/learning_resources.csv"
    ):
        """
        Initialize the complete ML pipeline
        
        Args:
            use_whisper: Enable speech-to-text (requires audio input)
            skill_taxonomy_path: Path to skill taxonomy
            job_listings_path: Path to job listings
            learning_resources_path: Path to learning resources
        """
        print("=" * 70)
        print("SkillSync ML Pipeline - Initialization")
        print("=" * 70)
        
        self.use_whisper = use_whisper
        
        # Initialize Speech-to-Text (Voice-First)
        self.audio_processor = None
        if use_whisper and AUDIO_AVAILABLE:
            try:
                print("\n[1/5] Initializing Audio Processor (Whisper)...")
                self.audio_processor = AudioProcessor(model_size="base")
                print("✓ Audio processor ready")
            except Exception as e:
                print(f"⚠ Audio processor failed: {e}")
                print("  Install with: pip install openai-whisper")
        elif use_whisper:
            print("⚠ Audio processing not available.")
            print("  Install: pip install openai-whisper ffmpeg-python pydub")
        
        # Initialize Skill Extraction (Multilingual)
        print(f"\n[{2 if use_whisper else 1}/4] Initializing Skill Extractor (Multilingual)...")
        try:
            self.skill_extractor = SkillExtractor(skill_taxonomy_path=skill_taxonomy_path)
        except TypeError:
            # For MultilingualSkillExtractor which may have different signature
            self.skill_extractor = SkillExtractor()
        print("✓ Skill Extractor initialized")
        
        # Initialize Skill Normalization
        print(f"\n[{3 if use_whisper else 2}/4] Initializing Skill Normalizer...")
        self.skill_normalizer = SkillNormalizer(
            skill_taxonomy_path=skill_taxonomy_path
        )
        
        # Initialize Job Recommender
        print(f"\n[{4 if use_whisper else 3}/4] Initializing Job Recommender...")
        self.job_recommender = JobRecommender(
            job_listings_path=job_listings_path,
            learning_resources_path=learning_resources_path
        )
        
        print("\n" + "=" * 70)
        print("✓ SkillSync Pipeline Ready!")
        print("=" * 70)
    
    def transcribe_audio(self, audio_path: Union[str, Path], **kwargs) -> Dict:
        """
        Convert speech to text using Whisper (Voice-First Primary Method)
        
        Args:
            audio_path: Path to audio file (mp3, wav, m4a, etc.)
            **kwargs: Additional transcription parameters
            
        Returns:
            Transcription result with text, language, segments, etc.
        """
        if not self.audio_processor:
            raise Exception("Audio processor not initialized. Set use_whisper=True")
        
        logger.info(f"🎤 Transcribing audio: {Path(audio_path).name}")
        result = self.audio_processor.transcribe_audio(audio_path, **kwargs)
        
        if result['success']:
            logger.info(f"✓ Transcription complete: {result['text'][:100]}...")
        else:
            logger.error(f"✗ Transcription failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def process_text_input(self, text: str) -> Dict:
        """
        Process text input through the complete pipeline
        
        Args:
            text: Worker utterance (text)
            
        Returns:
            Complete profile with skills, jobs, and learning recommendations
        """
        start_time = time.time()
        
        print("\n" + "=" * 70)
        print("Processing Worker Input")
        print("=" * 70)
        print(f"\nInput: {text}")
        
        # Step 1: Extract skills from text
        print("\n[Step 1/3] Extracting skills...")
        extraction_result = self.skill_extractor.extract_from_utterance(text)
        
        raw_skills = [s['skill'] for s in extraction_result['skills']]
        print(f"✓ Extracted {len(raw_skills)} skills: {', '.join(raw_skills[:5])}")
        
        # Step 2: Normalize skills
        print("\n[Step 2/3] Normalizing skills...")
        normalized_skills = []
        
        for raw_skill in raw_skills:
            matches = self.skill_normalizer.normalize_skill(
                raw_skill, 
                threshold=0.5, 
                top_k=1
            )
            if matches:
                normalized_skills.append(matches[0])
        
        unique_normalized = list({s['normalized_skill'] for s in normalized_skills})
        print(f"✓ Normalized to {len(unique_normalized)} standard skills")
        
        # Step 3: Generate recommendations
        print("\n[Step 3/3] Generating recommendations...")
        
        # Job recommendations
        job_recommendations = self.job_recommender.recommend_jobs(
            worker_skills=unique_normalized,
            top_k=10
        )
        print(f"✓ Found {len(job_recommendations)} job matches")
        
        # Learning recommendations
        learning_recommendations = self.job_recommender.recommend_learning(
            worker_skills=unique_normalized,
            top_k=5
        )
        print(f"✓ Found {len(learning_recommendations)} learning resources")
        
        # Compile complete profile
        profile = {
            'input_text': text,
            'processing_time': round(time.time() - start_time, 2),
            'extracted_info': {
                'raw_skills': raw_skills,
                'normalized_skills': unique_normalized,
                'job_title': extraction_result.get('job_title', ''),
                'experience_years': extraction_result.get('experience_years', 0),
                'categories': extraction_result.get('categories', [])
            },
            'job_recommendations': job_recommendations[:5],  # Top 5
            'learning_recommendations': learning_recommendations,
            'skill_details': normalized_skills
        }
        
        print(f"\n✓ Profile created in {profile['processing_time']}s")
        
        return profile
    
    def process_audio_input(self, audio_path: Union[str, Path], **kwargs) -> Dict:
        """
        Process audio input through complete pipeline (Voice-First Main Entry Point)
        
        This is the primary method for voice-based worker registration:
        Voice → Text → Skills → Jobs → Profile
        
        Args:
            audio_path: Path to audio file (mp3, wav, m4a, ogg, etc.)
            **kwargs: Additional transcription parameters
            
        Returns:
            Complete profile with:
            - transcription (text, language, segments)
            - extracted_info (skills, experience, job_title)
            - job_recommendations
            - learning_recommendations
        """
        logger.info(f"🎙️ Voice-First Processing: {Path(audio_path).name}")
        
        # Step 1: Transcribe audio to text
        transcription_result = self.transcribe_audio(audio_path, **kwargs)
        
        if not transcription_result['success']:
            return {
                'success': False,
                'error': 'Transcription failed',
                'transcription': transcription_result
            }
        
        text = transcription_result['text']
        
        # Step 2: Process the transcribed text
        processing_result = self.process_text_input(text)
        
        # Step 3: Combine results
        processing_result['transcription'] = {
            'text': transcription_result['text'],
            'language': transcription_result['language'],
            'duration': transcription_result['duration'],
            'segments': transcription_result.get('segments', [])
        }
        processing_result['audio_file'] = str(audio_path)
        processing_result['success'] = True
        
        logger.info(f"✓ Voice processing complete")
        
        return processing_result
    
    def create_worker_profile(
        self, 
        text: str, 
        worker_info: Dict = None
    ) -> Dict:
        """
        Create a complete worker profile
        
        Args:
            text: Worker utterance
            worker_info: Additional info (name, age, location, etc.)
            
        Returns:
            Complete worker profile
        """
        # Process through pipeline
        result = self.process_text_input(text)
        
        # Add additional worker info
        if worker_info:
            result['worker_info'] = worker_info
        
        return result
    
    def batch_process(
        self, 
        texts: List[str], 
        output_file: str = None
    ) -> List[Dict]:
        """
        Process multiple utterances in batch
        
        Args:
            texts: List of worker utterances
            output_file: Optional file to save results
            
        Returns:
            List of profiles
        """
        print(f"\n\nBatch processing {len(texts)} utterances...")
        
        profiles = []
        for i, text in enumerate(texts, 1):
            print(f"\nProcessing {i}/{len(texts)}...")
            profile = self.process_text_input(text)
            profiles.append(profile)
        
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(profiles, f, indent=2)
            print(f"\n✓ Results saved to {output_file}")
        
        return profiles
    
    def get_recommendations_for_profile(
        self, 
        skills: List[str], 
        location: str = None
    ) -> Dict:
        """
        Get fresh recommendations for existing profile
        
        Args:
            skills: List of worker skills
            location: Preferred location
            
        Returns:
            Job and learning recommendations
        """
        jobs = self.job_recommender.recommend_jobs(
            worker_skills=skills,
            location=location,
            top_k=10
        )
        
        learning = self.job_recommender.recommend_learning(
            worker_skills=skills,
            top_k=5
        )
        
        return {
            'job_recommendations': jobs,
            'learning_recommendations': learning
        }


def main():
    """Demo of complete pipeline"""
    print("\n" * 2)
    print("*" * 70)
    print("SkillSync ML Pipeline - Complete Demo")
    print("*" * 70)
    
    # Initialize pipeline
    pipeline = SkillSyncPipeline(use_whisper=False)
    
    # Test utterances in different languages/styles
    test_cases = [
        {
            "text": "I have 7 years experience in electrical wiring, fan installation and switch board repair",
            "name": "Ravi Kumar",
            "location": "Chennai"
        },
        {
            "text": "I am a plumber. I know pipe fitting, tap repair and drainage fixing. Working for 5 years",
            "name": "Suresh",
            "location": "Mumbai"
        },
        {
            "text": "Naan carpenter. Wood cutting, furniture making, door fitting ellam pannuven. 10 years experience",
            "name": "Selvam",
            "location": "Chennai"
        }
    ]
    
    print("\n\n" + "=" * 70)
    print("Running Test Cases")
    print("=" * 70)
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n\n{'='*70}")
        print(f"TEST CASE {i}: {case['name']} from {case['location']}")
        print("=" * 70)
        
        # Process through pipeline
        profile = pipeline.create_worker_profile(
            text=case['text'],
            worker_info={
                'name': case['name'],
                'location': case['location']
            }
        )
        
        # Display results
        print("\n--- Extracted Profile ---")
        print(f"Skills: {', '.join(profile['extracted_info']['normalized_skills'][:5])}")
        print(f"Experience: {profile['extracted_info']['experience_years']} years")
        print(f"Categories: {', '.join(profile['extracted_info']['categories'])}")
        
        print("\n--- Top 3 Job Recommendations ---")
        for j, job in enumerate(profile['job_recommendations'][:3], 1):
            print(f"\n{j}. {job['job_title']} - {job['location']}")
            print(f"   Match: {job['match_percentage']}% | Salary: {job['salary_range']}")
        
        print("\n--- Top 3 Learning Resources ---")
        for j, resource in enumerate(profile['learning_recommendations'][:3], 1):
            print(f"\n{j}. {resource['title']}")
            print(f"   {resource['platform']} | {resource['language']} | {resource['difficulty']}")
        
        results.append(profile)
    
    # Save all results
    output_file = "outputs/pipeline_results.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n\n" + "=" * 70)
    print("✓ Pipeline Demo Complete!")
    print(f"✓ Results saved to: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
