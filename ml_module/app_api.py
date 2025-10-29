"""
SkillSync Complete Application API
FastAPI backend with voice processing, database, and analytics
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import os
from pathlib import Path
from datetime import datetime
import json

# Import ML pipeline and database
from ml_pipeline import SkillSyncPipeline
from database import SkillSyncDB

# Initialize FastAPI app
app = FastAPI(
    title="SkillSync Voice-First API",
    description="Complete API for voice-based skill profiling and job matching",
    version="2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML pipeline and database
pipeline = None
db = None

@app.on_event("startup")
async def startup_event():
    """Initialize ML pipeline and database on startup"""
    global pipeline, db
    
    print("\n" + "="*70)
    print("🚀 SkillSync Application API - Starting...")
    print("="*70)
    
    # Initialize database
    db = SkillSyncDB("skillsync_app.db")
    print("✓ Database initialized")
    
    # Initialize ML pipeline
    pipeline = SkillSyncPipeline(use_whisper=True)
    print("✓ ML Pipeline initialized")
    
    # Create upload directory
    Path("uploads").mkdir(exist_ok=True)
    Path("profiles").mkdir(exist_ok=True)
    
    print("="*70)
    print("✅ API Ready!")
    print("="*70 + "\n")


# ==================== PYDANTIC MODELS ====================

class WorkerProfileCreate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class JobApplication(BaseModel):
    worker_id: str
    job_id: str
    job_title: str
    match_score: float

class LearningResource(BaseModel):
    worker_id: str
    resource_id: str
    title: str
    url: str

class AnalyticsQuery(BaseModel):
    worker_id: Optional[str] = None
    event_type: Optional[str] = None
    limit: int = 100


# ==================== VOICE PROCESSING ENDPOINTS ====================

@app.post("/api/voice/process")
async def process_voice_input(
    audio_file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    """
    Process voice input and create worker profile
    
    - **audio_file**: Audio file (MP3, WAV, M4A)
    - **name**: Worker name (optional)
    - **phone**: Phone number (optional)
    - **location**: Location (optional)
    """
    try:
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = audio_file.filename.split('.')[-1]
        audio_path = f"uploads/audio_{timestamp}.{file_extension}"
        
        with open(audio_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        print(f"📁 Saved audio: {audio_path}")
        
        # Process audio through ML pipeline
        result = pipeline.process_audio_input(audio_path)
        
        # Create worker profile in database
        profile_data = {
            'name': name,
            'phone': phone,
            'location': location,
            'language': result['transcription']['language'],
            'job_title': result['extracted_info']['job_title'],
            'experience_years': result['extracted_info']['experience_years'],
            'skills': result['extracted_info']['normalized_skills'],
            'audio_file_path': audio_path,
            'transcription': result['transcription']['text']
        }
        
        worker_id = db.create_worker_profile(profile_data)
        
        # Add job recommendations to database
        for job in result['job_recommendations'][:5]:
            db.apply_for_job(worker_id, {
                'job_id': job.get('job_id', f"JOB_{job['job_title'][:10]}"),
                'job_title': job['job_title'],
                'match_score': job['match_percentage']
            })
        
        # Add learning resources
        for resource in result['learning_resources'][:3]:
            db.add_learning_resource(worker_id, {
                'resource_id': f"RES_{resource['title'][:10]}",
                'title': resource['title'],
                'url': resource.get('url', '#')
            })
        
        return {
            "success": True,
            "worker_id": worker_id,
            "profile": profile_data,
            "transcription": result['transcription'],
            "extracted_info": result['extracted_info'],
            "job_recommendations": result['job_recommendations'][:5],
            "learning_resources": result['learning_resources'][:3],
            "message": "Profile created successfully!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/text/process")
async def process_text_input(
    text: str = Form(...),
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    """
    Process text input and create worker profile
    
    - **text**: Worker's skill description
    - **name**: Worker name (optional)
    - **phone**: Phone number (optional)
    - **location**: Location (optional)
    """
    try:
        # Process text through ML pipeline
        result = pipeline.process_text_input(text)
        
        # Create worker profile in database
        profile_data = {
            'name': name,
            'phone': phone,
            'location': location,
            'language': 'unknown',
            'job_title': result['extracted_info']['job_title'],
            'experience_years': result['extracted_info']['experience_years'],
            'skills': result['extracted_info']['normalized_skills'],
            'transcription': text
        }
        
        worker_id = db.create_worker_profile(profile_data)
        
        return {
            "success": True,
            "worker_id": worker_id,
            "profile": profile_data,
            "extracted_info": result['extracted_info'],
            "job_recommendations": result['job_recommendations'][:5],
            "learning_resources": result['learning_resources'][:3]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WORKER PROFILE ENDPOINTS ====================

@app.get("/api/workers/{worker_id}")
async def get_worker_profile(worker_id: str):
    """Get worker profile by ID"""
    profile = db.get_worker_profile(worker_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Get applications and learning progress
    applications = db.get_worker_applications(worker_id)
    learning = db.get_worker_learning(worker_id)
    
    return {
        "success": True,
        "profile": profile,
        "applications": applications,
        "learning_progress": learning
    }


@app.put("/api/workers/{worker_id}")
async def update_worker_profile(worker_id: str, updates: Dict):
    """Update worker profile"""
    try:
        db.update_worker_profile(worker_id, updates)
        return {"success": True, "message": "Profile updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workers/search")
async def search_workers(
    job_title: Optional[str] = None,
    location: Optional[str] = None,
    min_experience: Optional[int] = None
):
    """Search workers by filters"""
    filters = {}
    if job_title:
        filters['job_title'] = job_title
    if location:
        filters['location'] = location
    if min_experience:
        filters['min_experience'] = min_experience
    
    workers = db.search_workers(filters)
    
    return {
        "success": True,
        "count": len(workers),
        "workers": workers
    }


# ==================== JOB APPLICATION ENDPOINTS ====================

@app.post("/api/jobs/apply")
async def apply_for_job(application: JobApplication):
    """Apply for a job"""
    try:
        app_id = db.apply_for_job(application.worker_id, application.dict())
        return {
            "success": True,
            "application_id": app_id,
            "message": "Application submitted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workers/{worker_id}/applications")
async def get_worker_applications(worker_id: str):
    """Get all applications for a worker"""
    applications = db.get_worker_applications(worker_id)
    return {
        "success": True,
        "count": len(applications),
        "applications": applications
    }


@app.put("/api/applications/{application_id}/status")
async def update_application_status(application_id: int, status: str):
    """Update application status"""
    try:
        db.update_application_status(application_id, status)
        return {"success": True, "message": "Status updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LEARNING ENDPOINTS ====================

@app.post("/api/learning/add")
async def add_learning_resource(resource: LearningResource):
    """Add learning resource for worker"""
    try:
        resource_id = db.add_learning_resource(resource.worker_id, resource.dict())
        return {
            "success": True,
            "resource_id": resource_id,
            "message": "Resource added"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workers/{worker_id}/learning")
async def get_worker_learning(worker_id: str):
    """Get learning resources for worker"""
    learning = db.get_worker_learning(worker_id)
    return {
        "success": True,
        "count": len(learning),
        "resources": learning
    }


@app.put("/api/learning/{resource_id}/progress")
async def update_learning_progress(resource_id: int, progress: int, status: Optional[str] = None):
    """Update learning progress"""
    try:
        db.update_learning_progress(resource_id, progress, status)
        return {"success": True, "message": "Progress updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/analytics/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    stats = db.get_dashboard_stats()
    return {
        "success": True,
        "stats": stats
    }


@app.post("/api/analytics/query")
async def query_analytics(query: AnalyticsQuery):
    """Query analytics data"""
    analytics = db.get_analytics(
        worker_id=query.worker_id,
        event_type=query.event_type,
        limit=query.limit
    )
    return {
        "success": True,
        "count": len(analytics),
        "analytics": analytics
    }


@app.post("/api/analytics/log")
async def log_analytics_event(worker_id: str, event_type: str, event_data: Dict):
    """Log custom analytics event"""
    try:
        db.log_analytics(worker_id, event_type, event_data)
        return {"success": True, "message": "Event logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== UTILITY ENDPOINTS ====================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "SkillSync Voice-First API",
        "version": "2.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_pipeline": "ready"
    }


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Starting SkillSync Application API")
    print("="*70)
    print("\n📝 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        "app_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
