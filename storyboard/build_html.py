"""Renders storyboard/index.html from edit.json."""
import base64
import html
import json
from pathlib import Path

HERE = Path(__file__).parent
edit = json.loads((HERE / "edit.json").read_text(encoding="utf-8"))
scenes = edit["scenes"]
total = edit["output_duration"]


def fmt(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def caption_mock(sc):
    """First hero word with the words just before it as the small serif lead-in."""
    hero = sc["hero"][0]
    words = sc["line"].split()
    first = hero.split()[0].lower()
    idx = next((i for i, w in enumerate(words) if w.lower().strip(",.?…:") == first), 0)
    lead = " ".join(words[max(0, idx - 3):idx])
    return f'<span class="lead">{html.escape(lead)}</span><span class="hero">{html.escape(hero)}</span>'


bar = "".join(
    f'<a href="#s{sc["id"]}" class="seg" style="flex:{sc["dur"]}" title="{html.escape(sc["name"])}">{sc["id"]}</a>'
    for sc in scenes)

cards = []
for sc in scenes:
    heroes = "".join(f'<span class="chip">{html.escape(h)}</span>' for h in sc["hero"])
    cards.append(f"""
<article class="scene" id="s{sc['id']}">
  <div class="frame">
    <img src="data:image/jpeg;base64,{base64.b64encode((HERE / sc['thumb']).read_bytes()).decode()}" alt="Scene {sc['id']} frame">
    <div class="cap">{caption_mock(sc)}</div>
  </div>
  <div class="body">
    <div class="meta"><span class="num">{sc['id']:02d}</span><h2>{html.escape(sc['name'])}</h2>
      <span class="time">{fmt(sc['out'][0])}–{fmt(sc['out'][1])} · {sc['dur']:.1f}s</span></div>
    <p class="line">“{html.escape(sc['line'])}”</p>
    <div class="chips">{heroes}</div>
    <dl>
      <dt>Camera</dt><dd>{html.escape(sc['visual'])}</dd>
      <dt>Graphic</dt><dd>{html.escape(sc['graphic'])}</dd>
      <dt>Sound</dt><dd>{html.escape(sc['sfx'])}</dd>
    </dl>
    <div class="review">
      <label><input type="radio" name="r{sc['id']}" value="keep" checked> Keep</label>
      <label><input type="radio" name="r{sc['id']}" value="change"> Change</label>
      <label><input type="radio" name="r{sc['id']}" value="drop"> Drop</label>
      <input class="note" type="text" placeholder="Note for this scene…" data-scene="{sc['id']}">
    </div>
  </div>
</article>""")

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Diabetes Fruits Storyboard</title>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--gold:#F2B33D;--forest:#173A2E;--cream:#F7F0E1;--coral:#E8604C;--ink:#1d1d1b;--muted:#6b6a64;--card:#fffdf8;--line:#e6dcc6;--bg:#f3ecdc}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ink:#f1ece0;--muted:#a9a397;--card:#1f2a25;--line:#2f3d36;--bg:#121a16}}}}
:root[data-theme="dark"]{{--ink:#f1ece0;--muted:#a9a397;--card:#1f2a25;--line:#2f3d36;--bg:#121a16}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,sans-serif}}
header{{background:var(--forest);color:#fff;padding:32px 16px 24px}}
.wrap{{max-width:980px;margin:0 auto;padding:0 16px}}
header .wrap{{padding:0}}
.kicker{{font-family:'Instrument Serif';font-style:italic;font-size:20px;color:var(--gold)}}
h1{{font-family:'Archivo Black';font-size:clamp(26px,5vw,40px);margin:4px 0 8px;letter-spacing:.5px}}
.stats{{display:flex;flex-wrap:wrap;gap:8px 20px;color:#d9e4dc;font-size:14px}}
.stats b{{color:var(--gold)}}
.bar{{display:flex;gap:2px;margin:20px 0 0;height:28px}}
.seg{{background:rgba(255,255,255,.12);color:#fff;text-decoration:none;font-size:11px;display:flex;align-items:center;justify-content:center;border-radius:4px;min-width:14px}}
.seg:hover{{background:var(--gold);color:var(--forest)}}
section.notes{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin:24px 0}}
section.notes h3{{margin:0 0 8px;font-family:'Archivo Black';font-size:16px}}
section.notes ul{{margin:0;padding-left:20px}}
.scene{{display:grid;grid-template-columns:200px 1fr;gap:20px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin:0 0 16px}}
.frame{{position:relative;border-radius:10px;overflow:hidden;aspect-ratio:9/16;background:#000}}
.frame img{{width:100%;height:100%;object-fit:cover;display:block}}
.cap{{position:absolute;left:6%;right:6%;top:13%;text-align:center;text-shadow:0 2px 8px rgba(0,0,0,.55)}}
.cap .lead{{display:block;font-family:'Instrument Serif';font-style:italic;color:#fff;font-size:15px;line-height:1.1}}
.cap .hero{{display:block;font-family:'Archivo Black';color:var(--gold);font-size:20px;line-height:1.05;text-transform:uppercase}}
.meta{{display:flex;align-items:baseline;flex-wrap:wrap;gap:6px 12px}}
.num{{font-family:'Archivo Black';color:var(--coral)}}
h2{{font-family:'Archivo Black';font-size:20px;margin:0}}
.time{{color:var(--muted);font-size:13px;margin-left:auto}}
.line{{font-family:'Instrument Serif';font-size:20px;line-height:1.3;margin:8px 0}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}}
.chip{{background:var(--gold);color:var(--forest);font-weight:600;font-size:12px;padding:2px 8px;border-radius:999px}}
dl{{display:grid;grid-template-columns:70px 1fr;gap:4px 12px;margin:0 0 12px;font-size:14px}}
dt{{color:var(--muted);font-weight:600}} dd{{margin:0}}
.review{{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;border-top:1px dashed var(--line);padding-top:10px;font-size:14px}}
.note{{flex:1 1 220px;min-width:0;padding:6px 10px;border:1px solid var(--line);border-radius:8px;background:transparent;color:var(--ink);font:inherit}}
.export{{position:sticky;bottom:0;background:var(--forest);color:#fff;padding:12px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
.export button{{background:var(--gold);color:var(--forest);border:0;border-radius:8px;padding:8px 14px;font:600 14px Inter;cursor:pointer}}
.export span{{font-size:13px;color:#d9e4dc}}
@media (max-width:640px){{.scene{{grid-template-columns:1fr}}.frame{{max-width:240px;margin:0 auto}}.time{{margin-left:0}}}}
</style></head><body>
<header><div class="wrap">
  <div class="kicker">Storyboard · v1</div>
  <h1>Diabetes mein kela aur aam?</h1>
  <div class="stats"><span>Dr. Sachi Tandon · Sachi Naturopathy</span>
    <span>Length <b>{fmt(total)}</b> (raw {fmt(edit['source_duration'])})</span>
    <span><b>{len(scenes)}</b> scenes · <b>{len(edit['keep_segments'])}</b> cuts kept</span>
    <span>9:16 · 1080×1920 · Hinglish captions</span></div>
  <nav class="bar">{bar}</nav>
</div></header>
<main class="wrap">
<section class="notes"><h3>Before I render</h3><ul>
  <li><b>Opening:</b> the first 3.5 s (silent banana moment) is cut so the hook starts on frame 1.</li>
  <li><b>Pauses:</b> every pause over ~0.15 s is trimmed, 69.5 s → 61.3 s. Natural breaths are kept so it doesn't sound robotic.</li>
  <li><b>Quality:</b> the source is a WhatsApp copy (576×1024). It will be upscaled to 1080×1920 and look a little soft. Sending the original phone file fixes this.</li>
  <li><b>Music:</b> not chosen yet. I'll use a calm, royalty-free acoustic track at −24 dB.</li>
  <li><b>End card:</b> shows “Sachi Naturopathy”. Add an Instagram handle or phone number if you want one.</li>
  <li><b>Health facts on screen</b> only repeat what Dr. Tandon says. No extra medical claims are added.</li>
</ul></section>
{''.join(cards)}
</main>
<div class="export"><button id="copy">Copy my notes</button><span id="msg">Mark scenes, then copy your notes and paste them into Claude.</span></div>
<script>
document.getElementById('copy').onclick = async () => {{
  const out = [];
  document.querySelectorAll('.scene').forEach(s => {{
    const id = s.id.slice(1), name = s.querySelector('h2').textContent;
    const pick = s.querySelector('input[type=radio]:checked').value;
    const note = s.querySelector('.note').value.trim();
    if (pick !== 'keep' || note) out.push(`Scene ${{id}} (${{name}}): ${{pick.toUpperCase()}}${{note ? ' - ' + note : ''}}`);
  }});
  const text = out.length ? 'Storyboard notes:\\n' + out.join('\\n') : 'Storyboard approved, render it.';
  try {{ await navigator.clipboard.writeText(text); document.getElementById('msg').textContent = 'Copied! Paste it into Claude.'; }}
  catch (e) {{ prompt('Copy this:', text); }}
}};
</script>
</body></html>"""
(HERE / "index.html").write_text(page, encoding="utf-8")
print("wrote", HERE / "index.html")
