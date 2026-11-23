"""Render assets/ticker.svg: an animated 'currently ...' line in the profile palette."""
import base64, pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent.parent / "assets" / "ticker.svg"
PHRASES = ["shipping Davetiye Dijital", "writing Selenium suites", "teaching YOLO to see",
           "automating the boring parts", "cutting AI films after hours"]
EACH = 2.8  # seconds per phrase
N = len(PHRASES)
T = EACH * N


def font(name, fam, style="normal"):
    b = base64.b64encode((HERE / "fonts" / f"{name}.woff2").read_bytes()).decode()
    return f"@font-face{{font-family:{fam};font-style:{style};src:url(data:font/woff2;base64,{b})}}"


# one visible slot per phrase: slide up in, hold, slide up out
a, b, c = 100 / N * 0.12, 100 / N * 0.88, 100 / N
kf = (f"@keyframes cycle{{0%{{opacity:0;transform:translateY(18px)}}{a:.2f}%{{opacity:1;transform:none}}"
      f"{b:.2f}%{{opacity:1;transform:none}}{c:.2f}%,100%{{opacity:0;transform:translateY(-18px)}}}}")
petals = "".join(f'<ellipse cx="0" cy="-7" rx="5" ry="7" fill="#f0609a" transform="rotate({r})"/>' for r in range(0, 360, 72))
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="84" viewBox="0 0 1200 84">
<style>{font('uncut', 'U')}{font('nyght-italic', 'N', 'italic')}
text{{font-family:U,sans-serif;font-size:22px;fill:#a8637f;letter-spacing:-.01em}}
.p{{font-family:N,serif;font-style:italic;font-size:34px;fill:#c2366f;letter-spacing:-.03em;opacity:0;animation:cycle {T}s infinite}}
.f{{animation:spin 6s linear infinite;transform-box:fill-box;transform-origin:center}}
{kf}@keyframes spin{{to{{transform:rotate(360deg)}}}}
</style>
<rect width="1200" height="84" rx="42" fill="#ffe8f0"/>
<g transform="translate(46 42)"><g class="f">{petals}<circle r="3.6" fill="#fff6f9"/></g></g>
<text x="76" y="50">currently</text>
""" + "".join(f'<text class="p" x="186" y="54" style="animation-delay:{i * EACH}s">{p}…</text>' for i, p in enumerate(PHRASES)) + """
</svg>"""
OUT.write_text(svg, encoding="utf-8")
print("wrote", OUT)
