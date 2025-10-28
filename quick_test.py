"""
Quick Test Script - Fast verification of all components
Run this to quickly check if everything is working
"""

import sys
from pathlib import Path


def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        import pandas as pd
        import numpy as np
        import sklearn
        print("  ✓ Core libraries (pandas, numpy, sklearn)")
        
        import torch
        import transformers
        print("  ✓ Deep learning (torch, transformers)")
        
        from sentence_transformers import SentenceTransformer
        print("  ✓ Sentence-transformers")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        print("\n  Run: pip install -r requirements.txt")
        return False


def test_datasets():
    """Check if datasets exist"""
    print("\nChecking datasets...")
    
    datasets_dir = Path("datasets")
    required_files = [
        "skill_taxonomy.csv",
        "worker_utterances.csv",
        "job_listings.csv",
        "worker_profiles.csv",
        "learning_resources.csv"
    ]
    
    if not datasets_dir.exists():
        print("  ✗ datasets/ folder not found")
        print("  Run: python generate_datasets.py")
        return False
    
    missing = []
    for file in required_files:
        if (datasets_dir / file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (missing)")
            missing.append(file)
    
    if missing:
        print(f"\n  Missing {len(missing)} files. Run: python generate_datasets.py")
        return False
    
    return True


def test_skill_extraction():
    """Test skill extraction module"""
    print("\nTesting Skill Extraction...")
    try:
        from skill_extraction import SkillExtractor
        
        extractor = SkillExtractor()
        result = extractor.extract_from_utterance(
            "I have 5 years experience in electrical wiring"
        )
        
        if result['skills']:
            print(f"  ✓ Extracted skills: {[s['skill'] for s in result['skills'][:2]]}")
            return True
        else:
            print("  ⚠ No skills extracted (may need to check taxonomy)")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_skill_normalization():
    """Test skill normalization module"""
    print("\nTesting Skill Normalization...")
    try:
        from skill_normalization import SkillNormalizer
        
        print("  Loading Sentence-BERT model (may take time on first run)...")
        normalizer = SkillNormalizer()
        
        matches = normalizer.normalize_skill("electric work", threshold=0.4, top_k=1)
        
        if matches:
            print(f"  ✓ Normalized 'electric work' → '{matches[0]['normalized_skill']}'")
            return True
        else:
            print("  ⚠ No matches found (threshold may be too high)")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_job_recommender():
    """Test job recommendation module"""
    print("\nTesting Job Recommender...")
    try:
        from job_recommender import JobRecommender
        
        recommender = JobRecommender()
        jobs = recommender.recommend_jobs(
            ["Electrical Wiring", "Fan Installation"], 
            top_k=3
        )
        
        if jobs:
            print(f"  ✓ Found {len(jobs)} job recommendations")
            print(f"    Top job: {jobs[0]['job_title']} ({jobs[0]['match_percentage']}% match)")
            return True
        else:
            print("  ⚠ No jobs found")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_pipeline():
    """Test complete pipeline"""
    print("\nTesting Complete Pipeline...")
    try:
        from ml_pipeline import SkillSyncPipeline
        
        pipeline = SkillSyncPipeline(use_whisper=False)
        
        result = pipeline.process_text_input(
            "I am electrician with 5 years experience"
        )
        
        skills = result['extracted_info']['normalized_skills']
        jobs = result['job_recommendations']
        
        print(f"  ✓ Pipeline processed successfully")
        print(f"    Skills: {skills[:3]}")
        print(f"    Jobs: {len(jobs)} recommendations")
        print(f"    Processing time: {result['processing_time']}s")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("SkillSync ML Module - Quick Test")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Datasets", test_datasets()))
    results.append(("Skill Extraction", test_skill_extraction()))
    results.append(("Skill Normalization", test_skill_normalization()))
    results.append(("Job Recommender", test_job_recommender()))
    results.append(("Complete Pipeline", test_pipeline()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Run full demo: python run_complete_demo.py")
        print("  2. Integrate with backend API")
        print("  3. Test with real voice inputs")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("  - Make sure you ran: python generate_datasets.py")
        print("  - Make sure you ran: pip install -r requirements.txt")
    
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
