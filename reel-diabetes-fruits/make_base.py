"""Cuts the raw footage per storyboard/edit.json into assets/base.mp4.

Upscales to 1080x1920 @30fps, adds the storyboard's punch-in zooms per kept
segment, and joins audio with 8 ms fades so cuts don't click.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
edit = json.loads((ROOT.parent / "storyboard" / "edit.json").read_text(encoding="utf-8"))
src = str((ROOT.parent / "storyboard" / edit["source"]).resolve())
segs = edit["keep_segments"]
scenes = edit["scenes"]

# zoom per segment: alternate 1.0 / 1.12 on jump cuts; hook and "nuksaan" open tight
PUNCH = {1: 1.15, 8: 1.12, 11: 1.10}


def scene_of(t):
    for sc in scenes:
        if sc["src"][0] - 0.01 <= t < sc["src"][1]:
            return sc["id"]
    return scenes[-1]["id"]


parts, alt = [], False
for i, (a, b) in enumerate(segs):
    sid = scene_of(a)
    z = PUNCH.get(sid, 1.12 if alt else 1.0)
    alt = not alt
    w, h = int(1080 * z) // 2 * 2, int(1920 * z) // 2 * 2
    # crop keeps the face area: centre horizontally, bias towards the top third
    y_off = int((h - 1920) * 0.35)
    parts.append(
        f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,"
        f"scale={w}:{h}:flags=lanczos,crop=1080:1920:{(w - 1080) // 2}:{y_off},"
        f"unsharp=5:5:0.6,setsar=1[v{i}];"
        f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
        f"afade=t=in:d=0.008,afade=t=out:st={max(0, b - a - 0.008):.3f}:d=0.008[a{i}];"
    )
concat = "".join(f"[v{i}][a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[v][a]"
graph = "".join(parts) + concat

out = ROOT / "assets" / "base.mp4"
out.parent.mkdir(exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", graph,
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)], check=True)
print("wrote", out)
