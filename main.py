from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace * with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.post("/api/thumbnail")
async def fetch_thumbnail(url: str = Form(...)):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'force_generic_extractor': False
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "thumbnail": info.get("thumbnail", ""),
                "title": info.get("title", "Unknown Title")
            }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Thumbnail fetch failed: {str(e)}"})

@app.post("/api/download")
async def download_video(url: str = Form(...), format: str = Form(...)):
    video_id = str(uuid.uuid4())
    ydl_opts = {
        "format": "bestaudio" if format == "MP3" else "best",
        "outtmpl": f"{DOWNLOAD_DIR}/{video_id}.%(ext)s",
        "quiet": True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return FileResponse(
                path=filename,
                filename=os.path.basename(filename),
                media_type="application/octet-stream"
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Download failed: {str(e)}"})
