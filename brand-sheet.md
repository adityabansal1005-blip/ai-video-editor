# Brand Sheet: Health & Wellness Talking-Head Reels

**Status:** APPROVED 2026-10-27. Follow this on every edit.
**Built from:** 2 reference reels (in `References/`)
- `383378357_DXO504iDE24.mp4`: Dr Arnav Pai, laparoscopy explainer (62 s)
- `9678326420_DXhJXyoj2SK.mp4`: Dhanvantari Ayurveda, clinic intro (31 s)

The 3 `Video-*.mp4` files in References are about AI tools and editing, a different niche. I only borrowed one technique from them: the caption timing tip of using Whisper word timings.

---

## 1. What the references have in common

| | Dr Arnav Pai | Dhanvantari |
|---|---|---|
| Setup | Expert seated, talking to camera | Expert seated, talking to camera |
| Hook | A question: "What if I told you…" | A myth: "People say Ayurveda takes time" |
| Captions | Top third, 1–3 words, one **hero word** big and coloured | Top third, small lead-in words + **hero word** big and coloured |
| Visual change | Every ~2–3 s (text, diagram or cutaway) | Every ~2.6 s (11 cuts in 31 s) |
| Explaining | Medical illustrations on white, full screen or as a card | B-roll full screen or as a rounded card on black |
| Credibility | Name + credentials lower third | Name + hospital lower third |
| Ending | CTA question: "Tell me what you think" | Logo card on cream |
| Audio | No dead air, about −14 LUFS | No dead air, about −14 LUFS |

**The core formula:** a trusted expert, a hook that challenges a belief, simple visual proof for every claim, a credentials card, and a clean ending.

---

## 2. My style (adapted from the references, not copied)

### Format
- 9:16 vertical, 1080×1920, 30 fps
- Export: H.264 MP4, audio AAC 48 kHz, loudness **−14 LUFS**

### Colours
| Role | Colour | Hex |
|---|---|---|
| Hero word (captions) | Turmeric gold | `#F2B33D` |
| Body caption text | White | `#FFFFFF` |
| Cards / end screen | Deep forest | `#173A2E` |
| Diagram / info backgrounds | Warm cream | `#F7F0E1` |
| Highlight (circles, arrows) | Coral | `#E8604C` |

The references used bright yellow and lime green. This palette keeps the same "fresh and healthy" feeling but has its own warmer identity.

### Fonts (all free Google Fonts)
- **Hero words:** Archivo Black, ALL CAPS
- **Connector words** ("what if", "of the", "and even"): Instrument Serif *Italic*, small, above the hero word
- **Name card / labels:** Inter SemiBold + Inter Regular

### Captions
- **Language: Hinglish in Roman script** (e.g. "Kya diabetes mein kela kha sakte hain?"), even when the speaker talks in Hindi. Use simple, common spellings (*kya, mein, hain, nahi*), and keep English words as English (*diabetes, portion control, fiber*).
- Placed in the **top third**, clear of the face (never over the mouth)
- 1–3 words at a time, timed per word from Whisper
- One **hero word** per phrase, the keyword, big in turmeric gold. Connector words small, white, in serif italic.
- Soft shadow (no boxes) for readability
- Pop-in: scale 90% → 100% over 0.15 s, no bouncy effects
- Correct spellings of medical and food terms (check the transcript before rendering)

### Cuts and pacing
- Cut every pause longer than **0.1 s**, so there's no dead air
- **Something on screen changes every 2–3 s**: a jump cut, punch-in, caption change, or graphic
- Punch-in zooms: alternate 100% and 115% on jump cuts to hide them; a slow 100→105% push during long sentences
- Never let the same frame run longer than ~4 s without a change

### Explaining with graphics (the main thing to copy)
For every claim, show proof:
- **Diagrams / illustrations:** clean, on warm cream, with coral circles or arrows highlighting the key part
- **Icon + label cards** for lists (e.g. *LESS PAIN · QUICKER RECOVERY · SMALL SCARS*): icon above, hero font below, popping in one by one
- **B-roll:** full screen for big moments, or as a **rounded-corner card** (24 px radius) in the lower half while the speaker stays visible
- Images and illustrations should be accurate and real, never AI-generated medical diagrams that could be wrong

### Credibility card (lower third)
- Shown in the first 5–8 s, or right after the hook
- Name in Archivo Black (white), credentials below in Inter (white, 70% opacity), on a dark gradient at the bottom
- Slide up 0.3 s, hold 3–4 s, fade out

### Music and sound
- Soft background track under the voice at about **−24 dB** (voice always clearly louder)
- Subtle sound effects only on key moments: a soft *pop* for list items, a *whoosh* for full-screen cutaways
- Royalty-free music only

### Ending
- Last line asks a question to drive comments (e.g. "Tell me what you think")
- Final 1.5 s: end card on deep forest with name / handle in turmeric gold

---

## 3. Every-edit checklist
1. Transcribe with Whisper and fix spelling of key terms
2. Remove pauses > 0.1 s, bad takes and repeated lines
3. Hook in the first 2 s, with its hero word on screen from frame 1
4. Add credibility card early
5. Add proof (diagram / icon / B-roll) for each claim
6. Check for a visual change every 2–3 s
7. Captions top third, never covering the face
8. Music at −24 dB, master to −14 LUFS
9. Show the storyboard for approval, then export to `Exports/`
