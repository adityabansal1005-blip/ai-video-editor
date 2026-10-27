"""Generates index.html (the HyperFrames composition) for the diabetes-fruits reel.

Inputs:
  ../storyboard/edit.json   approved cut list + scenes (Hinglish lines, hero words)
  words.json                whisper small-model word timings on assets/base.mp4
  words_base_src.json       whisper base-model word timings on the raw source
                            (used for the tail, where the small model skipped words)
"""
import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
edit = json.loads((ROOT.parent / "storyboard" / "edit.json").read_text(encoding="utf-8"))
SEGS, SCENES = edit["keep_segments"], edit["scenes"]
FPS = 30
BASE_DUR = 61.6
END_CARD = 1.6
TOTAL = round(BASE_DUR + END_CARD, 2)
SWITCH_SRC = 55.0   # source time after which the base-model timings are used

# --- source -> output time, matching how make_base.py rounds each segment to frames
seg_out = []
acc = 0.0
for a, b in SEGS:
    seg_out.append((a, b, acc))
    acc += math.ceil((b - a) * FPS - 0.01) / FPS
scale = BASE_DUR / acc


def to_out(t):
    for a, b, o in seg_out:
        if t <= b:
            return (o + max(0.0, t - a)) * scale
    return BASE_DUR


def load_words(path):
    d = json.loads(Path(path).read_bytes().decode("utf-8", "replace"))
    out = []
    for s in d["transcription"]:
        txt = s["text"].strip()
        if txt:
            out.append((s["offsets"]["from"] / 1000, txt))
    # drop hallucinated runs where many words share one timestamp
    clean = [w for i, w in enumerate(out) if not (i + 1 < len(out) and abs(out[i + 1][0] - w[0]) < 0.001)]
    return clean


small = [t for t, _ in load_words(ROOT / "words.json") if t < to_out(SWITCH_SRC) and t < 61.4]
base = [to_out(t) for t, _ in load_words(sys.argv[1]) if t >= SWITCH_SRC]
word_times = sorted(small + base)

# --- scene windows in output time
for sc in SCENES:
    sc["t0"], sc["t1"] = to_out(sc["src"][0]), to_out(sc["src"][1])
SCENES[0]["t0"] = 0.0
for sc, nxt in zip(SCENES, SCENES[1:]):
    sc["t1"] = nxt["t0"]
SCENES[-1]["t1"] = BASE_DUR


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


# --- per-word timing: spread each scene's Hinglish words over whisper's word starts
words = []  # (time, text, scene)
for sc in SCENES:
    mine = sc["line"].split()
    ws = [t for t in word_times if sc["t0"] - 0.05 <= t < sc["t1"]]
    for i, w in enumerate(mine):
        if ws:
            t = ws[min(len(ws) - 1, int(i * len(ws) / len(mine)))]
        else:
            t = sc["t0"] + (sc["t1"] - sc["t0"]) * i / len(mine)
        words.append([max(t, sc["t0"]), w, sc])
for prev, cur in zip(words, words[1:]):   # keep times strictly increasing
    if cur[0] <= prev[0]:
        cur[0] = prev[0] + 0.12


def find_word(scene_id, needle, after=0.0):
    """Output time of the first word in the scene matching needle."""
    n = norm(needle)
    for t, w, sc in words:
        if sc["id"] == scene_id and t >= after and norm(w).startswith(n):
            return t
    raise ValueError(f"'{needle}' not found in scene {scene_id}")


# --- caption chunks -> groups
chunks = []  # dict(t, text, hero)
for sc in SCENES:
    sw = [w for w in words if w[2] is sc]
    heroes = [h.split() for h in sc["hero"]]
    i, cur = 0, []
    while i < len(sw):
        hit = next((h for h in heroes
                    if [norm(x[1]) for x in sw[i:i + len(h)]] == [norm(x) for x in h]), None)
        if hit:
            if cur:
                chunks.append(dict(t=cur[0][0], text=" ".join(x[1] for x in cur), hero=False))
                cur = []
            chunks.append(dict(t=sw[i][0], text=" ".join(x[1] for x in sw[i:i + len(hit)]), hero=True))
            i += len(hit)
            continue
        cur.append(sw[i])
        if len(cur) == 3 or re.search(r"[,.?:…]$", sw[i][1]):
            chunks.append(dict(t=cur[0][0], text=" ".join(x[1] for x in cur), hero=False))
            cur = []
        i += 1
    if cur:
        chunks.append(dict(t=cur[0][0], text=" ".join(x[1] for x in cur), hero=False))

groups, i = [], 0
while i < len(chunks):
    c = chunks[i]
    if not c["hero"] and i + 1 < len(chunks) and chunks[i + 1]["hero"]:
        groups.append(dict(t=c["t"], lead=c["text"], hero=chunks[i + 1]["text"], th=chunks[i + 1]["t"]))
        i += 2
    elif c["hero"]:
        groups.append(dict(t=c["t"], lead="", hero=c["text"], th=c["t"]))
        i += 1
    else:
        groups.append(dict(t=c["t"], lead=c["text"], hero="", th=c["t"]))
        i += 1
for g, nxt in zip(groups, groups[1:]):
    g["end"] = min(nxt["t"], max(g["th"], g["t"]) + 2.2)
groups[-1]["end"] = min(groups[-1]["t"] + 2.5, BASE_DUR)


def clean(s):
    return html.escape(s.strip(" ,…").rstrip(",:"))


def hero_size(text):
    longest = max(len(w) for w in text.split())
    size = min(132, 940 / (longest * 0.78))
    if len(text) * 0.78 * size > 940:   # wraps to two lines: keep it clear of the head
        size = min(size, 92)
    return int(size)


# --- graphics ------------------------------------------------------------------
els, anims, sfx = [], [], []
uid = 0


def clip(start, end, inner, cls="", track=3):
    global uid
    uid += 1
    cid = f"g{uid}"
    els.append(f'<div id="{cid}" class="clip {cls}" data-start="{start:.3f}" '
               f'data-duration="{end - start:.3f}" data-track-index="{track}">{inner}</div>')
    return cid


def pop_in(sel, t, y=40):
    anims.append(f'tl.fromTo("{sel}",{{y:{y},scale:0.9,opacity:0}},{{y:0,scale:1,opacity:1,duration:0.28,ease:"back.out(1.8)"}},{t:.3f});')


def fade_out(sel, t):
    anims.append(f'tl.to("{sel}",{{opacity:0,duration:0.2,ease:"power1.in"}},{t - 0.2:.3f});')


def add_sfx(name, t, vol):
    sfx.append((name, t, vol))


# captions
for k, g in enumerate(groups):
    lead = f'<div class="lead{" body" if not g["hero"] else ""}">{clean(g["lead"])}</div>' if g["lead"] else ""
    hero = (f'<div class="hero" style="font-size:{hero_size(g["hero"])}px">{clean(g["hero"])}</div>'
            if g["hero"] else "")
    cid = clip(g["t"], g["end"], f'<div class="capbox">{lead}{hero}</div>', "cap", track=2)
    if g["lead"]:
        anims.append(f'tl.fromTo("#{cid} .lead",{{y:18,opacity:0}},{{y:0,opacity:1,duration:0.15,ease:"power2.out"}},{g["t"]:.3f});')
    if g["hero"]:
        anims.append(f'tl.fromTo("#{cid} .hero",{{scale:0.9,opacity:0}},{{scale:1,opacity:1,duration:0.15,ease:"power2.out"}},{g["th"]:.3f});')

S = {sc["id"]: sc for sc in SCENES}

# 1 hook: fruit icons
for k, (word, emoji, side) in enumerate([("kela", "🍌", "left"), ("aam", "🥭", "right")]):
    t = find_word(1, word)
    cid = clip(t, S[1]["t1"], f'<div class="fruit {side}">{emoji}</div>')
    pop_in(f"#{cid} .fruit", t, 0)
    add_sfx("pop", t, 0.5)

# 2 name card (spans into scene 3)
t = S[2]["t0"] + 0.2
cid = clip(t, t + 3.8, '<div class="namecard"><div class="nm">Dr. Sachi Tandon</div>'
           '<div class="cr">Diabetologist · MD Naturopathy · Nutrition Expert</div></div>')
anims.append(f'tl.fromTo("#{cid} .namecard",{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.3,ease:"power3.out"}},{t:.3f});')
fade_out(f"#{cid} .namecard", t + 3.8)

# 3 instant energy
t = find_word(3, "instant")
cid = clip(t, S[3]["t1"], '<div class="card dark"><span class="ico">⚡</span><span>Instant energy</span></div>')
pop_in(f"#{cid} .card", t)
add_sfx("pop", t, 0.5)

# 4 fructose
t = find_word(4, "fructose")
cid = clip(t, S[4]["t1"], '<div class="card cream"><span class="ico">🍌</span>'
           '<span><b>FRUCTOSE</b><br-x>= fruit ki natural sugar</span></div>')
pop_in(f"#{cid} .card", t)
add_sfx("pop", t, 0.5)

# 5 micronutrient chips
t = find_word(5, "nutrition")
chips = "".join(f'<span class="chip c{i}">{x}</span>' for i, x in enumerate(["VITAMINS", "MINERALS", "FIBRE"]))
cid = clip(t, S[5]["t1"], f'<div class="chips">{chips}</div>')
for i in range(3):
    pop_in(f"#{cid} .c{i}", t + i * 0.45, 20)
    add_sfx("pop", t + i * 0.45, 0.45)

# 6 absorption
t = find_word(6, "absorption")
cid = clip(t, S[6]["t1"], '<div class="card cream small"><span>Kam micronutrients</span>'
           '<span class="arrow">→</span><span><b>Absorption kam</b></span></div>')
pop_in(f"#{cid} .card", t)

# 7 key factor full-screen title
t = find_word(7, "portion") - 0.15
cid = clip(t, t + 1.5, '<div class="title"><div class="k">key factor</div><div class="pc">PORTION<br-x>CONTROL</div></div>',
           "full", track=5)
anims.append(f'tl.fromTo("#{cid} .title",{{opacity:0}},{{opacity:1,duration:0.15}},{t:.3f});')
anims.append(f'tl.fromTo("#{cid} .pc",{{scale:1.25,opacity:0}},{{scale:1,opacity:1,duration:0.35,ease:"power3.out"}},{t + 0.1:.3f});')
fade_out(f"#{cid} .title", t + 1.5)
add_sfx("whoosh", t - 0.2, 0.6)

# 8 don'ts
for k, (word, label) in enumerate([("chaar", "4 kele ek saath"), ("bada", "1 bada aam ek saath")]):
    t = find_word(8, word)
    cid = clip(t, S[8]["t1"], f'<div class="card no n{k}"><span class="x">✕</span><span>{label}</span></div>')
    pop_in(f"#{cid} .card", t)
    add_sfx("thud", t, 0.7)

# 9 do's
items = [("short", "Chhota portion"), ("juice", "Juice nahi"), ("fibre", "Fibre ke saath")]
t0 = find_word(9, "short")
rows = "".join(f'<div class="row r{i}"><span class="tick">✓</span>{lbl}</div>' for i, (_, lbl) in enumerate(items))
cid = clip(t0, S[9]["t1"], f'<div class="list">{rows}</div>')
for i, (word, _) in enumerate(items):
    t = find_word(9, word)
    pop_in(f"#{cid} .r{i}", t, 20)
    add_sfx("pop", t, 0.5)

# 10 verdict stamp
t = find_word(10, "achhe")
cid = clip(t, S[10]["t1"], '<div class="stamp">Fruits bure nahi,<br-x><b>ACHHE</b> hain ✓</div>')
anims.append(f'tl.fromTo("#{cid} .stamp",{{scale:1.5,rotation:-10,opacity:0}},{{scale:1,rotation:-4,opacity:1,duration:0.3,ease:"back.out(2)"}},{t:.3f});')
add_sfx("ding", t, 0.45)

# 11 big name card
t = find_word(11, "dr")
cid = clip(t, S[11]["t1"], '<div class="namecard big"><div class="nm">Dr. Sachi Tandon</div>'
           '<div class="cr">Diabetologist<br-x>MD Naturopathy<br-x>Nutrition Expert</div></div>')
anims.append(f'tl.fromTo("#{cid} .namecard",{{y:60,opacity:0}},{{y:0,opacity:1,duration:0.3,ease:"power3.out"}},{t:.3f});')

# 12 end card
cid = clip(BASE_DUR, TOTAL, '<div class="end"><div class="k">for a customised diabetes meal plan</div>'
           '<div class="brand">SACHI<br-x>NATUROPATHY</div><div class="who">Dr. Sachi Tandon</div></div>', "full", track=5)
anims.append(f'tl.fromTo("#{cid} .brand",{{scale:0.9,opacity:0}},{{scale:1,opacity:1,duration:0.4,ease:"power3.out"}},{BASE_DUR:.3f});')
anims.append(f'tl.fromTo("#{cid} .k, #{cid} .who",{{y:20,opacity:0}},{{y:0,opacity:1,duration:0.4,stagger:0.12}},{BASE_DUR + 0.15:.3f});')

# slow pushes on the video wrapper (scenes 5 and 10)
for k, (sid, amt) in enumerate([(5, 1.05), (10, 1.08)]):
    a, b = S[sid]["t0"], S[sid]["t1"]
    lazy = ",immediateRender:false" if k else ""
    anims.append(f'tl.fromTo("#cam",{{scale:1}},{{scale:{amt},duration:{b - a:.3f},ease:"none"{lazy}}},{a:.3f});')
    anims.append(f'tl.set("#cam",{{scale:1}},{b:.3f});')

SFX_LEN = {"pop": 0.18, "whoosh": 0.6, "thud": 0.35, "ding": 0.9}
audio = "".join(
    f'<audio id="sfx{i}" src="assets/{n}.wav" data-start="{t:.3f}" data-duration="{SFX_LEN[n]}" '
    f'data-track-index="{12 + i % 3}" data-volume="{v}"></audio>\n'
    for i, (n, t, v) in enumerate(sfx))

# "<br-x>" is a line-break marker: lint forbids <br> in body text, so split into blocks
body = "\n".join(els)
body = re.sub(r"<span><b>(.*?)</b><br-x>(.*?)</span>", r'<span class="stack"><b>\1</b><span>\2</span></span>', body)
body = re.sub(r"(<div class=\"(?:pc|brand|stamp|cr)\">)(.*?)(</div>)",
              lambda m: m.group(1) + "".join(f'<span class="ln">{p}</span>' for p in m.group(2).split("<br-x>")) + m.group(3),
              body)

css = (ROOT / "style.css").read_text(encoding="utf-8")
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080, height=1920">
<title>Diabetes Fruits Reel</title>
<script src="assets/gsap.min.js"></script>
<style>
{css}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{TOTAL}">
  <div id="cam">
    <video id="a-roll" src="assets/base.mp4" data-start="0" data-duration="{BASE_DUR}" data-track-index="0" muted playsinline></video>
  </div>
  <audio id="voice" src="assets/base.mp4" data-start="0" data-duration="{BASE_DUR}" data-track-index="10" data-volume="1"></audio>
  <audio id="music" src="assets/music.wav" data-start="0" data-duration="{TOTAL}" data-track-index="11" data-volume="1"></audio>
{audio}
{body}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(anims)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
(ROOT / "index.html").write_text(page, encoding="utf-8")
print(f"groups={len(groups)} graphics={uid - len(groups)} sfx={len(sfx)} total={TOTAL}s")
for sc in SCENES:
    print(f"scene {sc['id']:>2} {sc['t0']:6.2f}-{sc['t1']:6.2f}")
