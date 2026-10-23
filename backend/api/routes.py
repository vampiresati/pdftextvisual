import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from api.schemas import UploadResponse
from core.config import MAX_UPLOAD_BYTES, UPLOADS
from core.state import documents, jobs, utc_now
from jobs.worker import process_upload

router = APIRouter(prefix="/api")

@router.post("/uploads", response_model=UploadResponse, status_code=202)
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    filename = file.filename or "upload.pdf"
    if file.content_type not in {"application/pdf", "application/x-pdf"} and not filename.lower().endswith(".pdf"):
        raise HTTPException(415, "Upload a PDF file.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if not content.startswith(b"%PDF"):
        raise HTTPException(422, "The uploaded file is not a valid PDF.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"PDF is larger than {MAX_UPLOAD_BYTES // 1024 // 1024} MB.")
    document_id, job_id = uuid.uuid4().hex, uuid.uuid4().hex
    pdf_path = UPLOADS / f"{document_id}.pdf"
    pdf_path.write_bytes(content)
    documents[document_id] = {"document_id": document_id, "filename": filename, "uploaded_at": utc_now()}
    jobs[job_id] = {"job_id": job_id, "document_id": document_id, "status": "queued", "progress": 0, "current_step": "Queued", "created_at": utc_now()}
    background_tasks.add_task(process_upload, job_id, document_id, pdf_path)
    return UploadResponse(job_id=job_id, document_id=document_id, status="queued", message="PDF accepted and queued for visualization.")

@router.get("/status/{job_id}")
async def job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found.")
    return jobs[job_id]

@router.get("/documents/{document_id}")
async def document(document_id: str):
    if document_id not in documents:
        raise HTTPException(404, "Document not found.")
    item = documents[document_id].copy()
    if item.get("video_path"):
        item["video_url"] = f"/api/documents/{document_id}/video"
    return item

@router.get("/documents/{document_id}/video")
async def video(document_id: str):
    item = documents.get(document_id)
    path = Path(item["video_path"]) if item and item.get("video_path") else None
    if not path or not path.is_file():
        raise HTTPException(404, "Video is not ready.")
    return FileResponse(path, media_type="video/mp4", filename=f"{document_id}.mp4")

@router.get("/health")
async def health():
    return {"status": "healthy", "renderer": "manim" if shutil.which("manim") else "missing"}
