"""
Generate Test Audio Files for Voice Accuracy Testing
Uses Google TTS to create multilingual worker audio samples
"""

from pathlib import Path
import sys

print("\n" + "="*70)
print("🎤 Generating Test Audio Files")
print("="*70)

# Check if gTTS is installed
try:
    from gtts import gTTS
    print("\n✓ gTTS library found")
except ImportError:
    print("\n✗ gTTS not installed")
    print("\nInstall it using:")
    print("  pip install gtts")
    sys.exit(1)

# Create test_audio directory
audio_dir = Path('test_audio')
audio_dir.mkdir(exist_ok=True)
print(f"✓ Directory created: {audio_dir}")

# Test audio samples (Focus on English and Hindi - most reliable)
samples = [
    # ===== ENGLISH SAMPLES =====
    {
        'lang': 'en',
        'text': 'I have 8 years experience in electrical work. I can do house wiring, fan installation, switch board repair. I also know motor winding.',
        'filename': 'electrician_en.mp3',
        'description': 'English - Electrician',
        'priority': 'high'
    },
    {
        'lang': 'en',
        'text': 'I am plumber with 5 years experience. I know pipe fitting and tap repair. I can fix all types of leakage problems.',
        'filename': 'plumber_en.mp3',
        'description': 'English - Plumber',
        'priority': 'high'
    },
    {
        'lang': 'en',
        'text': 'Mobile repair mechanic. Screen replacement, battery change, software issues all I can fix. iPhone, Samsung all brands. 4 years experience.',
        'filename': 'mobile_repair_en.mp3',
        'description': 'English - Mobile Repair',
        'priority': 'high'
    },
    {
        'lang': 'en',
        'text': 'I work as driver. I can drive car, truck, all vehicles. I have 10 years driving experience.',
        'filename': 'driver_en.mp3',
        'description': 'English - Driver',
        'priority': 'high'
    },
    {
        'lang': 'en',
        'text': 'I am carpenter. I can do wood cutting, furniture making, door fitting. 7 years experience in carpentry work.',
        'filename': 'carpenter_en.mp3',
        'description': 'English - Carpenter',
        'priority': 'high'
    },
    {
        'lang': 'en',
        'text': 'I work in beauty parlor. Hair cutting, facial treatment, makeup all I know. 3 years experience.',
        'filename': 'beautician_en.mp3',
        'description': 'English - Beautician',
        'priority': 'high'
    },
    
    # ===== HINDI SAMPLES =====
    {
        'lang': 'hi',
        'text': 'Main electrician hoon. Wiring, fan, switch board sab kaam aata hai. 8 saal ka experience hai.',
        'filename': 'electrician_hi.mp3',
        'description': 'Hindi - Electrician (Hinglish)',
        'priority': 'high'
    },
    {
        'lang': 'hi',
        'text': 'Main welding ka kaam karta hoon. Steel fabrication, gate banana sab aata hai. 7 saal ka experience.',
        'filename': 'welder_hi.mp3',
        'description': 'Hindi - Welder (Hinglish)',
        'priority': 'high'
    },
    {
        'lang': 'hi',
        'text': 'Main plumber hoon. Pipe fitting, tap repair, bathroom fitting sab kar sakta hoon. 5 saal ka experience.',
        'filename': 'plumber_hi.mp3',
        'description': 'Hindi - Plumber (Hinglish)',
        'priority': 'high'
    },
    {
        'lang': 'hi',
        'text': 'Main tailor hoon. Blouse silai, saree fall, churidar sab bana sakta hoon. 6 saal se kaam kar raha hoon.',
        'filename': 'tailor_hi.mp3',
        'description': 'Hindi - Tailor (Hinglish)',
        'priority': 'high'
    },
    {
        'lang': 'hi',
        'text': 'Mobile repair ka kaam karta hoon. Screen change, battery change, software problem sab theek kar sakta hoon.',
        'filename': 'mobile_hi.mp3',
        'description': 'Hindi - Mobile Repair (Hinglish)',
        'priority': 'high'
    },
    
    # ===== TAMIL (English script - more reliable) =====
    {
        'lang': 'en',
        'text': 'I am carpenter from Tamil Nadu. Wood cutting, furniture making, door fitting all I know. 10 years experience.',
        'filename': 'carpenter_tamil_en.mp3',
        'description': 'Tamil Worker (English)',
        'priority': 'medium'
    },
    
    # ===== KANNADA (English script - more reliable) =====
    {
        'lang': 'en',
        'text': 'I work in beauty parlor in Karnataka. Hair cut, facial, makeup all I know. 6 years experience in beauty work.',
        'filename': 'beautician_kannada_en.mp3',
        'description': 'Kannada Worker (English)',
        'priority': 'medium'
    },
]

print(f"\n📝 Generating {len(samples)} audio files...\n")

success_count = 0
failed_count = 0

for i, sample in enumerate(samples, 1):
    try:
        print(f"[{i}/{len(samples)}] {sample['description']}...")
        print(f"  Text: {sample['text'][:50]}...")
        
        # Generate audio
        tts = gTTS(text=sample['text'], lang=sample['lang'], slow=False)
        
        # Save file
        output_path = audio_dir / sample['filename']
        tts.save(str(output_path))
        
        print(f"  ✓ Saved: {output_path}")
        success_count += 1
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        failed_count += 1

print("\n" + "="*70)
print("📊 Generation Summary")
print("="*70)
print(f"✅ Successfully created: {success_count}/{len(samples)} files")
if failed_count > 0:
    print(f"❌ Failed: {failed_count} files")

print(f"\n📁 Audio files location: {audio_dir.absolute()}")

print("\n🚀 Next Steps:")
print("  1. Run voice accuracy test:")
print("     python test_voice_accuracy.py")
print("\n  2. Or test single file:")
print("     python test_voice_accuracy.py --audio test_audio/electrician_en.mp3")
print("\n  3. Or test with actual pipeline:")
print("     python -c \"")
print("     from ml_pipeline import SkillSyncPipeline")
print("     pipeline = SkillSyncPipeline(use_whisper=True)")
print("     result = pipeline.process_audio_input('test_audio/electrician_en.mp3')")
print("     print(result['transcription']['text'])")
print("     print(result['extracted_info']['normalized_skills'])")
print("     \"")

print("\n" + "="*70)
print("✅ Test audio generation complete!")
print("="*70 + "\n")
