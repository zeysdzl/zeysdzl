"""Render assets/contributions.svg: a pink contribution calendar + weekday rhythm.

Stdlib only. Needs GH_TOKEN (or GITHUB_TOKEN) and optionally GH_USER.
"""
import base64, datetime as dt, json, os, pathlib, urllib.request

USER = os.environ.get("GH_USER", "zeysdzl")
TOKEN = os.environ.get("GH_TOKEN") or os.environ["GITHUB_TOKEN"]
HERE = pathlib.Path(__file__).parent
OUT = HERE.parent.parent / "assets" / "contributions.svg"

C = dict(bg="#fff6f9", card="#ffe8f0", ink="#c2366f", soft="#a8637f", accent="#f0609a",
         levels=["#ffe1eb", "#ffc0d5", "#ff94b6", "#f4679a", "#d8427c"])

Q = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount weekday}}}}}}"""
req = urllib.request.Request("https://api.github.com/graphql",
    data=json.dumps({"query": Q, "variables": {"u": USER}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-graph"})
cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks = [w["contributionDays"] for w in cal["weeks"]]
days = [d for w in weeks for d in w]
total = cal["totalContributions"]

# ---- stats -------------------------------------------------------------
nz = sorted(d["contributionCount"] for d in days if d["contributionCount"])
def level(n):
    if not n: return 0
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)] if nz else [1, 2, 3]
    return 1 + sum(n > t for t in q)

longest = run = 0
for d in days:
    run = run + 1 if d["contributionCount"] else 0
    longest = max(longest, run)
current = 0
for d in reversed(days):
    if d["contributionCount"]: current += 1
    elif current or d is not days[-1]: break  # today may still be empty
best = max(days, key=lambda d: d["contributionCount"])
best_date = dt.date.fromisoformat(best["date"])
active = sum(1 for d in days if d["contributionCount"])

by_wd = [0] * 7  # GitHub: 0 = Sunday
for d in days: by_wd[d["weekday"]] += d["contributionCount"]
order = [1, 2, 3, 4, 5, 6, 0]
names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
top_wd = max(order, key=lambda i: by_wd[i])

# ---- svg ---------------------------------------------------------------
def font(name, fam, style="normal", weight=400):
    b = base64.b64encode((HERE / "fonts" / f"{name}.woff2").read_bytes()).decode()
    return f"@font-face{{font-family:{fam};font-style:{style};font-weight:{weight};src:url(data:font/woff2;base64,{b})}}"

W, H = 1200, 560
cell, gap = 15, 4
step = cell + gap
x0, y0 = 84, 196
o = []
o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
o.append("<style>" + font("nyght", "N") + font("nyght-italic", "N", "italic") + font("uncut", "U") +
         font("uncut-medium", "U", weight=500) + f"""
text{{font-family:U,sans-serif;fill:{C['soft']};font-size:14px;letter-spacing:-.01em}}
.s{{font-family:N,serif;font-weight:300;fill:{C['ink']};letter-spacing:-.04em}}
.a{{fill:{C['accent']}}}
.c{{transform-box:fill-box;transform-origin:center;animation:pop .5s cubic-bezier(.2,.8,.2,1.2) both}}
.b{{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.8,.2,1) both}}
@keyframes pop{{from{{opacity:0;transform:scale(.3)}}}}
@keyframes grow{{from{{transform:scaleY(0)}}}}
</style>""")
o.append(f'<rect width="{W}" height="{H}" rx="28" fill="{C["bg"]}"/>')

# header
o.append(f'<text x="{x0}" y="62">04 · Contributions</text>')
o.append(f'<text class="s" x="{x0 - 3}" y="122" style="font-size:58px">A year of <tspan font-style="italic">building</tspan></text>')
o.append(f'<text class="s" x="{W - 72}" y="118" style="font-size:72px" text-anchor="end">{total:,}</text>')
o.append(f'<text x="{W - 72}" y="148" text-anchor="end">contributions in the last year</text>')

# months
last_m = None
for wi, w in enumerate(weeks):
    m = dt.date.fromisoformat(w[0]["date"]).month
    if m != last_m and wi < len(weeks) - 2:
        if last_m is not None or w[0]["weekday"] == 0:
            o.append(f'<text x="{x0 + wi * step}" y="{y0 - 12}" style="font-size:12px">{dt.date(2000, m, 1):%b}</text>')
        last_m = m
for r, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    o.append(f'<text x="{x0 - 12}" y="{y0 + r * step + 11}" style="font-size:12px" text-anchor="end">{lab}</text>')

# cells
for wi, w in enumerate(weeks):
    for d in w:
        n = d["contributionCount"]
        x, y = x0 + wi * step, y0 + d["weekday"] * step
        o.append(f'<rect class="c" style="animation-delay:{wi * 18}ms" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4.5" '
                 f'fill="{C["levels"][level(n)]}"><title>{n} on {d["date"]}</title></rect>')

# legend
lx, ly = x0 + len(weeks) * step - 5 * step - 34, y0 + 7 * step + 22
o.append(f'<text x="{lx - 10}" y="{ly + 12}" style="font-size:12px" text-anchor="end">Less</text>')
for i, col in enumerate(C["levels"]):
    o.append(f'<rect x="{lx + i * step}" y="{ly}" width="{cell}" height="{cell}" rx="4.5" fill="{col}"/>')
o.append(f'<text x="{lx + 5 * step + 6}" y="{ly + 12}" style="font-size:12px">More</text>')

# stats
sy = 420
stats = [(f"{longest}", "day longest streak"), (f"{current}", "day current streak"),
         (f"{active}", "active days"), (f"{best['contributionCount']}", f"best day · {best_date.day} {best_date:%b}")]
for i, (big, small) in enumerate(stats):
    x = x0 + i * 150
    o.append(f'<text class="s" x="{x - 2}" y="{sy + 40}" style="font-size:52px">{big}</text>')
    o.append(f'<text x="{x}" y="{sy + 72}">{small}</text>')

# weekday rhythm
bx, bw, bg, bh = 760, 34, 14, 92
peak = max(by_wd) or 1
o.append(f'<text x="{bx}" y="{sy - 26}">Busiest on <tspan class="a" font-weight="500">{names[top_wd]}days</tspan></text>')
for i, wd in enumerate(order):
    v, x = by_wd[wd], bx + i * (bw + bg)
    h = max(6, round(bh * v / peak))
    fill = C["levels"][4] if wd == top_wd else C["levels"][2]
    o.append(f'<rect x="{x}" y="{sy - 6}" width="{bw}" height="{bh}" rx="10" fill="{C["card"]}"/>')
    o.append(f'<rect class="b" style="animation-delay:{300 + i * 70}ms" x="{x}" y="{sy - 6 + bh - h}" width="{bw}" height="{h}" rx="10" fill="{fill}"><title>{v} on {names[wd]}days</title></rect>')
    o.append(f'<text x="{x + bw / 2}" y="{sy + bh + 16}" style="font-size:12px" text-anchor="middle">{names[wd][0]}</text>')

o.append("</svg>")
OUT.parent.mkdir(exist_ok=True)
OUT.write_text("\n".join(o), encoding="utf-8")
print(f"wrote {OUT} · {total} contributions")
