from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import time
import random
import string

app = FastAPI(title="Sonia Video API")

# Clé API (à configurer via variable d'environnement)
import os
API_KEY = os.getenv("SONIA_VIDEO_API_KEY", "")

# Stockage en mémoire des vidéos (simulé)
videos_db = {}

class GenerateVideoRequest(BaseModel):
    prompt: str
    duration: int  # 5, 10, ou 25 secondes
    quality: Optional[str] = "standard"

class VideoStatusResponse(BaseModel):
    video_id: str
    status: str
    video_url: Optional[str] = None
    detail: Optional[str] = None

def verify_api_key(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/")
def root():
    return {"message": "Sonia Video API - Ready"}

@app.post("/api/v1/videos/generate")
def generate_video(request: GenerateVideoRequest, authorization: str = Header(None)):
    verify_api_key(authorization)
    
    # Générer un ID unique
    video_id = f"mock_{int(time.time() * 1000)}_{''.join(random.choices(string.ascii_lowercase, k=9))}"
    
    # Stocker la vidéo avec statut initial
    videos_db[video_id] = {
        "video_id": video_id,
        "status": "queued",
        "video_url": None,
        "created_at": time.time(),
        "prompt": request.prompt,
        "duration": request.duration
    }
    
    return {
        "video_id": video_id,
        "status_url": f"/api/v1/videos/{video_id}/status"
    }

@app.get("/api/v1/videos/{video_id}/status")
def get_video_status(video_id: str, authorization: str = Header(None)):
    verify_api_key(authorization)
    
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = videos_db[video_id]
    elapsed = time.time() - video["created_at"]
    
    # Simulation de progression
    if elapsed < 0.5:
        video["status"] = "queued"
    elif elapsed < 3:
        video["status"] = "processing"
    else:
        video["status"] = "done"
        video["video_url"] = f"https://demo.soniavideo.fr/videos/{video_id}.mp4"
    
    return VideoStatusResponse(
        video_id=video["video_id"],
        status=video["status"],
        video_url=video.get("video_url" ),
        detail=None
    )
