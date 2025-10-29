"""
SkillSync Master API - Complete Implementation
Features:
1. FastAPI REST API
2. Speech-to-Text (Whisper)
3. Fine-tuned Skill Extraction
4. Model Save/Load
5. Multilingual Support (English, Tamil, Hindi, Telugu, Kannada)
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import json
from pathlib import Path
import logging
import torch
from datetime import datetime
import tempfile
import os

# Import custom modules
from ml_pipeline import SkillSyncPipeline
from skill_extraction import SkillExtractor
from skill_normalization import SkillNormalizer
from job_recommender import JobRecommender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models for API
# ============================================================================

class TextInput(BaseModel):
    """Input model for text-based skill extraction"""
    text: str
    language: Optional[str] = "auto"  # auto, en, ta, hi, te, kn
    location: Optional[str] = None
    include_recommendations: bool = True


class WorkerProfile(BaseModel):
    """Worker profile input"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    text: str
    language: Optional[str] = "auto"


class SkillQuery(BaseModel):
    """Query for skill-based job search"""
    skills: List[str]
    location: Optional[str] = None
    experience_years: Optional[int] = 0
    top_k: int = 10


class LearningQuery(BaseModel):
    """Query for learning recommendations"""
    current_skills: List[str]
    target_skills: Optional[List[str]] = None
    language: Optional[str] = None
    top_k: int = 5


# ============================================================================
# Initialize FastAPI App
# ============================================================================

app = FastAPI(
    title="SkillSync ML API",
    description="AI-powered skill extraction and job recommendation for informal workers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Global ML Pipeline Instance
# ============================================================================

# Initialize with lazy loading
pipeline = None
voice_pipeline = None

def get_pipeline(use_whisper: bool = False):
    """Get or initialize the ML pipeline"""
    global pipeline, voice_pipeline
    
    if use_whisper:
        if voice_pipeline is None:
            logger.info("Initializing Voice-First Pipeline...")
            voice_pipeline = SkillSyncPipeline(use_whisper=True)
            logger.info("✓ Voice pipeline ready")
        return voice_pipeline
    else:
        if pipeline is None:
            logger.info("Initializing ML Pipeline...")
            pipeline = SkillSyncPipeline(use_whisper=False)
            logger.info("✓ Pipeline ready")
        return pipeline


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "SkillSync ML API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "extract_skills": "/api/extract-skills (POST)",
            "extract_from_audio": "/api/extract-from-audio (POST)",
            "create_profile": "/api/create-profile (POST)",
            "recommend_jobs": "/api/recommend-jobs (POST)",
            "recommend_learning": "/api/recommend-learning (POST)",
            "skill_gap": "/api/skill-gap (POST)",
            "health": "/health (GET)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "pipeline_loaded": pipeline is not None,
        "whisper_loaded": whisper_model is not None
    }


@app.post("/api/extract-skills")
async def extract_skills(input_data: TextInput):
    """
    Extract skills from text input
    
    Supports multilingual input (English, Tamil, Hindi, Telugu, Kannada)
    """
    try:
        logger.info(f"Processing text input: {input_data.text[:50]}...")
        
        pipe = get_pipeline()
        
        # Process through pipeline
        result = pipe.process_text_input(input_data.text)
        
        # Add language detection
        result['detected_language'] = detect_language(input_data.text)
        
        # Filter recommendations by location if provided
        if input_data.location and input_data.include_recommendations:
            result['job_recommendations'] = [
                job for job in result['job_recommendations']
                if input_data.location.lower() in job['location'].lower()
            ][:5]
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in extract_skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/process")
@app.post("/api/extract-from-audio")  # Alias for backward compatibility
async def process_voice_input(
    audio_file: UploadFile = File(...),
    language: Optional[str] = None
):
    """
    VOICE-FIRST PRIMARY ENDPOINT
    Process audio input through complete pipeline
    
    Voice → Speech-to-Text → Skills → Jobs → Profile
    
    Supports: mp3, wav, m4a, ogg, flac, aac
    Languages: auto-detect or specify (en, hi, ta, te, kn, etc.)
    
    Returns complete worker profile with skills and job recommendations
    """
    try:
        logger.info(f"🎙️ Voice processing request: {audio_file.filename}")
        
        # Validate file type
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']
        file_ext = Path(audio_file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Process audio through complete pipeline
            pipe = get_pipeline(use_whisper=True)
            
            logger.info("Processing audio through voice-first pipeline...")
            result = pipe.process_audio_input(tmp_path, language=language)
            
            logger.info(f"✓ Voice processing complete")
            
            return {
                "success": True,
                "data": result,
                "filename": audio_file.filename,
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        logger.error(f"Error in extract_from_audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/create-profile")
async def create_worker_profile(profile: WorkerProfile):
    """
    Create complete worker profile with skills and recommendations
    """
    try:
        logger.info(f"Creating profile for: {profile.name or 'Anonymous'}")
        
        pipe = get_pipeline()
        
        # Create profile
        worker_info = {
            'name': profile.name,
            'age': profile.age,
            'gender': profile.gender,
            'location': profile.location,
            'phone': profile.phone
        }
        
        result = pipe.create_worker_profile(
            text=profile.text,
            worker_info=worker_info
        )
        
        # Add language support
        result['language'] = profile.language or detect_language(profile.text)
        
        return {
            "success": True,
            "profile_id": f"WP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in create_worker_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommend-jobs")
async def recommend_jobs(query: SkillQuery):
    """
    Get job recommendations based on skills
    """
    try:
        logger.info(f"Getting job recommendations for skills: {query.skills}")
        
        pipe = get_pipeline()
        
        jobs = pipe.job_recommender.recommend_jobs(
            worker_skills=query.skills,
            location=query.location,
            top_k=query.top_k
        )
        
        return {
            "success": True,
            "query": {
                "skills": query.skills,
                "location": query.location,
                "experience_years": query.experience_years
            },
            "results": jobs,
            "count": len(jobs),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in recommend_jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommend-learning")
async def recommend_learning(query: LearningQuery):
    """
    Get learning resource recommendations
    """
    try:
        logger.info(f"Getting learning recommendations for: {query.current_skills}")
        
        pipe = get_pipeline()
        
        resources = pipe.job_recommender.recommend_learning(
            worker_skills=query.current_skills,
            target_skills=query.target_skills,
            top_k=query.top_k
        )
        
        # Filter by language if specified
        if query.language:
            resources = [
                r for r in resources
                if query.language.lower() in r['language'].lower()
            ]
        
        return {
            "success": True,
            "query": {
                "current_skills": query.current_skills,
                "target_skills": query.target_skills,
                "language": query.language
            },
            "results": resources,
            "count": len(resources),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in recommend_learning: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/skill-gap")
async def analyze_skill_gap(data: dict):
    """
    Analyze skill gap between current skills and target job
    """
    try:
        worker_skills = data.get('worker_skills', [])
        target_job = data.get('target_job', '')
        
        logger.info(f"Analyzing skill gap for job: {target_job}")
        
        pipe = get_pipeline()
        
        gap_analysis = pipe.job_recommender.get_skill_gap_analysis(
            worker_skills=worker_skills,
            target_job_title=target_job
        )
        
        return {
            "success": True,
            "analysis": gap_analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in analyze_skill_gap: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Utility Functions
# ============================================================================

def detect_language(text: str) -> str:
    """
    Detect language from text (simple rule-based)
    """
    # Tamil unicode range
    if any('\u0B80' <= char <= '\u0BFF' for char in text):
        return 'tamil'
    
    # Hindi/Devanagari unicode range
    if any('\u0900' <= char <= '\u097F' for char in text):
        return 'hindi'
    
    # Telugu unicode range
    if any('\u0C00' <= char <= '\u0C7F' for char in text):
        return 'telugu'
    
    # Kannada unicode range
    if any('\u0C80' <= char <= '\u0CFF' for char in text):
        return 'kannada'
    
    return 'english'


# ============================================================================
# Model Management Endpoints
# ============================================================================

@app.post("/api/models/save")
async def save_models(background_tasks: BackgroundTasks):
    """
    Save trained models to disk
    """
    try:
        pipe = get_pipeline()
        
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        # Save in background
        background_tasks.add_task(save_models_task, pipe)
        
        return {
            "success": True,
            "message": "Model saving initiated",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error saving models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def save_models_task(pipeline):
    """Background task to save models"""
    try:
        logger.info("Saving models...")
        
        # Save skill embeddings
        pipeline.skill_normalizer.save_embeddings("models/skill_embeddings.pkl")
        
        # Save job recommender
        pipeline.job_recommender.save_model("models/job_recommender.pkl")
        
        logger.info("✓ Models saved successfully")
    except Exception as e:
        logger.error(f"Error in save_models_task: {str(e)}")


@app.get("/api/models/info")
async def model_info():
    """
    Get information about loaded models
    """
    pipe = get_pipeline() if pipeline else None
    
    return {
        "models": {
            "skill_extraction": {
                "type": "Rule-based + spaCy",
                "loaded": pipe is not None
            },
            "skill_normalization": {
                "type": "Sentence-BERT",
                "model": "all-MiniLM-L6-v2",
                "loaded": pipe is not None
            },
            "job_recommendation": {
                "type": "TF-IDF + Cosine Similarity",
                "loaded": pipe is not None
            },
            "speech_to_text": {
                "type": "Whisper",
                "model": "base",
                "loaded": whisper_model is not None
            }
        },
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Startup and Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("=" * 70)
    logger.info("SkillSync ML API Starting...")
    logger.info("=" * 70)
    
    # Pre-load pipeline (optional)
    # get_pipeline()
    
    logger.info("✓ API Ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down API...")
    # Add cleanup code here if needed


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SkillSync ML API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("SkillSync ML API Server")
    print("=" * 70)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"API Docs: http://{args.host}:{args.port}/docs")
    print(f"OpenAPI: http://{args.host}:{args.port}/redoc")
    print("=" * 70 + "\n")
    
    uvicorn.run(
        "master_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
