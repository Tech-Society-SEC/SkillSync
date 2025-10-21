"""
Audio Processor - Whisper-based Speech-to-Text
Primary input method for SkillSync (Voice-First System)
"""

import whisper
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List, Union
import tempfile
import os
import logging

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Voice-to-Text processor using OpenAI Whisper
    Supports multiple languages and audio formats
    """
    
    def __init__(
        self, 
        model_size: str = "base",
        device: Optional[str] = None,
        language: Optional[str] = None
    ):
        """
        Initialize Whisper audio processor
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to use (cuda/cpu), auto-detected if None
            language: Target language code (en, hi, ta, te, kn, etc.)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_size = model_size
        self.language = language
        
        logger.info(f"🎙️ Initializing AudioProcessor...")
        logger.info(f"  Model: Whisper {model_size}")
        logger.info(f"  Device: {self.device}")
        logger.info(f"  Language: {language or 'auto-detect'}")
        
        # Load Whisper model
        try:
            self.model = whisper.load_model(model_size, device=self.device)
            logger.info(f"✓ Whisper {model_size} loaded successfully")
        except Exception as e:
            logger.error(f"✗ Failed to load Whisper model: {e}")
            raise
        
        # Supported audio formats
        self.supported_formats = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma']
        
        # Language mapping (ISO 639-1 to full name)
        self.language_map = {
            'en': 'english',
            'hi': 'hindi',
            'ta': 'tamil',
            'te': 'telugu',
            'kn': 'kannada',
            'mr': 'marathi',
            'bn': 'bengali',
            'gu': 'gujarati',
            'ml': 'malayalam',
            'pa': 'punjabi'
        }
    
    def transcribe_audio(
        self, 
        audio_path: Union[str, Path],
        language: Optional[str] = None,
        task: str = "transcribe",
        **kwargs
    ) -> Dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (overrides default)
            task: 'transcribe' or 'translate' (to English)
            **kwargs: Additional Whisper parameters
            
        Returns:
            Dictionary with transcription results
        """
        audio_path = Path(audio_path)
        
        # Validate file
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if audio_path.suffix.lower() not in self.supported_formats:
            raise ValueError(
                f"Unsupported format: {audio_path.suffix}. "
                f"Supported: {', '.join(self.supported_formats)}"
            )
        
        logger.info(f"🎤 Transcribing: {audio_path.name}")
        
        # Convert to WAV if needed
        audio_path = self._preprocess_audio(audio_path)
        
        # Transcribe
        target_language = language or self.language
        
        try:
            result = self.model.transcribe(
                str(audio_path),
                language=target_language,
                task=task,
                **kwargs
            )
            
            # Extract segments with timestamps
            segments = []
            if 'segments' in result:
                for seg in result['segments']:
                    segments.append({
                        'start': seg['start'],
                        'end': seg['end'],
                        'text': seg['text'].strip(),
                        'confidence': seg.get('no_speech_prob', 0.0)
                    })
            
            transcription_result = {
                'text': result['text'].strip(),
                'language': result.get('language', target_language or 'unknown'),
                'segments': segments,
                'duration': self._get_audio_duration(audio_path),
                'model': self.model_size,
                'success': True
            }
            
            logger.info(f"✓ Transcription complete")
            logger.info(f"  Language: {transcription_result['language']}")
            logger.info(f"  Duration: {transcription_result['duration']:.2f}s")
            logger.info(f"  Text: {transcription_result['text'][:100]}...")
            
            return transcription_result
        
        except Exception as e:
            logger.error(f"✗ Transcription failed: {e}")
            return {
                'text': '',
                'language': 'unknown',
                'segments': [],
                'duration': 0,
                'model': self.model_size,
                'success': False,
                'error': str(e)
            }
    
    def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        format: str = 'wav',
        **kwargs
    ) -> Dict:
        """
        Transcribe audio from bytes (for API uploads)
        
        Args:
            audio_bytes: Audio file bytes
            format: Audio format (wav, mp3, etc.)
            **kwargs: Additional parameters
            
        Returns:
            Transcription result dictionary
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        try:
            result = self.transcribe_audio(tmp_path, **kwargs)
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        return result
    
    def _preprocess_audio(self, audio_path: Path) -> Path:
        """
        Convert audio to format suitable for Whisper
        
        Args:
            audio_path: Input audio path
            
        Returns:
            Path to processed audio (WAV format)
        """
        # If already WAV, return as is
        if audio_path.suffix.lower() == '.wav':
            return audio_path
        
        # Convert using pydub if available
        if PYDUB_AVAILABLE:
            try:
                logger.info(f"  Converting {audio_path.suffix} to WAV...")
                audio = AudioSegment.from_file(str(audio_path))
                
                # Create temp WAV file
                wav_path = audio_path.with_suffix('.wav')
                audio.export(str(wav_path), format='wav')
                
                logger.info(f"  ✓ Converted to WAV")
                return wav_path
            
            except Exception as e:
                logger.warning(f"  Conversion failed: {e}, using original file")
                return audio_path
        
        # Return original if pydub not available
        logger.warning("  pydub not available, using original format")
        return audio_path
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds"""
        try:
            if SOUNDFILE_AVAILABLE:
                info = sf.info(str(audio_path))
                return info.duration
            elif PYDUB_AVAILABLE:
                audio = AudioSegment.from_file(str(audio_path))
                return len(audio) / 1000.0
            else:
                return 0.0
        except:
            return 0.0
    
    def detect_language(self, audio_path: Union[str, Path]) -> str:
        """
        Detect language from audio
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Language code
        """
        audio_path = Path(audio_path)
        
        # Load and preprocess audio
        audio = whisper.load_audio(str(audio_path))
        audio = whisper.pad_or_trim(audio)
        
        # Make log-Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(self.device)
        
        # Detect language
        _, probs = self.model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        confidence = probs[detected_language]
        
        logger.info(f"🌍 Detected language: {detected_language} ({confidence:.2%} confidence)")
        
        return detected_language
    
    def batch_transcribe(
        self, 
        audio_paths: List[Union[str, Path]],
        **kwargs
    ) -> List[Dict]:
        """
        Transcribe multiple audio files
        
        Args:
            audio_paths: List of audio file paths
            **kwargs: Additional parameters
            
        Returns:
            List of transcription results
        """
        results = []
        
        logger.info(f"🎙️ Batch transcription: {len(audio_paths)} files")
        
        for i, audio_path in enumerate(audio_paths, 1):
            logger.info(f"\n[{i}/{len(audio_paths)}] Processing {Path(audio_path).name}")
            result = self.transcribe_audio(audio_path, **kwargs)
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        logger.info(f"\n✓ Batch complete: {successful}/{len(results)} successful")
        
        return results
    
    @staticmethod
    def get_model_info(model_size: str = "base") -> Dict:
        """
        Get information about Whisper model
        
        Args:
            model_size: Model size to query
            
        Returns:
            Model information dictionary
        """
        model_info = {
            'tiny': {
                'parameters': '39M',
                'size': '~75 MB',
                'speed': 'Fastest',
                'accuracy': 'Lower',
                'use_case': 'Quick testing, resource-constrained'
            },
            'base': {
                'parameters': '74M',
                'size': '~140 MB',
                'speed': 'Fast',
                'accuracy': 'Good',
                'use_case': 'Production (recommended)'
            },
            'small': {
                'parameters': '244M',
                'size': '~460 MB',
                'speed': 'Moderate',
                'accuracy': 'Better',
                'use_case': 'High-quality transcription'
            },
            'medium': {
                'parameters': '769M',
                'size': '~1.5 GB',
                'speed': 'Slow',
                'accuracy': 'High',
                'use_case': 'Best quality, research'
            },
            'large': {
                'parameters': '1550M',
                'size': '~3 GB',
                'speed': 'Very Slow',
                'accuracy': 'Highest',
                'use_case': 'Professional transcription'
            }
        }
        
        return model_info.get(model_size, model_info['base'])


# Convenience function for quick usage
def transcribe(audio_path: Union[str, Path], model_size: str = "base", **kwargs) -> str:
    """
    Quick transcription function
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size
        **kwargs: Additional parameters
        
    Returns:
        Transcribed text
    """
    processor = AudioProcessor(model_size=model_size)
    result = processor.transcribe_audio(audio_path, **kwargs)
    return result['text']


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎙️ SkillSync Audio Processor - Demo")
    print("="*70)
    
    # Initialize processor
    processor = AudioProcessor(model_size="base")
    
    print("\n📊 Model Information:")
    info = AudioProcessor.get_model_info("base")
    for key, value in info.items():
        print(f"  {key.capitalize()}: {value}")
    
    print("\n✅ Audio processor ready for use!")
    print("\nUsage:")
    print("  from audio_processor import AudioProcessor")
    print("  processor = AudioProcessor()")
    print("  result = processor.transcribe_audio('worker_audio.mp3')")
    print("  print(result['text'])")
    
    print("\n" + "="*70)
