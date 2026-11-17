
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import subprocess
import uuid

app = FastAPI(title="ClipForge AI")

os.makedirs("uploads", exist_ok=True)
os.makedirs("clips", exist_ok=True)

app.mount("/clips", StaticFiles(directory="clips"), name="clips")

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.post("/generate")
async def generate(video: UploadFile = File(...)):
    allowed = {".mp4", ".mov", ".mkv", ".webm"}
    ext = os.path.splitext(video.filename or "")[1].lower()

    if ext not in allowed:
        return {"error": "Unsupported video format"}

    job_id = uuid.uuid4().hex
    input_path = f"uploads/{job_id}{ext}"
    output_path = f"clips/{job_id}_clip.mp4"

    with open(input_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-t", "30",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-c:a", "aac",
            output_path
        ], check=True, capture_output=True)

        return {
            "message": "Your clip is ready!",
            "clip": f"/clips/{job_id}_clip.mp4"
        }
    except subprocess.CalledProcessError:
        return {"error": "Video processing failed. Check FFmpeg installation."}
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
          
