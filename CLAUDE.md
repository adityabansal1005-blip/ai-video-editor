# AI Video Editor

This folder is a video-editing workspace. Claude edits Instagram Reels from the user's raw footage. Read `NOTES.md` for the history and the decisions made so far.

## Folders
- `Raw footage/`: source clips to edit (plus `<name> - transcript.md` once transcribed). Videos are not in git.
- `References/`: reels the style was learned from. Links are in `References/README.md`.
- `Exports/`: finished videos (not in git)
- `storyboard/`: storyboard page + `edit.json` (cut list and scenes) for the current reel
- `reel-<name>/`: one HyperFrames project per reel (`build.py` → `index.html` → render)
- `tools/`: per-machine tools, see `tools/README.md`

## Where the tools are
| | Windows laptop | Cloud / Linux |
|---|---|---|
| Setup | already installed | run `bash setup-cloud.sh --small` first |
| Whisper | `tools/whisper/Release/whisper-cli.exe` | `tools/whisper-cli` |
| yt-dlp | `tools/yt-dlp.exe` | `yt-dlp` |
| Models | `tools/ggml-base.bin`, `tools/ggml-small.bin` | same |

FFmpeg and Node (for `npx hyperframes`) are on PATH in both. Remotion is not used.

## Rules
- **Always follow `brand-sheet.md`** (approved 2026-10-27) for every edit: captions, colours, fonts, pacing, graphics, audio.
- Captions are Hinglish in Roman script. Check names and medical terms against the transcript file before rendering.
- Use the `small` Whisper model for Hindi speech.
- Always show a storyboard for review before rendering, then export to `Exports/`.
- Use the local Whisper. The OpenAI API account has no credits.
- Never commit videos, audio (except the small SFX), models or tools (see `.gitignore`).

## Cloud sessions
- Raw footage isn't in the repo. Ask the user for a Google Drive share link and download it with `curl -L` (or `gdown`) into `Raw footage/`.
- Reference reels: download from their links with `yt-dlp`.
- The cloud can't save to the user's laptop. Deliver finished videos as a downloadable link, or ask how they want them.
