"""
Voice Input Accuracy Testing - Multilingual
Test real audio files across English, Hindi, Tamil, Telugu, Kannada
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Test cases with expected results (Updated for English + Hindi/Hinglish)
VOICE_TEST_CASES = [
    # ===== ENGLISH TESTS =====
    {
        'id': 'EN_001',
        'language': 'English',
        'audio_file': 'test_audio/electrician_en.mp3',
        'expected_text': 'I have 8 years experience in electrical work. I can do house wiring, fan installation, switch board repair.',
        'expected_skills': ['Electrical Wiring', 'Fan Installation', 'Switch Board Repair', 'Motor Winding'],
        'expected_job': 'Electrician',
        'expected_experience': 8
    },
    {
        'id': 'EN_002',
        'language': 'English',
        'audio_file': 'test_audio/plumber_en.mp3',
        'expected_text': 'I am plumber with 5 years experience. I know pipe fitting and tap repair.',
        'expected_skills': ['Pipe Fitting', 'Tap Repair'],
        'expected_job': 'Plumber',
        'expected_experience': 5
    },
    {
        'id': 'EN_003',
        'language': 'English',
        'audio_file': 'test_audio/mobile_repair_en.mp3',
        'expected_text': 'Mobile repair mechanic. Screen replacement, battery change, software issues.',
        'expected_skills': ['Mobile Repair', 'Screen Replacement', 'Battery Replacement', 'Software Troubleshooting'],
        'expected_job': 'Mechanic',
        'expected_experience': 4
    },
    {
        'id': 'EN_004',
        'language': 'English',
        'audio_file': 'test_audio/driver_en.mp3',
        'expected_text': 'I work as driver. I can drive car, truck, all vehicles.',
        'expected_skills': ['Vehicle Driving'],
        'expected_job': 'Driver',
        'expected_experience': 10
    },
    {
        'id': 'EN_005',
        'language': 'English',
        'audio_file': 'test_audio/carpenter_en.mp3',
        'expected_text': 'I am carpenter. Wood cutting, furniture making, door fitting.',
        'expected_skills': ['Wood Cutting', 'Furniture Making', 'Door Fitting'],
        'expected_job': 'Carpenter',
        'expected_experience': 7
    },
    {
        'id': 'EN_006',
        'language': 'English',
        'audio_file': 'test_audio/beautician_en.mp3',
        'expected_text': 'I work in beauty parlor. Hair cutting, facial treatment, makeup.',
        'expected_skills': ['Hair Cutting', 'Facial Treatment', 'Makeup'],
        'expected_job': 'Beautician',
        'expected_experience': 3
    },
    
    # ===== HINDI/HINGLISH TESTS =====
    {
        'id': 'HI_001',
        'language': 'Hindi',
        'audio_file': 'test_audio/electrician_hi.mp3',
        'expected_text': 'Main electrician hoon. Wiring, fan, switch board sab kaam aata hai.',
        'expected_skills': ['Electrical Wiring', 'Fan Installation', 'Switch Board Repair'],
        'expected_job': 'Electrician',
        'expected_experience': 8
    },
    {
        'id': 'HI_002',
        'language': 'Hindi',
        'audio_file': 'test_audio/welder_hi.mp3',
        'expected_text': 'Main welding ka kaam karta hoon. Steel fabrication, gate banana sab aata hai.',
        'expected_skills': ['Arc Welding', 'Steel Fabrication', 'Gate Making'],
        'expected_job': 'Welder',
        'expected_experience': 7
    },
    {
        'id': 'HI_003',
        'language': 'Hindi',
        'audio_file': 'test_audio/plumber_hi.mp3',
        'expected_text': 'Main plumber hoon. Pipe fitting, tap repair, bathroom fitting.',
        'expected_skills': ['Pipe Fitting', 'Tap Repair'],
        'expected_job': 'Plumber',
        'expected_experience': 5
    },
    {
        'id': 'HI_004',
        'language': 'Hindi',
        'audio_file': 'test_audio/tailor_hi.mp3',
        'expected_text': 'Main tailor hoon. Blouse silai, saree fall, churidar sab bana sakta hoon.',
        'expected_skills': ['Blouse Stitching', 'Saree Fall', 'Churidar Making'],
        'expected_job': 'Tailor',
        'expected_experience': 6
    },
    {
        'id': 'HI_005',
        'language': 'Hindi',
        'audio_file': 'test_audio/mobile_hi.mp3',
        'expected_text': 'Mobile repair ka kaam karta hoon. Screen change, battery change, software problem.',
        'expected_skills': ['Mobile Repair', 'Screen Replacement', 'Battery Replacement', 'Software Troubleshooting'],
        'expected_job': 'Mechanic',
        'expected_experience': 0
    },
    
    # ===== MULTILINGUAL (English with context) =====
    {
        'id': 'TAMIL_EN',
        'language': 'Tamil-English',
        'audio_file': 'test_audio/carpenter_tamil_en.mp3',
        'expected_text': 'I am carpenter from Tamil Nadu. Wood cutting, furniture making, door fitting.',
        'expected_skills': ['Wood Cutting', 'Furniture Making', 'Door Fitting'],
        'expected_job': 'Carpenter',
        'expected_experience': 10
    },
    {
        'id': 'KANNADA_EN',
        'language': 'Kannada-English',
        'audio_file': 'test_audio/beautician_kannada_en.mp3',
        'expected_text': 'I work in beauty parlor in Karnataka. Hair cut, facial, makeup.',
        'expected_skills': ['Hair Cutting', 'Facial Treatment', 'Makeup'],
        'expected_job': 'Beautician',
        'expected_experience': 6
    },
]


def test_voice_pipeline():
    """Test complete voice-to-profile pipeline"""
    print("\n" + "="*70)
    print("🎙️ Voice Accuracy Testing - Multilingual")
    print("="*70)
    
    try:
        from ml_pipeline import SkillSyncPipeline
        
        print("\n✓ Initializing Voice-First Pipeline...")
        pipeline = SkillSyncPipeline(use_whisper=True)
        
        return pipeline
    
    except Exception as e:
        print(f"\n✗ Failed to initialize pipeline: {e}")
        print("\nMake sure Whisper is installed:")
        print("  pip install openai-whisper ffmpeg-python pydub")
        return None


def calculate_skill_accuracy(extracted: list, expected: list) -> float:
    """Calculate accuracy of skill extraction"""
    if not expected:
        return 0.0
    
    # Count matches (case-insensitive, partial matching)
    matches = 0
    for exp_skill in expected:
        for ext_skill in extracted:
            if exp_skill.lower() in ext_skill.lower() or ext_skill.lower() in exp_skill.lower():
                matches += 1
                break
    
    accuracy = (matches / len(expected)) * 100
    return accuracy


def test_single_audio(pipeline, test_case: dict) -> dict:
    """Test a single audio file"""
    audio_path = Path(test_case['audio_file'])
    
    print(f"\n{'='*70}")
    print(f"Test: {test_case['id']} - {test_case['language']}")
    print(f"{'='*70}")
    
    # Check if file exists
    if not audio_path.exists():
        print(f"⚠️  Audio file not found: {audio_path}")
        print(f"   Expected text: {test_case['expected_text'][:60]}...")
        return {
            'test_id': test_case['id'],
            'language': test_case['language'],
            'status': 'file_not_found',
            'audio_file': str(audio_path)
        }
    
    print(f"🎤 Processing: {audio_path.name}")
    
    try:
        # Process audio through complete pipeline
        result = pipeline.process_audio_input(str(audio_path))
        
        if not result.get('success'):
            print(f"✗ Processing failed: {result.get('error')}")
            return {
                'test_id': test_case['id'],
                'language': test_case['language'],
                'status': 'processing_failed',
                'error': result.get('error')
            }
        
        # Extract results
        transcription = result['transcription']['text']
        detected_lang = result['transcription']['language']
        skills = result['extracted_info']['normalized_skills']
        job_title = result['extracted_info']['job_title']
        experience = result['extracted_info']['experience_years']
        
        # Calculate accuracies
        skill_accuracy = calculate_skill_accuracy(skills, test_case['expected_skills'])
        
        # Display results
        print(f"\n📝 Transcription:")
        print(f"   Detected Language: {detected_lang}")
        print(f"   Text: {transcription}")
        
        print(f"\n🔧 Skills Extracted:")
        print(f"   Expected: {test_case['expected_skills']}")
        print(f"   Extracted: {skills}")
        print(f"   Accuracy: {skill_accuracy:.1f}%")
        
        print(f"\n💼 Job & Experience:")
        print(f"   Expected Job: {test_case['expected_job']}")
        print(f"   Extracted Job: {job_title}")
        print(f"   Expected Experience: {test_case['expected_experience']} years")
        print(f"   Extracted Experience: {experience} years")
        
        # Overall assessment
        job_match = (job_title == test_case['expected_job'])
        exp_match = (experience == test_case['expected_experience']) if test_case['expected_experience'] > 0 else True
        
        overall_score = skill_accuracy
        if job_match:
            overall_score += 10
        if exp_match:
            overall_score += 10
        overall_score = min(100, overall_score)
        
        status_icon = "✅" if overall_score >= 70 else "⚠️" if overall_score >= 50 else "❌"
        print(f"\n{status_icon} Overall Score: {overall_score:.1f}%")
        
        return {
            'test_id': test_case['id'],
            'language': test_case['language'],
            'status': 'success',
            'transcription': transcription,
            'detected_language': detected_lang,
            'expected_skills': test_case['expected_skills'],
            'extracted_skills': skills,
            'skill_accuracy': skill_accuracy,
            'expected_job': test_case['expected_job'],
            'extracted_job': job_title,
            'job_match': job_match,
            'expected_experience': test_case['expected_experience'],
            'extracted_experience': experience,
            'experience_match': exp_match,
            'overall_score': overall_score
        }
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'test_id': test_case['id'],
            'language': test_case['language'],
            'status': 'error',
            'error': str(e)
        }


def run_all_tests():
    """Run all voice accuracy tests"""
    # Initialize pipeline
    pipeline = test_voice_pipeline()
    
    if not pipeline:
        return
    
    # Run tests
    results = []
    languages = {}
    
    for test_case in VOICE_TEST_CASES:
        result = test_single_audio(pipeline, test_case)
        results.append(result)
        
        # Track by language
        lang = result['language']
        if lang not in languages:
            languages[lang] = {'tests': [], 'scores': []}
        
        languages[lang]['tests'].append(result)
        if result['status'] == 'success':
            languages[lang]['scores'].append(result['overall_score'])
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 Test Summary")
    print(f"{'='*70}")
    
    successful = [r for r in results if r['status'] == 'success']
    not_found = [r for r in results if r['status'] == 'file_not_found']
    
    print(f"\nTotal Tests: {len(VOICE_TEST_CASES)}")
    print(f"✅ Completed: {len(successful)}/{len(VOICE_TEST_CASES)}")
    print(f"⚠️  Files Not Found: {len(not_found)}")
    
    if successful:
        avg_score = sum(r['overall_score'] for r in successful) / len(successful)
        avg_skill_acc = sum(r['skill_accuracy'] for r in successful) / len(successful)
        
        print(f"\n📈 Performance Metrics:")
        print(f"  Overall Score: {avg_score:.1f}%")
        print(f"  Skill Accuracy: {avg_skill_acc:.1f}%")
        
        # Language-wise breakdown
        print(f"\n🌍 Language-wise Results:")
        for lang, data in sorted(languages.items()):
            if data['scores']:
                lang_avg = sum(data['scores']) / len(data['scores'])
                print(f"  {lang}: {len(data['tests'])} tests, {lang_avg:.1f}% avg score")
        
        # Save results
        output_dir = Path("outputs/voice_tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"voice_accuracy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_tests': len(VOICE_TEST_CASES),
                    'completed': len(successful),
                    'average_score': avg_score if successful else 0,
                    'average_skill_accuracy': avg_skill_acc if successful else 0
                },
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved: {output_file}")
    
    # Guide for missing files
    if not_found:
        print(f"\n{'='*70}")
        print("📁 Missing Audio Files - How to Create")
        print(f"{'='*70}")
        
        print("\n1. Create 'test_audio/' folder:")
        print("   mkdir test_audio")
        
        print("\n2. Record or generate audio files:")
        for test in not_found:
            print(f"\n   {test['test_id']} ({test['language']}):")
            print(f"   File: {test['audio_file']}")
            # Find the test case
            tc = next(t for t in VOICE_TEST_CASES if t['id'] == test['test_id'])
            print(f"   Say: {tc['expected_text'][:60]}...")
        
        print("\n3. Recording options:")
        print("   • Use phone voice recorder (export as MP3)")
        print("   • Use online TTS: https://ttstool.com")
        print("   • Use Google TTS (gTTS Python library)")
        print("   • Record using Windows Sound Recorder")
        
        print("\n4. Python TTS example:")
        print("""
   from gtts import gTTS
   text = "I am electrician with 8 years experience"
   tts = gTTS(text=text, lang='en')
   tts.save('test_audio/electrician_en.mp3')
        """)
    
    print(f"\n{'='*70}")


def create_sample_audio_guide():
    """Generate a script to create sample audio files"""
    print("\n" + "="*70)
    print("🎤 Sample Audio Creation Guide")
    print("="*70)
    
    print("\nUsing Google TTS (gTTS):")
    print("\nInstall: pip install gtts\n")
    
    print("Python script to generate all test audio files:")
    print("""
from gtts import gTTS
from pathlib import Path

# Create directory
Path('test_audio').mkdir(exist_ok=True)

# Generate audio files
samples = [
    ('en', 'I have 8 years experience in electrical work. I can do house wiring, fan installation, switch board repair.', 'electrician_en.mp3'),
    ('en', 'I am plumber with 5 years experience. I know pipe fitting and tap repair.', 'plumber_en.mp3'),
    ('en', 'Mobile repair mechanic. Screen replacement, battery change, software issues all I fix.', 'mobile_repair_en.mp3'),
    ('hi', 'मैं वेल्डिंग का काम करता हूं। स्टील फैब्रिकेशन, गेट बनाना सब आता है।', 'welder_hi.mp3'),
    ('hi', 'मैं दर्जी हूं। ब्लाउज़ सिलाई, साड़ी फॉल, चूड़ीदार सब बना सकता हूं।', 'tailor_hi.mp3'),
    ('ta', 'நான் தச்சு வேலை செய்கிறேன். மரம் வெட்டுதல், பர்னிச்சர் செய்தல் தெரியும்।', 'carpenter_ta.mp3'),
    ('te', 'నేను పెయింటర్ ని. వాల్ పెయింటింగ్, రంగు మిక్సింగ్ చేయగలను.', 'painter_te.mp3'),
    ('kn', 'ನಾನು ಬ್ಯೂಟಿ ಪಾರ್ಲರ್ ನಲ್ಲಿ ಕೆಲಸ ಮಾಡುತ್ತೇನೆ. ಹೇರ್ ಕಟ್, ಫೇಶಿಯಲ್, ಮೇಕಪ್ ಎಲ್ಲಾ ತಿಳಿದಿದೆ.', 'beautician_kn.mp3'),
]

for lang, text, filename in samples:
    print(f"Generating {filename}...")
    tts = gTTS(text=text, lang=lang)
    tts.save(f'test_audio/{filename}')
    print(f"✓ {filename} created")

print("\\n✅ All audio files created!")
    """)
    
    print("\nThen run: python test_voice_accuracy.py")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Voice Accuracy Testing')
    parser.add_argument('--create-samples', action='store_true', help='Show guide to create sample audio')
    parser.add_argument('--audio', type=str, help='Test single audio file')
    
    args = parser.parse_args()
    
    if args.create_samples:
        create_sample_audio_guide()
        return
    
    if args.audio:
        # Test single file
        pipeline = test_voice_pipeline()
        if pipeline:
            test_case = {
                'id': 'CUSTOM',
                'language': 'auto',
                'audio_file': args.audio,
                'expected_text': '',
                'expected_skills': [],
                'expected_job': '',
                'expected_experience': 0
            }
            result = test_single_audio(pipeline, test_case)
            print(f"\n✓ Test complete")
    else:
        # Run all tests
        run_all_tests()


if __name__ == "__main__":
    main()
