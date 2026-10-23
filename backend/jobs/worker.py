import asyncio
from pathlib import Path

from core.state import documents, update_job, utc_now
from services.pdf_parser import extract_document
from services.video_renderer import render_video


def text_to_beats(text: str) -> list[str]:
    """Turn prose into a small set of readable visual beats."""
    chunks = [" ".join(part.split()) for part in text.replace("!", ".").replace("?", ".").split(".")]
    beats = [chunk[:150].rstrip(" ,;:") for chunk in chunks if len(chunk) > 8]
    return (beats or [text[:150]])[:4]

async def process_upload(job_id: str, document_id: str, pdf_path: Path, narration: bool = True) -> None:
    try:
        update_job(job_id, status="processing", progress=12, current_step="Reading PDF")
        title, beats, page_count = await asyncio.to_thread(extract_document, pdf_path)
        documents[document_id].update(title=title, beats=beats, page_count=page_count)
        update_job(job_id, progress=42, current_step="Planning visual explanation")
        update_job(job_id, progress=65, current_step="Creating narration" if narration else "Rendering video")
        video_path, narration_ready = await render_video(document_id, title, beats, narration_text=". ".join([title, *beats]) if narration else None)
        documents[document_id].update(video_path=str(video_path), narration_ready=narration_ready)
        update_job(job_id, status="completed", progress=100, current_step="Video ready", completed_at=utc_now())
    except Exception as exc:
        update_job(job_id, status="failed", progress=100, error=str(exc), current_step="Processing failed")


async def process_text(job_id: str, document_id: str, text: str, requested_title: str | None, narration: bool) -> None:
    try:
        update_job(job_id, status="processing", progress=15, current_step="Reading your text")
        beats = text_to_beats(text)
        title = (requested_title or beats[0]).strip()[:100]
        documents[document_id].update(title=title, beats=beats, page_count=None)
        update_job(job_id, progress=42, current_step="Planning visual explanation")
        update_job(job_id, progress=64, current_step="Creating narration" if narration else "Rendering video")
        video_path, narration_ready = await render_video(document_id, title, beats, narration_text=text if narration else None)
        documents[document_id].update(video_path=str(video_path), narration_ready=narration_ready)
        update_job(job_id, status="completed", progress=100, current_step="Video ready", completed_at=utc_now())
    except Exception as exc:
        update_job(job_id, status="failed", progress=100, error=str(exc), current_step="Processing failed")
