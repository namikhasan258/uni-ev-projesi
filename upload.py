# routers/upload.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from core.auth import get_current_user
from database import User
import os
import aiofiles
from cuid2 import cuid_wrapper

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 10)) * 1024 * 1024  # Increased to 10MB
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".avi"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".webm"}

cuid_generator = cuid_wrapper()


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(400, "Geçersiz dosya türü. Sadece resim dosyaları yüklenebilir.")
    
    # Read file
    contents = await file.read()
    
    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, f"Dosya boyutu {MAX_FILE_SIZE // (1024*1024)} MB'dan büyük olamaz")
    
    # Generate unique filename
    filename = f"{cuid_generator()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(contents)
    
    return {"url": f"/uploads/{filename}", "filename": file.filename}


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, "Geçersiz dosya türü. Sadece video dosyaları yüklenebilir.")
    
    # Read file
    contents = await file.read()
    
    # Validate file size (20MB for videos)
    max_video_size = 20 * 1024 * 1024
    if len(contents) > max_video_size:
        raise HTTPException(400, f"Video boyutu 20 MB'dan büyük olamaz")
    
    # Generate unique filename
    filename = f"{cuid_generator()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(contents)
    
    return {"url": f"/uploads/{filename}", "filename": file.filename}


@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(400, "Geçersiz dosya türü. Sadece ses dosyaları yüklenebilir.")
    
    # Read file
    contents = await file.read()
    
    # Validate file size (5MB for audio)
    max_audio_size = 5 * 1024 * 1024
    if len(contents) > max_audio_size:
        raise HTTPException(400, f"Ses dosyası boyutu 5 MB'dan büyük olamaz")
    
    # Generate unique filename
    filename = f"{cuid_generator()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(contents)
    
    return {"url": f"/uploads/{filename}", "filename": file.filename}
