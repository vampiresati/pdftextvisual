import asyncio
from pathlib import Path

from core.state import documents, update_job, utc_now
from services.pdf_parser import extract_document
from services.video_renderer import render_video

async def process_upload(job_id: str, document_id: str, pdf_path: Path) -> None:
    try:
        update_job(job_id, status="processing", progress=12, current_step="Reading PDF")
        title, beats, page_count = await asyncio.to_thread(extract_document, pdf_path)
        documents[document_id].update(title=title, beats=beats, page_count=page_count)
        update_job(job_id, progress=42, current_step="Planning visual explanation")
        update_job(job_id, progress=65, current_step="Rendering video")
        documents[document_id]["video_path"] = str(await render_video(document_id, title, beats))
        update_job(job_id, status="completed", progress=100, current_step="Video ready", completed_at=utc_now())
    except Exception as exc:
        update_job(job_id, status="failed", progress=100, error=str(exc), current_step="Processing failed")
