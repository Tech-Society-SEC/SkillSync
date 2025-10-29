"""
Voice Input Testing - SkillSync Voice-First System
Test audio processing, transcription, and complete pipeline
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_audio_processor():
    """Test audio processor standalone"""
    print("\n" + "="*70)
    print("🎙️ Test 1: Audio Processor (Whisper)")
    print("="*70)
    
    try:
        from audio_processor import AudioProcessor
        
        processor = AudioProcessor(model_size="base")
        
        print("\n✓ Audio processor initialized")
        print(f"  Model: Whisper base")
        print(f"  Supported formats: {', '.join(processor.supported_formats)}")
        
        return True, processor
    
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        print("\nInstall required packages:")
        print("  pip install openai-whisper ffmpeg-python pydub")
        return False, None


def test_voice_pipeline():
    """Test complete voice-first pipeline"""
    print("\n" + "="*70)
    print("🎙️ Test 2: Voice-First ML Pipeline")
    print("="*70)
    
    try:
        from ml_pipeline import SkillSyncPipeline
        
        # Initialize with Whisper enabled
        pipeline = SkillSyncPipeline(use_whisper=True)
        
        print("\n✓ Voice-first pipeline initialized")
        print("  Ready to process audio → text → skills → jobs")
        
        return True, pipeline
    
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def create_test_audio_samples():
    """Generate information about test audio samples"""
    print("\n" + "="*70)
    print("📝 Test Audio Samples Guide")
    print("="*70)
    
    samples = [
        {
            'filename': 'worker_electrician_en.mp3',
            'content': 'I have 8 years experience in electrical work. I can do house wiring, fan installation, and switch board repair.',
            'language': 'English',
            'expected_skills': ['Electrical Wiring', 'Fan Installation', 'Switch Board Repair']
        },
        {
            'filename': 'worker_plumber_hi.mp3',
            'content': 'मैं प्लंबर हूं। मुझे पाइप फिटिंग और नल की मरम्मत का काम आता है। 5 साल का अनुभव है।',
            'language': 'Hindi',
            'expected_skills': ['Pipe Fitting', 'Tap Repair']
        },
        {
            'filename': 'worker_carpenter_ta.mp3',
            'content': 'நான் தச்சு வேலை செய்கிறேன். மரம் வெட்டுதல், பர்னிச்சர் செய்தல் தெரியும்।',
            'language': 'Tamil',
            'expected_skills': ['Wood Cutting', 'Furniture Making']
        }
    ]
    
    print("\n📁 To test voice processing, create audio files with:")
    for i, sample in enumerate(samples, 1):
        print(f"\n{i}. {sample['filename']}")
        print(f"   Language: {sample['language']}")
        print(f"   Content: {sample['content'][:50]}...")
        print(f"   Expected: {', '.join(sample['expected_skills'][:2])}")
    
    print("\n💡 How to create test audio:")
    print("  1. Use a voice recorder app on your phone")
    print("  2. Or use online text-to-speech (Google TTS, etc.)")
    print("  3. Or use: https://ttstool.com")
    print("  4. Save as MP3, WAV, or M4A")
    print("  5. Place in 'test_audio/' folder")
    
    return samples


def test_with_sample_audio(audio_path: str):
    """Test pipeline with actual audio file"""
    print("\n" + "="*70)
    print(f"🎙️ Test 3: Processing Audio File")
    print("="*70)
    print(f"File: {audio_path}")
    
    audio_path = Path(audio_path)
    
    if not audio_path.exists():
        print(f"\n✗ File not found: {audio_path}")
        print("\nCreate test audio using the guide above")
        return None
    
    try:
        from ml_pipeline import SkillSyncPipeline
        
        # Initialize pipeline
        pipeline = SkillSyncPipeline(use_whisper=True)
        
        # Process audio
        print(f"\n🎤 Processing audio...")
        result = pipeline.process_audio_input(str(audio_path))
        
        if result.get('success'):
            print("\n✅ SUCCESS! Voice Processing Complete")
            print("="*70)
            
            # Display results
            print(f"\n📝 Transcription:")
            print(f"  Text: {result['transcription']['text']}")
            print(f"  Language: {result['transcription']['language']}")
            print(f"  Duration: {result['transcription']['duration']:.2f}s")
            
            print(f"\n🔧 Extracted Skills:")
            skills = result['extracted_info']['normalized_skills']
            if skills:
                for skill in skills[:5]:
                    print(f"  • {skill}")
            else:
                print("  (No skills detected)")
            
            print(f"\n💼 Job Recommendations:")
            jobs = result['job_recommendations']
            if jobs:
                for i, job in enumerate(jobs[:3], 1):
                    print(f"  {i}. {job['job_title']} ({job['match_percentage']:.0f}% match)")
            else:
                print("  (No jobs recommended)")
            
            print(f"\n⏱️ Total Processing Time: {result['processing_time']:.2f}s")
            
            # Save results
            output_dir = Path("outputs/voice_tests")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"voice_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved: {output_file}")
            
            return result
        else:
            print(f"\n✗ Processing failed: {result.get('error')}")
            return None
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def interactive_voice_test():
    """Interactive voice testing session"""
    print("\n" + "="*70)
    print("🎙️ Interactive Voice Testing")
    print("="*70)
    
    print("\nThis will test the voice-first processing pipeline.")
    print("You need audio files (MP3, WAV, M4A, etc.) to test with.")
    
    # Check if test_audio folder exists
    test_audio_dir = Path("test_audio")
    
    if test_audio_dir.exists():
        audio_files = list(test_audio_dir.glob("*.*"))
        audio_files = [f for f in audio_files if f.suffix.lower() in ['.mp3', '.wav', '.m4a', '.ogg']]
        
        if audio_files:
            print(f"\n✓ Found {len(audio_files)} audio files in test_audio/")
            for i, f in enumerate(audio_files, 1):
                print(f"  {i}. {f.name}")
            
            choice = input("\nSelect file number to test (or 'q' to skip): ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(audio_files):
                selected_file = audio_files[int(choice) - 1]
                test_with_sample_audio(str(selected_file))
                return True
    
    print("\n📁 No audio files found in test_audio/")
    print("   Create the folder and add some audio files to test.")
    
    # Ask for manual path
    manual_path = input("\nEnter audio file path (or press Enter to skip): ").strip()
    
    if manual_path and Path(manual_path).exists():
        test_with_sample_audio(manual_path)
        return True
    
    return False


def generate_usage_guide():
    """Generate usage examples"""
    print("\n" + "="*70)
    print("📚 Voice-First API Usage Guide")
    print("="*70)
    
    print("\n1️⃣ Python API Usage:")
    print("""
from ml_pipeline import SkillSyncPipeline

# Initialize voice-first pipeline
pipeline = SkillSyncPipeline(use_whisper=True)

# Process audio file
result = pipeline.process_audio_input("worker_audio.mp3")

# Access results
print("Transcription:", result['transcription']['text'])
print("Skills:", result['extracted_info']['normalized_skills'])
print("Jobs:", result['job_recommendations'][:3])
    """)
    
    print("\n2️⃣ REST API Usage:")
    print("""
import requests

# Upload audio file
with open('worker_audio.mp3', 'rb') as f:
    files = {'audio': f}
    response = requests.post(
        'http://localhost:8000/api/voice/process',
        files=files
    )

result = response.json()
print(result['data'])
    """)
    
    print("\n3️⃣ Supported Audio Formats:")
    print("  ✓ MP3 (.mp3)")
    print("  ✓ WAV (.wav)")
    print("  ✓ M4A (.m4a)")
    print("  ✓ OGG (.ogg)")
    print("  ✓ FLAC (.flac)")
    print("  ✓ AAC (.aac)")
    
    print("\n4️⃣ Supported Languages:")
    print("  ✓ English")
    print("  ✓ Hindi (हिंदी)")
    print("  ✓ Tamil (தமிழ்)")
    print("  ✓ Telugu (తెలుగు)")
    print("  ✓ Kannada (ಕನ್ನಡ)")
    print("  ✓ 90+ other languages")


def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("🎙️ SkillSync Voice-First Testing System")
    print("="*70)
    print("\nThis will test the voice processing capabilities")
    print("Voice → Speech-to-Text → Skills → Jobs")
    
    # Test 1: Audio Processor
    success1, processor = test_audio_processor()
    
    if not success1:
        print("\n" + "="*70)
        print("⚠️ Audio processing not available")
        print("="*70)
        print("\nTo enable voice processing, run:")
        print("  pip install openai-whisper ffmpeg-python pydub soundfile")
        print("\nNote: Also requires FFmpeg installed on system")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  Or use: choco install ffmpeg")
        return False
    
    # Test 2: Voice Pipeline
    success2, pipeline = test_voice_pipeline()
    
    if not success2:
        print("\n⚠️ Pipeline initialization failed")
        return False
    
    # Test 3: Create guide for test samples
    samples = create_test_audio_samples()
    
    # Test 4: Interactive testing
    print("\n" + "="*70)
    
    response = input("\nRun interactive voice test? (y/n): ").strip().lower()
    
    if response == 'y':
        interactive_voice_test()
    
    # Display usage guide
    generate_usage_guide()
    
    # Summary
    print("\n" + "="*70)
    print("✅ Voice System Status")
    print("="*70)
    print(f"  Audio Processor: {'✓ Ready' if success1 else '✗ Not available'}")
    print(f"  Voice Pipeline: {'✓ Ready' if success2 else '✗ Not available'}")
    print(f"  Whisper Model: base (140MB)")
    print(f"  Languages: 90+ supported")
    
    print("\n🚀 Next Steps:")
    print("  1. Create test_audio/ folder")
    print("  2. Add audio samples (worker recordings)")
    print("  3. Run: python test_voice_input.py")
    print("  4. Or start API: python master_api.py")
    print("  5. Upload audio via /api/voice/process")
    
    print("\n" + "="*70)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
