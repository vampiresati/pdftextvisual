import asyncio
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from core.config import OUTPUTS


async def add_narration(video_path: Path, document_id: str, text: str) -> bool:
    """Create an Edge neural voice track and mux it into the MP4.

    Edge TTS is intentionally optional: a visual video still succeeds on
    machines without internet access or the package installed.
    """
    try:
        import edge_tts
    except ImportError:
        return False
    audio_path = OUTPUTS / f"{document_id}.mp3"
    try:
        await edge_tts.Communicate(text, voice="en-US-JennyNeural").save(str(audio_path))
        narrated = OUTPUTS / f"{document_id}.narrated.mp4"
        result = await asyncio.to_thread(subprocess.run, [
            "ffmpeg", "-y", "-i", str(video_path), "-i", str(audio_path),
            "-filter_complex", "[0:v]tpad=stop_mode=clone:stop_duration=120[v]",
            "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-c:a", "aac",
            "-shortest", str(narrated),
        ], capture_output=True, text=True, timeout=180)
        if result.returncode:
            return False
        shutil.move(narrated, video_path)
        return True
    except Exception:
        return False
    finally:
        audio_path.unlink(missing_ok=True)

def build_scene_source(title: str, beats: list[str]) -> str:
    title_json, beats_json = json.dumps(title), json.dumps(beats)
    return f'''from manim import *
TITLE = {title_json}
BEATS = {beats_json}
class PDFVisualScene(Scene):
    def construct(self):
        self.camera.background_color = "#08111f"
        header = Text(TITLE, font_size=34, color=WHITE, line_spacing=0.8).scale_to_fit_width(11)
        header.to_edge(UP, buff=0.65)
        rule = Line(LEFT * 5.7, RIGHT * 5.7, color=BLUE_D).next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(header, shift=DOWN * .25), Create(rule), run_time=1.2)
        for index, beat in enumerate(BEATS):
            number = Text(str(index + 1).zfill(2), font_size=26, color=BLUE_B)
            label = Text(beat, font_size=30, color=GREY_A, line_spacing=0.85).scale_to_fit_width(8.8)
            row = VGroup(number, label).arrange(RIGHT, buff=.45, aligned_edge=UP)
            row.move_to(UP * (1.5 - index * 1.35))
            accent = Dot(radius=.08, color=TEAL_A).next_to(row, LEFT, buff=.35)
            self.play(FadeIn(accent), FadeIn(row, shift=RIGHT * .25), run_time=1.0)
            self.wait(4.5)
        closing = Text("PDFVisual", font_size=22, color=GREY_B).to_edge(DOWN, buff=.45)
        self.play(FadeIn(closing), run_time=.6)
        self.wait(2.0)
'''

async def render_video(document_id: str, title: str, beats: list[str], narration_text: str | None = None) -> tuple[Path, bool]:
    # Keep Manim's generated Python source outside the backend directory.  In
    # development, uvicorn --reload watches Python files below the backend
    # directory; putting the source in OUTPUTS causes a reload mid-job and
    # clears the in-memory job registry, so the next status poll returns 404.
    scenes_dir = Path(tempfile.gettempdir()) / "pdfvisual-scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    scene_path = scenes_dir / f"{document_id}.py"
    scene_path.write_text(build_scene_source(title, beats), encoding="utf-8")
    manim = shutil.which("manim")
    if not manim:
        raise RuntimeError("Manim is not installed. Install it to enable video rendering.")
    result = await asyncio.to_thread(subprocess.run, [manim, "-ql", "--format=mp4", "--media_dir", str(OUTPUTS), str(scene_path), "PDFVisualScene"], cwd=OUTPUTS, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[-700:])
    rendered = max((OUTPUTS / "videos").rglob("PDFVisualScene.mp4"), key=lambda item: item.stat().st_mtime, default=None)
    if rendered is None:
        raise RuntimeError("Manim finished without producing an MP4.")
    video_path = OUTPUTS / f"{document_id}.mp4"
    shutil.copy2(rendered, video_path)
    narration_ready = await add_narration(video_path, document_id, narration_text) if narration_text else False
    return video_path, narration_ready
