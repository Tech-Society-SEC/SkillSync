"""
Download and verify all required ML models
Handles network issues and provides progress tracking
"""

import sys
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def download_spacy_model():
    """Download spaCy English model"""
    print("\n" + "="*70)
    print("📥 Downloading spaCy Model")
    print("="*70)
    
    try:
        import spacy
        
        # Check if already installed
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy model 'en_core_web_sm' already installed")
            return True
        except OSError:
            print("⚠ spaCy model not found. Downloading...")
            
            # Download
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ spaCy model downloaded successfully")
                return True
            else:
                print(f"✗ Failed to download spaCy model: {result.stderr}")
                return False
    
    except ImportError:
        print("✗ spaCy not installed. Run: pip install spacy")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def download_sentence_bert():
    """Download Sentence-BERT model"""
    print("\n" + "="*70)
    print("📥 Downloading Sentence-BERT Model")
    print("="*70)
    print("Model: all-MiniLM-L6-v2 (~80MB)")
    print("This may take a few minutes depending on your connection...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Try to download with timeout handling
        print("\n⏳ Downloading... (this might take 2-5 minutes)")
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("\n✓ Sentence-BERT model downloaded successfully!")
        print(f"  Model cached at: {model._model_card_vars.get('model_name', 'cache')}")
        
        # Test the model
        print("\n🧪 Testing model...")
        embeddings = model.encode(["test sentence"])
        print(f"✓ Model working! Embedding dimension: {len(embeddings[0])}")
        
        return True
    
    except ImportError:
        print("✗ sentence-transformers not installed")
        print("  Run: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"✗ Error downloading model: {e}")
        print("\n💡 Troubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Try again later (HuggingFace might be busy)")
        print("  3. Use a VPN if connection fails")
        print("  4. Download manually from: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2")
        return False


def download_whisper(model_size="base"):
    """Download Whisper model (optional)"""
    print("\n" + "="*70)
    print(f"📥 Downloading Whisper Model ({model_size})")
    print("="*70)
    
    model_sizes = {
        "tiny": "~75MB (fastest, less accurate)",
        "base": "~140MB (balanced)",
        "small": "~460MB (better accuracy)",
        "medium": "~1.5GB (high accuracy)"
    }
    
    print(f"Selected: {model_size} - {model_sizes.get(model_size, 'unknown')}")
    
    try:
        import whisper
        
        print(f"\n⏳ Downloading Whisper {model_size} model...")
        model = whisper.load_model(model_size)
        
        print(f"✓ Whisper {model_size} model downloaded successfully!")
        
        return True
    
    except ImportError:
        print("✗ openai-whisper not installed")
        print("  Run: pip install openai-whisper")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def verify_installations():
    """Verify all models are properly installed"""
    print("\n" + "="*70)
    print("✅ Verifying All Models")
    print("="*70)
    
    results = {}
    
    # Check spaCy
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy: Working")
        results['spacy'] = True
    except:
        print("✗ spaCy: Not working")
        results['spacy'] = False
    
    # Check Sentence-BERT
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        test = model.encode(["test"])
        print("✓ Sentence-BERT: Working")
        results['sentence_bert'] = True
    except:
        print("✗ Sentence-BERT: Not working")
        results['sentence_bert'] = False
    
    # Check Whisper (optional)
    try:
        import whisper
        model = whisper.load_model("base")
        print("✓ Whisper: Working")
        results['whisper'] = True
    except:
        print("⚠ Whisper: Not installed (optional)")
        results['whisper'] = False
    
    return results


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🤖 SkillSync ML Models - Download Manager")
    print("="*70)
    print("\nThis script will download all required ML models:")
    print("  1. spaCy (en_core_web_sm) - ~12MB")
    print("  2. Sentence-BERT (all-MiniLM-L6-v2) - ~80MB")
    print("  3. Whisper (base) - ~140MB [OPTIONAL]")
    print("\nTotal download: ~230MB")
    print("="*70)
    
    # Ask for confirmation
    response = input("\nProceed with downloads? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\n❌ Download cancelled")
        return
    
    results = {}
    
    # Download models
    results['spacy'] = download_spacy_model()
    results['sentence_bert'] = download_sentence_bert()
    
    # Ask about Whisper
    print("\n" + "="*70)
    response = input("Download Whisper for speech-to-text? (y/n): ").strip().lower()
    
    if response == 'y':
        results['whisper'] = download_whisper("base")
    else:
        print("⚠ Skipping Whisper (you can download later)")
        results['whisper'] = None
    
    # Verify
    print("\n" + "="*70)
    print("🔍 Running Verification Tests...")
    print("="*70)
    
    verified = verify_installations()
    
    # Summary
    print("\n" + "="*70)
    print("📊 Download Summary")
    print("="*70)
    
    for model, status in results.items():
        if status is None:
            status_icon = "⚠ SKIPPED"
        elif status:
            status_icon = "✓ SUCCESS"
        else:
            status_icon = "✗ FAILED"
        
        print(f"  {status_icon}: {model}")
    
    # Final status
    core_models = ['spacy', 'sentence_bert']
    all_core_success = all(results.get(m, False) for m in core_models)
    
    print("\n" + "="*70)
    
    if all_core_success:
        print("🎉 SUCCESS! All core models downloaded and working!")
        print("\nYou can now:")
        print("  • Run: python quick_test.py")
        print("  • Run: python run_complete_demo.py")
        print("  • Start API: python master_api.py")
    else:
        print("⚠ Some models failed to download")
        print("\nTroubleshooting:")
        print("  1. Check internet connection")
        print("  2. Try running this script again")
        print("  3. Use a VPN if network issues persist")
        print("  4. See SETUP_GUIDE.md for manual download")
    
    print("="*70 + "\n")
    
    return all_core_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
