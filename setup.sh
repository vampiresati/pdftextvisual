#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python >/dev/null || { echo "Python is required." >&2; exit 1; }
command -v npm >/dev/null || { echo "Node.js and npm are required." >&2; exit 1; }

echo "Installing PDFVisual backend dependencies..."
python -m pip install -r "$PROJECT_DIR/backend/requirements.txt"

echo "Installing PDFVisual frontend dependencies..."
npm --prefix "$PROJECT_DIR/frontend" install

if command -v manim >/dev/null; then
  echo "Manim detected: $(manim --version | head -n 1)"
else
  echo "Warning: Manim is not installed. PDF uploads will be accepted, but video rendering will fail."
fi

cat <<EOF

Setup complete.

Start the backend:
  cd "$PROJECT_DIR/backend"
  uvicorn main:app --reload --port 8000

Start the frontend in another terminal:
  cd "$PROJECT_DIR/frontend"
  npm run dev

Open http://localhost:3000
EOF
