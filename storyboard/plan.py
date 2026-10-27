"""Builds the cut list, scene plan and thumbnails for the storyboard.

Usage: python plan.py <source video> <silencedetect log>
Writes edit.json (cut list + scenes, used later for rendering) and thumbs/.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
SIL_LOG = Path(sys.argv[2])
OUT = Path(__file__).parent
PAD = 0.06          # keep this much air either side of speech
MIN_PAUSE = 0.15    # pauses shorter than this stay (natural breath)
SPEECH_START, SPEECH_END = 3.48, 68.85

# --- cut list -----------------------------------------------------------------
log = SIL_LOG.read_text()
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
silences = [(s, e) for s, e in zip(starts, ends) if e - s >= MIN_PAUSE]

keep, cur = [], SPEECH_START
for s, e in silences:
    if e <= SPEECH_START or s >= SPEECH_END:
        continue
    cut_from, cut_to = max(s + PAD, cur), min(e - PAD, SPEECH_END)
    if cut_to - cut_from > 0.05:
        keep.append((round(cur, 3), round(cut_from, 3)))
        cur = cut_to
keep.append((round(cur, 3), SPEECH_END))


def to_out(t):
    """Map a source timestamp to its time in the cut video."""
    acc = 0.0
    for a, b in keep:
        if t <= b:
            return acc + max(0.0, t - a)
        acc += b - a
    return acc


total = to_out(SPEECH_END)

# --- scenes (source times) ------------------------------------------------------
# caption: list of (word, is_hero). Hinglish, per brand-sheet.md.
scenes = [
    dict(id=1, name="Hook", src=(3.48, 6.62),
         line="Kya diabetes mein hum kela aur aam kha sakte hain?",
         hero=["DIABETES", "KELA", "AAM"],
         visual="Punch-in 115%. Banana + mango icons pop in beside the question.",
         graphic="Captions from frame 1. Question mark pulses once.",
         sfx="Soft pop on each fruit icon"),
    dict(id=2, name="Tease", src=(6.62, 9.05),
         line="Iska answer aapko surprise kar dega.",
         hero=["SURPRISE"],
         visual="Back to 100%. Lower third slides up.",
         graphic="Name card: Dr. Sachi Tandon / Diabetologist · MD Naturopathy · Nutrition Expert",
         sfx="Music bed starts"),
    dict(id=3, name="Why fruits", src=(9.85, 16.2),
         line="Humare shareer ko kuch aise tatvon ki bahut zyada zaroorat hoti hai, jo humein instant energy dete hain.",
         hero=["ZAROORAT", "INSTANT ENERGY"],
         visual="Jump cut at the mid-sentence pause, 100% → 115%.",
         graphic="Energy icon card (lightning) pops in on 'instant energy'.",
         sfx="Pop"),
    dict(id=4, name="Fructose", src=(16.9, 21.8),
         line="Jaise ki fructose, jo humare banana ya phir aur fruits mein hota hai.",
         hero=["FRUCTOSE", "FRUITS"],
         visual="Rounded card in lower half, speaker stays visible.",
         graphic="Cream card: 'FRUCTOSE = fruit ki natural sugar' with banana illustration.",
         sfx="Pop"),
    dict(id=5, name="Micronutrients", src=(22.0, 28.15),
         line="Aur usme kuch aise poshak tatva, yaani nutrition hota hai, jinko hum micronutrients kehte hain.",
         hero=["NUTRITION", "MICRONUTRIENTS"],
         visual="Slow push 100→105%.",
         graphic="Three chips pop in one by one: VITAMINS · MINERALS · FIBRE",
         sfx="Pop ×3"),
    dict(id=6, name="Absorption", src=(28.4, 35.6),
         line="Agar woh humari body mein prachur matra mein nahi hain, to hum jo bhi intake karte hain, uska absorption proper nahi hota.",
         hero=["BODY", "ABSORPTION"],
         visual="Jump cut 115% → 100% at 'to hum jo bhi'.",
         graphic="Simple card: 'Kam micronutrients → absorption kam'",
         sfx="None"),
    dict(id=7, name="Key factor", src=(35.9, 38.3),
         line="To yahan par key factor hai: portion control.",
         hero=["PORTION CONTROL"],
         visual="FULL-SCREEN title on deep forest for ~1.2 s, then back to speaker.",
         graphic="'KEY FACTOR' in serif italic, 'PORTION CONTROL' huge in turmeric.",
         sfx="Whoosh in"),
    dict(id=8, name="Don't", src=(38.9, 44.6),
         line="Agar aap chaar banana ek saath kha lete hain, ya bada mango ek saath kha lete hain, to woh aapko nuksaan kar sakte hain.",
         hero=["CHAAR BANANA", "BADA MANGO", "NUKSAAN"],
         visual="Punch-in 115% on 'nuksaan'.",
         graphic="❌ cards in coral: '4 kele ek saath' and '1 bada aam ek saath'",
         sfx="Soft 'wrong' thud on each ❌"),
    dict(id=9, name="Do", src=(44.9, 50.6),
         line="Lekin agar aap usko short portion mein khate hain, juice nahi banate, aur fibre ke saath khate hain…",
         hero=["SHORT PORTION", "JUICE NAHI", "FIBRE"],
         visual="Back to 100%.",
         graphic="✅ icon list pops in one by one: CHHOTA PORTION · JUICE NAHI · FIBRE KE SAATH",
         sfx="Pop ×3"),
    dict(id=10, name="Verdict", src=(50.9, 56.85),
         line="…to fruits bure nahi hain, fruits achhe hain. Unko zaroor include kariye.",
         hero=["BURE NAHI", "ACHHE", "ZAROOR"],
         visual="Slow push 100→108% for emphasis.",
         graphic="'Fruits bure nahi, ACHHE hain' ✅ stamp on 'achhe'.",
         sfx="Ding on 'achhe'"),
    dict(id=11, name="Intro", src=(56.9, 62.05),
         line="Main hoon Dr. Sachi Tandon, diabetologist, MD Naturopathy and nutritional expert.",
         hero=["DR. SACHI TANDON"],
         visual="Punch-in 110%.",
         graphic="Name card again, larger, with credentials listed.",
         sfx="None"),
    dict(id=12, name="CTA + end card", src=(62.05, 68.85),
         line="Agar aap diabetes ke liye customised meal plan chahte hain, to Sachi Naturopathy se sampark kariye, immediately.",
         hero=["MEAL PLAN", "SACHI NATUROPATHY"],
         visual="100%, then 1.5 s end card.",
         graphic="End card on deep forest: 'SACHI NATUROPATHY' in turmeric + 'Customised diabetes meal plans'.",
         sfx="Music swells and fades out"),
]

thumbs = OUT / "thumbs"
thumbs.mkdir(exist_ok=True)
for sc in scenes:
    a, b = sc["src"]
    sc["out"] = (round(to_out(a), 2), round(to_out(b), 2))
    sc["dur"] = round(sc["out"][1] - sc["out"][0], 2)
    mid = (a + b) / 2
    thumb = thumbs / f"scene{sc['id']:02d}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{mid:.2f}", "-i", str(SRC),
                    "-frames:v", "1", "-vf", "scale=360:-2", "-q:v", "3", str(thumb)], check=True)
    sc["thumb"] = f"thumbs/{thumb.name}"

# make scenes contiguous: each runs until the next one starts
for sc, nxt in zip(scenes, scenes[1:]):
    sc["out"] = (sc["out"][0], nxt["out"][0])
scenes[0]["out"] = (0.0, scenes[0]["out"][1])
for sc in scenes:
    sc["dur"] = round(sc["out"][1] - sc["out"][0], 2)

edit = dict(source=str(SRC), source_duration=69.51, output_duration=round(total, 2),
            keep_segments=keep, scenes=scenes)
(OUT / "edit.json").write_text(json.dumps(edit, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"segments kept: {len(keep)}  output: {total:.2f}s (from 69.51s)")
for sc in scenes:
    print(f"{sc['id']:>2} {sc['name']:<16} out {sc['out'][0]:5.2f}-{sc['out'][1]:5.2f} ({sc['dur']}s)")
