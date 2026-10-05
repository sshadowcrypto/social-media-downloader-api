from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(
    title="Universal Social Media Media Extractor API",
    description="Extract video, audio, metadata, and clean streaming URLs from TikTok, Instagram, YouTube, etc.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Social Media Media Extractor API",
        "docs": "/docs"
    }

@app.get("/extract")
def extract_media(url: str = Query(..., description="Full URL of the video (TikTok, Instagram, YouTube, etc.)")):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': False,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise HTTPException(status_code=400, detail="Could not extract information from the provided URL.")

            # Seleciona as melhores streams diretas
            formats = info.get("formats", [])
            video_url = info.get("url")
            audio_url = None

            # Procura stream pura de áudio caso exista
            for f in formats:
                if f.get("vcodec") == "none" and f.get("acodec") != "none":
                    audio_url = f.get("url")
                    break

            return {
                "success": True,
                "platform": info.get("extractor_key"),
                "id": info.get("id"),
                "title": info.get("title"),
                "description": info.get("description"),
                "thumbnail": info.get("thumbnail"),
                "duration_seconds": info.get("duration"),
                "uploader": info.get("uploader"),
                "uploader_id": info.get("uploader_id"),
                "metrics": {
                    "views": info.get("view_count"),
                    "likes": info.get("like_count"),
                    "comments": info.get("comment_count"),
                    "shares": info.get("repost_count")
                },
                "media": {
                    "download_url": video_url,
                    "audio_url": audio_url or video_url,
                    "format_id": info.get("format_id"),
                    "resolution": f"{info.get('width')}x{info.get('height')}" if info.get("width") else None
                }
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Extraction failed: {str(e)}")
