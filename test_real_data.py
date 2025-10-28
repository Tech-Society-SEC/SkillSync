"""
Real Data Testing Framework
Test the ML pipeline with real-world worker examples
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Real Worker Examples (Indian Informal Sector)
# ============================================================================

REAL_TEST_CASES = [
    {
        "id": "WORKER_001",
        "name": "Ravi Kumar",
        "input_text": "I have 8 years experience in electrical work. I can do house wiring, fan installation, switch board repair. I also know motor winding.",
        "language": "english",
        "location": "Chennai",
        "expected_skills": ["Electrical Wiring", "Fan Installation", "Switch Board Repair", "Motor Winding"],
        "expected_category": "Electrical Work"
    },
    {
        "id": "WORKER_002",
        "name": "Suresh Patel",
        "input_text": "मैं प्लंबर हूं। मुझे पाइप फिटिंग, नल की मरम्मत, और बाथरूम फिटिंग का काम आता है। 5 साल का अनुभव है।",
        "language": "hindi",
        "location": "Mumbai",
        "expected_skills": ["Pipe Fitting", "Tap Repair", "Bathroom Fitting"],
        "expected_category": "Plumbing"
    },
    {
        "id": "WORKER_003",
        "name": "Murugan",
        "input_text": "நான் தச்சு வேலை செய்கிறேன். மரம் வெட்டுதல், பர்னிச்சர் செய்தல், கதவு பொருத்துதல் தெரியும். 10 வருடங்கள் அனுபவம்.",
        "language": "tamil",
        "location": "Coimbatore",
        "expected_skills": ["Wood Cutting", "Furniture Making", "Door Installation"],
        "expected_category": "Carpentry"
    },
    {
        "id": "WORKER_004",
        "name": "Ahmed Ali",
        "input_text": "I am auto mechanic. I repair bikes and cars. Engine repair, brake service, oil change all I know. 6 years working in garage.",
        "language": "english",
        "location": "Bangalore",
        "expected_skills": ["Engine Repair", "Brake Service", "Oil Change", "Vehicle Maintenance"],
        "expected_category": "Automotive Repair"
    },
    {
        "id": "WORKER_005",
        "name": "Lakshmi",
        "input_text": "I do tailoring work at home. Blouse stitching, saree fall, churidar making. Ladies suits also I make. 12 years experience.",
        "language": "english",
        "location": "Hyderabad",
        "expected_skills": ["Blouse Stitching", "Saree Work", "Suit Making", "Tailoring"],
        "expected_category": "Tailoring & Garments"
    },
    {
        "id": "WORKER_006",
        "name": "Rajesh Singh",
        "input_text": "मैं वेल्डिंग का काम करता हूं। स्टील फैब्रिकेशन, गेट बनाना, ग्रिल वर्क सब आता है। 7 साल का अनुभव।",
        "language": "hindi",
        "location": "Delhi",
        "expected_skills": ["Welding", "Steel Fabrication", "Gate Making", "Grill Work"],
        "expected_category": "Welding & Metal Work"
    },
    {
        "id": "WORKER_007",
        "name": "Venkatesh",
        "input_text": "నాకు పెయింటింగ్ పని తెలుసు. గోడల పెయింటింగ్, బాహ్య పెయింటింగ్, వార్నిషింగ్ చేయగలను. 9 సంవత్సరాల అనుభవం.",
        "language": "telugu",
        "location": "Vijayawada",
        "expected_skills": ["Wall Painting", "External Painting", "Varnishing"],
        "expected_category": "Painting & Decoration"
    },
    {
        "id": "WORKER_008",
        "name": "Ramesh Kumar",
        "input_text": "I drive taxi for 15 years. Licensed driver with clean record. Know all routes in city. Good with customers.",
        "language": "english",
        "location": "Pune",
        "expected_skills": ["Taxi Driving", "Licensed Driver", "Route Knowledge", "Customer Service"],
        "expected_category": "Driving"
    },
    {
        "id": "WORKER_009",
        "name": "Santosh",
        "input_text": "Mobile repair mechanic. Screen replacement, battery change, software issues all I fix. iPhone, Samsung all brands. 4 years shop.",
        "language": "english",
        "location": "Jaipur",
        "expected_skills": ["Mobile Repair", "Screen Replacement", "Battery Replacement", "Software Troubleshooting"],
        "expected_category": "Mobile & Electronics Repair"
    },
    {
        "id": "WORKER_010",
        "name": "Priya Devi",
        "input_text": "ನಾನು ಬ್ಯೂಟಿ ಪಾರ್ಲರ್ ನಲ್ಲಿ ಕೆಲಸ ಮಾಡುತ್ತೇನೆ. ಹೇರ್ ಕಟ್, ಫೇಶಿಯಲ್, ಮೇಕಪ್ ಎಲ್ಲಾ ತಿಳಿದಿದೆ. 6 ವರ್ಷ ಅನುಭವ.",
        "language": "kannada",
        "location": "Mysore",
        "expected_skills": ["Hair Cutting", "Facial Treatment", "Makeup"],
        "expected_category": "Beauty & Salon"
    }
]


# ============================================================================
# Testing Functions
# ============================================================================

def test_skill_extraction(test_case: Dict):
    """Test skill extraction on real data"""
    try:
        # Try multilingual extractor first (best for Indian languages)
        extractor_type = 'original'
        try:
            from skill_extraction_multilingual import MultilingualSkillExtractor
            extractor = MultilingualSkillExtractor()
            extractor_type = 'multilingual'
        except:
            # Try improved extractor
            try:
                from skill_extraction_improved import ImprovedSkillExtractor
                extractor = ImprovedSkillExtractor()
                extractor_type = 'improved'
            except:
                # Fallback to original
                from skill_extraction import SkillExtractor
                extractor = SkillExtractor()
                extractor_type = 'original'
        
        result = extractor.extract_from_utterance(test_case['input_text'])
        
        extracted_skills = [s['skill'] for s in result.get('skills', [])]
        
        # Get category safely
        category = ''
        if 'primary_category' in result:
            category = result['primary_category']
        elif 'categories' in result and result['categories']:
            category = result['categories'][0] if isinstance(result['categories'], list) else result['categories']
        
        return {
            'success': True,
            'extracted_skills': extracted_skills,
            'experience': result.get('experience_years', 0),
            'job_title': result.get('job_title', ''),
            'category': category,
            'extractor_type': extractor_type
        }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def test_skill_normalization(test_case: Dict, extracted_skills: List[str]):
    """Test skill normalization"""
    try:
        from skill_normalization import SkillNormalizer
        
        normalizer = SkillNormalizer()
        
        normalized = []
        for skill in extracted_skills:
            result = normalizer.normalize_skill(skill)
            # normalize_skill returns a list of matches
            if result and len(result) > 0:
                normalized.append(result[0]['normalized_skill'])
            else:
                normalized.append(skill)  # Keep original if no match
        
        return {
            'success': True,
            'normalized_skills': normalized
        }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def test_job_recommendations(test_case: Dict, skills: List[str]):
    """Test job recommendations"""
    try:
        from job_recommender import JobRecommender
        
        recommender = JobRecommender()
        
        jobs = recommender.recommend_jobs(
            worker_skills=skills,
            location=test_case.get('location', ''),
            top_k=5
        )
        
        return {
            'success': True,
            'job_count': len(jobs),
            'top_jobs': [j['job_title'] for j in jobs[:3]] if jobs else [],
            'avg_match': float(sum(j['match_percentage'] for j in jobs) / len(jobs)) if jobs else 0.0
        }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def test_complete_pipeline(test_case: Dict):
    """Test complete pipeline"""
    try:
        from ml_pipeline import SkillSyncPipeline
        
        pipeline = SkillSyncPipeline(use_whisper=False)
        
        result = pipeline.process_text_input(test_case['input_text'])
        
        return {
            'success': True,
            'result': result
        }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def calculate_accuracy(extracted: List[str], expected: List[str]) -> float:
    """Calculate skill extraction accuracy"""
    if not expected:
        return 0.0
    
    # Fuzzy matching
    matches = 0
    for exp_skill in expected:
        for ext_skill in extracted:
            # Simple substring matching
            if exp_skill.lower() in ext_skill.lower() or ext_skill.lower() in exp_skill.lower():
                matches += 1
                break
    
    return (matches / len(expected)) * 100


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all real data tests"""
    print("\n" + "="*70)
    print("🧪 Real Data Testing - SkillSync ML Pipeline")
    print("="*70)
    print(f"\nTesting with {len(REAL_TEST_CASES)} real worker examples")
    print("Languages: English, Hindi, Tamil, Telugu, Kannada")
    print("="*70)
    
    results = []
    
    for i, test_case in enumerate(REAL_TEST_CASES, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}/{len(REAL_TEST_CASES)}: {test_case['id']}")
        print(f"{'='*70}")
        print(f"Worker: {test_case['name']}")
        print(f"Language: {test_case['language']}")
        print(f"Location: {test_case['location']}")
        print(f"\nInput: {test_case['input_text'][:100]}...")
        
        test_result = {
            'test_case': test_case,
            'timestamp': datetime.now().isoformat()
        }
        
        # Test 1: Skill Extraction
        print(f"\n[1/4] Testing Skill Extraction...")
        extraction = test_skill_extraction(test_case)
        test_result['extraction'] = extraction
        
        if extraction['success']:
            print(f"  ✓ Extracted: {extraction['extracted_skills']}")
            print(f"  Experience: {extraction['experience']} years")
            print(f"  Category: {extraction['category']}")
            
            # Calculate accuracy
            accuracy = calculate_accuracy(
                extraction['extracted_skills'],
                test_case['expected_skills']
            )
            test_result['accuracy'] = accuracy
            print(f"  Accuracy: {accuracy:.1f}%")
        else:
            print(f"  ✗ Failed: {extraction['error']}")
        
        # Test 2: Skill Normalization
        if extraction['success'] and extraction['extracted_skills']:
            print(f"\n[2/4] Testing Skill Normalization...")
            normalization = test_skill_normalization(
                test_case,
                extraction['extracted_skills']
            )
            test_result['normalization'] = normalization
            
            if normalization['success']:
                print(f"  ✓ Normalized: {normalization['normalized_skills']}")
            else:
                print(f"  ✗ Failed: {normalization['error']}")
        
        # Test 3: Job Recommendations
        skills_to_use = extraction.get('extracted_skills', [])
        if skills_to_use:
            print(f"\n[3/4] Testing Job Recommendations...")
            recommendations = test_job_recommendations(test_case, skills_to_use)
            test_result['recommendations'] = recommendations
            
            if recommendations['success']:
                print(f"  ✓ Found {recommendations['job_count']} jobs")
                print(f"  Top matches: {', '.join(recommendations['top_jobs'])}")
                print(f"  Avg match: {recommendations['avg_match']:.1f}%")
            else:
                print(f"  ✗ Failed: {recommendations['error']}")
        
        # Test 4: Complete Pipeline
        print(f"\n[4/4] Testing Complete Pipeline...")
        pipeline_result = test_complete_pipeline(test_case)
        test_result['pipeline'] = pipeline_result
        
        if pipeline_result['success']:
            print(f"  ✓ Pipeline executed successfully")
        else:
            print(f"  ✗ Failed: {pipeline_result['error']}")
        
        results.append(test_result)
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    successful_tests = sum(1 for r in results if r.get('extraction', {}).get('success', False))
    avg_accuracy = sum(r.get('accuracy', 0) for r in results) / len(results) if results else 0
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Successful: {successful_tests}/{len(results)} ({successful_tests/len(results)*100:.1f}%)")
    print(f"Average Accuracy: {avg_accuracy:.1f}%")
    
    # Language-wise breakdown
    print(f"\n📊 Language-wise Results:")
    lang_stats = {}
    for r in results:
        lang = r['test_case']['language']
        if lang not in lang_stats:
            lang_stats[lang] = {'total': 0, 'success': 0, 'accuracy': []}
        
        lang_stats[lang]['total'] += 1
        if r.get('extraction', {}).get('success', False):
            lang_stats[lang]['success'] += 1
            lang_stats[lang]['accuracy'].append(r.get('accuracy', 0))
    
    for lang, stats in lang_stats.items():
        avg_acc = sum(stats['accuracy']) / len(stats['accuracy']) if stats['accuracy'] else 0
        print(f"  {lang.capitalize()}: {stats['success']}/{stats['total']} ({avg_acc:.1f}% accuracy)")
    
    # Save results
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Convert numpy int64 to regular int for JSON serialization
    import numpy as np
    def convert_numpy(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        return obj
    
    results_cleaned = convert_numpy(results)
    
    output_file = output_dir / f"real_data_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_cleaned, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    print("="*70 + "\n")
    
    return results, avg_accuracy


def main():
    """Main function"""
    try:
        results, accuracy = run_all_tests()
        
        if accuracy >= 70:
            print("🎉 Good performance! System is working well.")
            return True
        elif accuracy >= 50:
            print("⚠ Moderate performance. Consider fine-tuning.")
            return True
        else:
            print("⚠ Low performance. Review and improve models.")
            return False
    
    except Exception as e:
        print(f"\n✗ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
