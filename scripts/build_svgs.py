#!/usr/bin/env python3
"""Build the animated SVG assets for the profile README.

One source of truth for geometry and copy; two palettes (dark / light).
Writes assets/dark/*.svg and assets/light/*.svg.

    python scripts/build_svgs.py

Design: monochrome. No colour, no fills, no plates — the panels are
transparent so they sit on GitHub's own canvas in either theme.
Hierarchy comes from weight, scale, letter-spacing and hairlines.

Motion is restrained to three moves:
  DRAW    hairlines stroke themselves in, once, then freeze
  RISE    type fades up a few pixels, staggered, once, then freeze
  SCAN    a single 1px hairline crosses the panel on a long interval

Load-bearing motion (text reveals, rule draws) is SMIL with safe static
defaults, so a renderer that ignores animation shows finished content
rather than blank content. CSS @keyframes are decorative-only.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W = 900

THEMES = {
    # ink = primary marks, mid = secondary, faint = hairlines
    "dark": {"ink": "#ffffff", "mid": "#9a9a9a", "faint": "#3d3d3d"},
    "light": {"ink": "#000000", "mid": "#5a5a5a", "faint": "#cfcfcf"},
}

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
ADV = 0.6  # monospace advance width as a fraction of font-size


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def head(h, defs="", css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img">\n'
        f"<style>\n"
        f"text{{font-family:{MONO}}}\n"
        f"@keyframes blink{{0%,45%{{opacity:1}}50%,95%{{opacity:0}}100%{{opacity:1}}}}\n"
        f".cur{{animation:blink 1.1s step-end infinite}}\n"
        f"{css}</style>\n{defs}"
    )


def _staged(attr, hidden, shown, delay, dur, splines=False, extra=""):
    """A reveal that holds its hidden state from t=0 rather than using begin=.

    Using begin= would leave the element at its *static* value until the
    animation starts, which paints the finished state for `delay` seconds and
    then snaps to hidden - a visible flash. Holding the hidden value across a
    leading keyTimes segment avoids that while keeping the static attribute at
    the finished value, so no-SMIL renderers still show completed content.
    """
    total = delay + dur
    k = (delay / total) if total else 0.0
    tag = ("<animateTransform attributeName=\"%s\" type=\"translate\"" % attr
           if attr == "transform" else "<animate attributeName=\"%s\"" % attr)
    spline = (' calcMode="spline" keySplines="0 0 1 1;0.16 1 0.3 1"' if splines else "")
    return (f'{tag} values="{hidden};{hidden};{shown}" '
            f'keyTimes="0;{k:.4f};1" dur="{total:.2f}s"{spline}{extra} fill="freeze"/>')


def rise(delay, dur=0.6):
    """RISE: fade a node in. Defaults to visible if SMIL is unsupported."""
    return _staged("opacity", "0", "1", delay, dur)


def draw(x1, y1, x2, y2, colour, width=1, delay=0.0, dur=0.9):
    """DRAW: a hairline that strokes itself in. Renders complete without SMIL."""
    length = abs(x2 - x1) + abs(y2 - y1)
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" '
            f'stroke-width="{width}" stroke-dasharray="{length}">'
            f'{_staged("stroke-dashoffset", str(length), "0", delay, dur)}</line>')


def scan(t, h, dur="13s", begin="2s"):
    """SCAN: one hairline crossing the panel, then a long pause."""
    return (f'<line x1="0" y1="0" x2="0" y2="{h}" stroke="{t["ink"]}" '
            f'stroke-width="1" opacity="0.14">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{W} 0;{W} 0" keyTimes="0;0.28;1" '
            f'dur="{dur}" begin="{begin}" repeatCount="indefinite"/></line>')


# --------------------------------------------------------------------------
# header
# --------------------------------------------------------------------------

NAME = "Derek Sun"
TAGLINES = [
    "building a voice AI that answers the phone in 300ms",
    "shipping outreach tooling to 13,000+ banking contacts",
    "calling squat depth with computer vision at 90% accuracy",
]


def header(t):
    h = 200
    fs = 15
    adv = fs * ADV
    x0 = 40 + 2 * adv
    widths = [len(s) * adv for s in TAGLINES]
    span, n = 6.0, len(TAGLINES)
    total = span * n

    defs = "<defs>"
    for i, wd in enumerate(widths):
        defs += (
            f'<clipPath id="t{i}"><rect x="{x0}" y="158" width="0" height="26">'
            f'<animate attributeName="width" values="0;0;{wd:.0f};{wd:.0f};0;0" '
            f'keyTimes="0;{i*span/total:.4f};{(i*span+1.8)/total:.4f};'
            f'{(i*span+4.6)/total:.4f};{(i*span+5.6)/total:.4f};1" '
            f'dur="{total:.0f}s" repeatCount="indefinite"/></rect></clipPath>'
        )
    defs += "</defs>"

    s = head(h, defs)

    # the name resolves one character at a time
    nfs, nls = 40, 4
    step = nfs * ADV + nls
    for i, ch in enumerate(NAME):
        if ch == " ":
            continue
        s += (f'<text x="{40 + i*step:.1f}" y="70" font-size="{nfs}" font-weight="700" '
              f'fill="{t["ink"]}">{ch}'
              f'{rise(0.05 * i, 0.4)}'
              f'{_staged("transform", "0 9", "0 0", 0.05 * i, 0.5, splines=True)}'
              f"</text>")

    s += draw(40, 92, W - 40, 92, t["faint"], 1, delay=0.5, dur=1.1)
    s += (f'<text x="40" y="118" font-size="14" fill="{t["ink"]}" letter-spacing="0.3">'
          f'Computer Science @ University of Toronto — Statistics minor{rise(0.7)}</text>')
    s += (f'<text x="40" y="140" font-size="12.5" fill="{t["mid"]}" letter-spacing="0.3">'
          f'B.Sc. expected May 2028 · Toronto, ON{rise(0.85)}</text>')

    # the one looping element
    s += f'<text x="40" y="176" font-size="{fs}" fill="{t["mid"]}">${rise(1.0)}</text>'
    # textLength pins the advance width, so the cursor lands exactly at the end
    # of the text whatever monospace face the viewer's platform resolves to.
    for i, tl in enumerate(TAGLINES):
        s += (f'<g clip-path="url(#t{i})"><text x="{x0:.0f}" y="176" font-size="{fs}" '
              f'textLength="{widths[i]:.0f}" lengthAdjust="spacing" '
              f'fill="{t["ink"]}">{esc(tl)}</text></g>')

    kt, vals = ["0"], [f"{x0:.0f}"]
    for i, wd in enumerate(widths):
        b = i * span
        for off, v in ((1.8, x0 + wd), (4.6, x0 + wd), (5.6, x0), (6.0, x0)):
            kt.append(f"{(b+off)/total:.4f}")
            vals.append(f"{v:.0f}")
    kt[-1], vals[-1] = "1", f"{x0:.0f}"
    s += (f'<rect class="cur" y="163" width="9" height="17" fill="{t["ink"]}" x="{x0:.0f}">'
          f'<animate attributeName="x" values="{";".join(vals)}" keyTimes="{";".join(kt)}" '
          f'dur="{total:.0f}s" repeatCount="indefinite"/></rect>')
    s += scan(t, h, dur="15s", begin="2.5s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# section rules
# --------------------------------------------------------------------------

SECTIONS = [("01", "WHOAMI"), ("02", "PROJECTS"),
            ("03", "EXPERIENCE"), ("04", "STACK")]


def section(t, num, label):
    h = 44
    lx = 40 + 3 * 8.4
    tx = lx + (len(label) + 3) * 8.4 + 18
    s = head(h)
    s += (f'<rect x="16" y="16" width="4" height="12" fill="{t["ink"]}">{rise(0.05)}</rect>')
    s += (f'<text x="32" y="27" font-size="13" font-weight="700" letter-spacing="1" '
          f'fill="{t["mid"]}">{num}{rise(0.1)}</text>')
    s += (f'<text x="{lx:.0f}" y="27" font-size="13" font-weight="700" letter-spacing="3.4" '
          f'fill="{t["ink"]}">{label}{rise(0.18)}</text>')
    s += draw(tx, 22, W - 30, 22, t["faint"], 1, delay=0.28, dur=0.9)
    return s + "</svg>"


# --------------------------------------------------------------------------
# whoami
# --------------------------------------------------------------------------

WHOAMI = [
    "Computer Science student @ University of Toronto with a Statistics minor.",
    "I enjoy building practical software and exploring how AI can be used to solve real problems.",
    "I'm always looking to learn, build, and collaborate on meaningful projects.",
]


def whoami(t):
    h = 124
    s = head(h)
    s += draw(10, 22, 10, h - 22, t["faint"], 2, delay=0.05, dur=0.8)
    for i, ln in enumerate(WHOAMI):
        s += (f'<text x="34" y="{38+i*30}" font-size="14" fill="{t["ink"]}" '
              f'letter-spacing="0.2">{esc(ln)}{rise(0.2 + i * 0.14)}</text>')
    s += scan(t, h, dur="14s", begin="3s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# projects
# --------------------------------------------------------------------------

PROJECTS = [
    ("T-Care", "1st place — AWS x UofT Hackathon",
     "Turns “I lost my TCard” into the exact campus office to visit.",
     "Bedrock + React/Node, routing across 30+ services."),
    ("Fall Detection App", "React Native + TCN",
     "Catches a fall from motion data in real time,",
     "streaming sensor input at 50 Hz."),
    ("Demo & Test Environments", "Docker + Postgres",
     "Spins up realistic, disposable demo environments",
     "so teams stop testing against real user data."),
    ("Squat-Depth Judge (iOS)", "Swift + MediaPipe",
     "Judges squat depth from video the way a meet ref would.",
     "~90% accurate across 100+ labelled clips."),
]


def projects(t):
    h, step = 364, 84
    s = head(h)
    for i, (name, tag, l1, l2) in enumerate(PROJECTS):
        y = 28 + i * step
        d = 0.15 + i * 0.13
        s += (f'<rect x="24" y="{y-14}" width="2" height="62" fill="{t["ink"]}">'
              f'{_staged("height", "0", "62", d, 0.6, splines=True)}</rect>')
        s += (f'<text x="42" y="{y}" font-size="15.5" font-weight="700" letter-spacing="0.3" '
              f'fill="{t["ink"]}">{esc(name)}{rise(d)}</text>')
        s += (f'<text x="42" y="{y+20}" font-size="11.5" letter-spacing="1.2" '
              f'fill="{t["mid"]}">{esc(tag.upper())}{rise(d+0.07)}</text>')
        s += (f'<text x="42" y="{y+40}" font-size="13" fill="{t["ink"]}">{esc(l1)}{rise(d+0.13)}</text>')
        s += (f'<text x="42" y="{y+58}" font-size="13" fill="{t["mid"]}">{esc(l2)}{rise(d+0.18)}</text>')
    s += draw(10, 22, 10, h - 22, t["faint"], 2, delay=0.05, dur=1)
    s += scan(t, h, dur="16s", begin="3.5s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# experience
# --------------------------------------------------------------------------

EXPERIENCE = [
    ("Nova Vacation Homes", "Software Engineer Intern — May–Aug 2026",
     "Shipped a voice AI that answers 500+ calls; cut RAG latency from 40s to 300ms."),
    ("Maybole", "Founding Software Engineer Intern — Apr–Aug 2026",
     "Built an outreach platform connecting students to 13,000+ banking contacts."),
]


def experience(t):
    h = 192
    s = head(h)
    for i, (org, role, line) in enumerate(EXPERIENCE):
        y = 36 + i * 88
        d = 0.15 + i * 0.18
        s += (f'<rect x="24" y="{y-14}" width="2" height="60" fill="{t["ink"]}">'
              f'{_staged("height", "0", "60", d, 0.6, splines=True)}</rect>')
        s += (f'<text x="42" y="{y}" font-size="15.5" font-weight="700" letter-spacing="0.3" '
              f'fill="{t["ink"]}">{esc(org)}{rise(d)}</text>')
        s += (f'<text x="42" y="{y+20}" font-size="11.5" letter-spacing="1.2" '
              f'fill="{t["mid"]}">{esc(role.upper())}{rise(d+0.07)}</text>')
        s += (f'<text x="42" y="{y+42}" font-size="13" fill="{t["ink"]}">{esc(line)}{rise(d+0.13)}</text>')
        # a quiet marker for "this is live"
        s += (f'<circle cx="{W-34}" cy="{y-5}" r="3.5" fill="{t["ink"]}">'
              f'<animate attributeName="opacity" values="1;0.25;1" dur="2.6s" '
              f'begin="{i*0.5:.1f}s" repeatCount="indefinite"/></circle>')
        s += (f'<text x="{W-46}" y="{y-1}" font-size="10.5" letter-spacing="1.4" '
              f'fill="{t["mid"]}" text-anchor="end">CURRENT{rise(d+0.2)}</text>')
    s += draw(10, 22, 10, h - 22, t["faint"], 2, delay=0.05, dur=0.9)
    s += scan(t, h, dur="15s", begin="4s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# stack
# --------------------------------------------------------------------------

STACK = [
    ("Languages", "Python · TypeScript · JavaScript · Java · Swift · SQL · R · HTML/CSS"),
    ("Frameworks", "React · React Native · Next.js · Node.js · Express · FastAPI · PyTorch · MediaPipe"),
    ("Data / Infra", "PostgreSQL · pgvector · Redis · RabbitMQ · Docker"),
    ("Cloud & Tools", "AWS Bedrock · Git · REST · WebSockets · Twilio · Stripe · Google Maps API"),
]


def stack(t):
    h, step = 216, 46
    s = head(h)
    for i, (cat, items) in enumerate(STACK):
        y = 32 + i * step
        d = 0.15 + i * 0.12
        s += (f'<text x="34" y="{y}" font-size="11" letter-spacing="1.8" font-weight="700" '
              f'fill="{t["mid"]}">{esc(cat.upper())}{rise(d)}</text>')
        s += (f'<text x="34" y="{y+21}" font-size="13" fill="{t["ink"]}">{esc(items)}{rise(d+0.09)}</text>')
        if i < len(STACK) - 1:
            s += draw(34, y + 32, W - 30, y + 32, t["faint"], 1, delay=d + 0.16, dur=0.7)
    s += draw(10, 18, 10, h - 20, t["faint"], 2, delay=0.05, dur=0.9)
    s += scan(t, h, dur="14s", begin="4.5s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------

def footer(t):
    h = 76
    s = head(h)
    s += draw(0, 1, W, 1, t["faint"], 1, delay=0.05, dur=1.1)
    s += (f'<circle cx="26" cy="42" r="4" fill="{t["ink"]}">'
          f'<animate attributeName="opacity" values="1;0.2;1" dur="2.4s" repeatCount="indefinite"/></circle>')
    s += (f'<text x="44" y="46" font-size="13" fill="{t["ink"]}">'
          f'currently shipping voice AI at Nova and outreach tooling at Maybole{rise(0.3)}</text>')

    # a quiet level meter — the voice work, rendered literally
    bars = [8, 16, 26, 18, 11, 22, 14, 24, 10]
    for i, bh in enumerate(bars):
        x = W - 34 - (len(bars) - i) * 9
        lo = max(4, bh * 0.35)
        s += (f'<rect x="{x}" y="{42-bh/2:.0f}" width="3" height="{bh}" fill="{t["ink"]}" '
              f'opacity="0.75">'
              f'<animate attributeName="height" values="{bh};{lo:.0f};{bh}" dur="1.8s" '
              f'begin="{i*0.13:.2f}s" repeatCount="indefinite"/>'
              f'<animate attributeName="y" values="{42-bh/2:.0f};{42-lo/2:.0f};{42-bh/2:.0f}" '
              f'dur="1.8s" begin="{i*0.13:.2f}s" repeatCount="indefinite"/></rect>')
    return s + "</svg>"


# --------------------------------------------------------------------------

def build():
    written = []
    for theme, t in THEMES.items():
        out = ROOT / "assets" / theme
        out.mkdir(parents=True, exist_ok=True)
        files = {
            "header-v1.svg": header(t),
            "whoami.svg": whoami(t),
            "projects.svg": projects(t),
            "experience.svg": experience(t),
            "stack.svg": stack(t),
            "footer.svg": footer(t),
        }
        for num, label in SECTIONS:
            files[f"s{num}.svg"] = section(t, num, label)
        for name, body in files.items():
            (out / name).write_text(body, encoding="utf-8")
            written.append(f"assets/{theme}/{name}")
    return written


if __name__ == "__main__":
    for p in sorted(build()):
        print(f"  wrote {p}")
