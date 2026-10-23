import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "PDFVisual — PDFs, Visualized", description: "Upload a PDF and turn its key ideas into a short visual video." };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
