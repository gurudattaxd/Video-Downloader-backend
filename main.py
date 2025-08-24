from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from video_utils import download_and_trim
import os
import uvicorn
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video Downloader & Trimmer API",
    description="API for downloading and trimming videos from various platforms",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

OUTPUT_DIR = "downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "Video Downloader API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "output_dir_exists": os.path.exists(OUTPUT_DIR),
        "output_dir_writable": os.access(OUTPUT_DIR, os.W_OK)
    }


@app.post("/download")
async def download_video(
    url: str = Form(..., description="Video URL to download"),
    quality: str = Form(default="720p", description="Video quality (720p, 1080p, 4k, audio)"),
    start: float = Form(None, description="Start time in seconds for trimming"),
    end: float = Form(None, description="End time in seconds for trimming")
):
    try:
        logger.info(f"Download request: URL={url}, Quality={quality}")

        if not url or not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL provided")

        filename = download_and_trim(url, start, end, OUTPUT_DIR, quality)

        if not filename or not os.path.exists(filename):
            raise HTTPException(status_code=500, detail="Failed to download video")

        file_size = os.path.getsize(filename)
        logger.info(f"Download successful: {filename} ({file_size} bytes)")

        return FileResponse(
            path=filename,
            media_type='video/mp4' if quality != 'audio' else 'audio/mpeg',
            filename=os.path.basename(filename),
            headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(filename)}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return JSONResponse(
            content={"error": f"Download failed: {str(e)}"},
            status_code=400
        )


@app.post("/info")
async def get_video_info(url: str = Form(...)):
    try:
        return JSONResponse(content={
            "url": url,
            "message": "Video info endpoint - implement as needed"
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


@app.get("/cleanup")
async def cleanup_downloads():
    try:
        files_removed = 0
        for filename in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                files_removed += 1
        return {"message": f"Cleaned up {files_removed} files"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(content={"error": "Internal server error"}, status_code=500)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", access_log=True)
