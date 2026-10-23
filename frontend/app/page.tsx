"use client";

import { ChangeEvent, DragEvent, useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
type Job = { status: string; progress: number; current_step?: string; error?: string };
type Document = { title?: string; beats?: string[]; page_count?: number; video_url?: string; filename: string };

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string>();
  const [documentId, setDocumentId] = useState<string>();
  const [job, setJob] = useState<Job>();
  const [document, setDocument] = useState<Document>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    if (!jobId || job?.status === "completed" || job?.status === "failed") return;
    const poll = async () => {
      const response = await fetch(`${API}/api/status/${jobId}`);
      if (!response.ok) return;
      const next = await response.json(); setJob(next);
      if (next.status === "completed" && documentId) {
        const doc = await fetch(`${API}/api/documents/${documentId}`); setDocument(await doc.json());
      }
    };
    poll(); const timer = window.setInterval(poll, 1200); return () => window.clearInterval(timer);
  }, [jobId, job?.status, documentId]);

  function choose(next: File | undefined) {
    setError(undefined); setJob(undefined); setDocument(undefined); setJobId(undefined);
    if (!next) return;
    if (next.type !== "application/pdf" && !next.name.toLowerCase().endsWith(".pdf")) { setError("Please select a PDF file."); return; }
    setFile(next);
  }
  async function submit() {
    if (!file) return;
    setError(undefined); const data = new FormData(); data.append("file", file);
    const response = await fetch(`${API}/api/uploads`, { method: "POST", body: data });
    const payload = await response.json();
    if (!response.ok) { setError(payload.detail || "Upload failed."); return; }
    setJobId(payload.job_id); setDocumentId(payload.document_id); setJob({ status: "queued", progress: 0, current_step: "Queued" });
  }
  function drop(event: DragEvent<HTMLLabelElement>) { event.preventDefault(); choose(event.dataTransfer.files[0]); }
  return <main>
    <div className="orb one" /><div className="orb two" />
    <nav><span className="brand"><i>◇</i> PDFVisual</span><span>PDF → visual explanation</span></nav>
    <section className="hero"><p className="eyebrow">TURN DOCUMENTS INTO MOTION</p><h1>Your PDF, <em>made visual.</em></h1><p className="lede">Upload a research paper, report, or lesson. We extract its central ideas and render a concise animated walkthrough.</p>
      <label className={`dropzone ${file ? "ready" : ""}`} onDragOver={e => e.preventDefault()} onDrop={drop}>
        <input type="file" accept="application/pdf" onChange={(e: ChangeEvent<HTMLInputElement>) => choose(e.target.files?.[0])} />
        <span className="uploadIcon">↑</span><strong>{file ? file.name : "Drop your PDF here"}</strong><small>{file ? `${(file.size / 1024 / 1024).toFixed(1)} MB · ready to visualize` : "or browse files · PDF up to 25 MB"}</small>
      </label>
      <button disabled={!file || Boolean(jobId)} onClick={submit}>{jobId ? "Visualizing…" : "Create visual video →"}</button>
      {error && <p className="error">{error}</p>}
    </section>
    {job && <section className="card progress"><div><p className="eyebrow">PROCESSING</p><h2>{job.status === "completed" ? "Your visual is ready" : job.current_step}</h2></div><b>{job.progress}%</b><div className="bar"><span style={{ width: `${job.progress}%` }} /></div>{job.error && <p className="error">{job.error}</p>}</section>}
    {document?.video_url && <section className="card result"><div><p className="eyebrow">VIDEO EXPLANATION</p><h2>{document.title}</h2><p>{document.page_count} pages · {document.beats?.length} key ideas</p></div><video controls playsInline src={`${API}${document.video_url}`} /><ol>{document.beats?.map(beat => <li key={beat}>{beat}</li>)}</ol></section>}
    <footer>Built on the asynchronous processing and Manim rendering patterns from arxivpa, adapted for private PDF uploads.</footer>
  </main>;
}
