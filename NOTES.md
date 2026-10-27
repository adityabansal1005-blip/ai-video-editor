# Project notes (history and decisions)

A summary of the first session (2026-10-27), so any future Claude session, local or cloud, knows what was decided and why. Rules to follow live in `CLAUDE.md` and `brand-sheet.md`. This file is the background.

## Where the idea came from
An Instagram reel by **@millee.md** (credit @samdespomarketing) showed a 4-step "AI video editor with Claude Code":
1. **Set it up:** a folder with `Raw footage/`, `References/`, `Exports/`.
2. **Install tools:** Remotion, HyperFrames, FFmpeg, Whisper, yt-dlp.
3. **Find your style:** give Claude 3–5 reels, it studies them and writes a brand sheet (own it, don't copy).
4. **Film and edit:** drop raw footage in, Claude cuts pauses > 0.1 s, follows the brand sheet, adds captions, music and graphics, shows a storyboard first, then exports.

This repo follows that workflow.

## Setup decisions and lessons
- **Everything is free** except Claude itself. All tools are open source and run locally. Remotion is free for individuals and companies of up to 3 people.
- **Remotion was skipped.** HyperFrames covers code-based editing, motion graphics and captions.
- **OpenAI Whisper API: no credits.** Always use local whisper.cpp.
- **The user's ISP is very slow to GitHub release downloads and PyPI** (about 5 KB/s, even though general speed is about 9 Mbps). npm and Hugging Face are fast. On the Windows laptop, tools were downloaded through the browser instead.
- **whisper.cpp:** the latest tags (v1.9.x) ship no Windows binaries. Use build `b5454` (`whisper-bin-x64.zip`, CPU build; the laptop is a Ryzen 5 5600U with no NVIDIA GPU).
- **Python 3.14** has no faster-whisper wheels yet, and the registered 3.13 points at a missing exe. That's another reason to use whisper.cpp.
- **Whisper models:** `base` is fine for English but poor for Hindi. **Use `small` for Hindi.** It's accurate but can skip or garble the final ~10 s, so check the tail against the `base` output.

## Style (brand sheet, approved 2026-10-27)
Learned from two health-niche reels: Dr Arnav Pai (laparoscopy) and Dhanvantari Ayurveda. The shared formula: an expert talking to camera, a hook that challenges a belief, top-third captions with one big coloured hero word, visual proof for every claim, an early credentials card, a change every 2–3 s, no dead air, −14 LUFS.

Own palette: turmeric `#F2B33D`, deep forest `#173A2E`, cream `#F7F0E1`, coral `#E8604C`. Fonts: Archivo Black (hero words), Instrument Serif Italic (connector words), Inter (labels). Full rules are in `brand-sheet.md`.

**Captions are Hinglish in Roman script** (the user's choice), even when the speaker talks in Hindi.

## Reel 1: "Diabetes mein kela aur aam?" (`reel-diabetes-fruits/`)
- **Speaker:** Dr. Sachi Tandon, Diabetologist · MD Naturopathy · Nutrition Expert. **Clinic:** Sachi Naturopathy. (Spellings confirmed by the user.)
- **Source:** a WhatsApp copy, 576×1024 (rotated), 69.5 s. It's soft when upscaled, so ask for the original phone file next time.
- **Message:** fruits are fine for diabetics with portion control: small portions, whole fruit with fibre, no juice.
- **Storyboard:** `storyboard/index.html`, 12 scenes, cut to 61.6 s plus a 1.6 s end card. Approved.
- **Pipeline:**
  1. `storyboard/plan.py` → `edit.json` (cut list from `silencedetect -35 dB`, pauses ≥ 0.15 s trimmed to 0.06 s of padding; the silent first 3.5 s removed).
  2. `reel-diabetes-fruits/make_base.py` → `assets/base.mp4` (cut, upscaled to 1080×1920 @ 30, punch-ins 1.0/1.12/1.15, light unsharp).
  3. Word timings: `whisper-cli -m ggml-small.bin -l hi -ml 1 -sow -oj` on `base.mp4` audio → `words.json`, plus `words_base_src.json` for the tail.
  4. `build.py` → `index.html` (HyperFrames composition: captions, cards, SFX). `style.css` holds the brand styling.
  5. `npx hyperframes render --quality delivery` (about 4 min on the laptop GPU), then mix in the music and `loudnorm` to −14 LUFS.
- **Music:** synthesised (`make_music.sh`) to avoid copyright. It plays at full file level (file mean −40 dB, about 23 dB under the voice). The first export had it at 9% and it was inaudible.
- **Export:** `Exports/Diabetes-kela-aam - Dr Sachi Tandon - reel v2.mp4` (not in git).
- **Status:** the user says it **needs a lot of refinement**. Ask what to improve before changing things.

## Known gaps / ideas
- Caption timing is spread across Whisper's word starts per scene, so some words can land a beat early or late.
- HyperFrames lint wants scenes split into sub-compositions (Studio tidiness only, not a render issue).
- The music is a simple synth pad. A real royalty-free track would sound better.
- No Instagram handle or phone number on the end card yet.
