# PDFVisual

Turn an uploaded PDF into a short, shareable visual explanation.

This project reuses the useful shape of `arxivpa`: FastAPI starts an asynchronous job, the UI polls its status, and completed MP4 assets are served from the API. Unlike `arxivpa`, its input is a local PDF upload rather than an arXiv identifier.

## Run locally

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. The backend requires `manim` and its system dependencies to render the animation. Set `PDFVISUAL_MAX_UPLOAD_MB` to change the 25 MB upload limit.

## API

- `POST /api/uploads` — multipart upload with a `file` PDF field; returns a job ID.
- `GET /api/status/{job_id}` — polling status and progress.
- `GET /api/documents/{document_id}` — extracted document metadata and playable video URL.

Generated PDFs, scripts, and MP4s are held in `backend/data/`, which is intentionally ignored by Git.
