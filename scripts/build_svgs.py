#!/usr/bin/env python3
"""Build the animated SVG assets for the profile README.

One source of truth for geometry and copy; two palettes (dark / light).
Writes assets/dark/*.svg and assets/light/*.svg.

    python scripts/build_svgs.py

Motion system - every panel uses only these three verbs:
  SETTLE  intro that plays once and freezes (SMIL, fill="freeze")
  FLOW    infinite ambient drift (dashed rails, particles)
  SWEEP   periodic oscilloscope pass across the panel

Load-bearing motion (text reveals, bar fills) is SMIL with safe static
defaults, so a renderer that ignores animation shows finished content
rather than blank content. CSS @keyframes are decorative-only.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W = 900

THEMES = {
    "dark": {
        "bg": "#0d1117", "panel": "#161b22", "line": "#30363d",
        "text": "#c9d1d9", "muted": "#8b949e", "blue": "#58a6ff",
        "green": "#3fb950", "amber": "#f0883e", "violet": "#bc8cff",
        "shim": "#ffffff", "shim_op": "0.10", "grid_op": "0.5",
    },
    "light": {
        "bg": "#ffffff", "panel": "#f6f8fa", "line": "#d0d7de",
        "text": "#1f2328", "muted": "#656d76", "blue": "#0969da",
        "green": "#1a7f37", "amber": "#bc4c00", "violet": "#8250df",
        "shim": "#0969da", "shim_op": "0.07", "grid_op": "0.8",
    },
}

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
ADV = 0.6  # monospace advance width as a fraction of font-size


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def head(h, extra_defs="", css=""):
    """Open an SVG with the shared style block."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img">\n'
        f"<style>\n"
        f"text{{font-family:{MONO}}}\n"
        f"@keyframes blink{{0%,45%{{opacity:1}}50%,95%{{opacity:0}}100%{{opacity:1}}}}\n"
        f".cur{{animation:blink 1.05s step-end infinite}}\n"
        f"{css}</style>\n{extra_defs}"
    )


def panel(t, h, rx=10):
    """Background plate + hairline border."""
    return (
        f'<rect width="{W}" height="{h}" rx="{rx}" fill="{t["bg"]}"/>'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="{rx}" '
        f'fill="none" stroke="{t["line"]}" opacity="{t["grid_op"]}"/>'
    )


def sweep(t, h, uid, dur="7s", begin="0s", rx=10):
    """SWEEP: an oscilloscope pass, clipped to the panel's rounded corners."""
    return (
        f'<defs><linearGradient id="sw{uid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["shim"]}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{t["shim"]}" stop-opacity="{t["shim_op"]}"/>'
        f'<stop offset="1" stop-color="{t["shim"]}" stop-opacity="0"/>'
        f"</linearGradient>"
        f'<clipPath id="cp{uid}"><rect width="{W}" height="{h}" rx="{rx}"/></clipPath>'
        f"</defs>"
        f'<g clip-path="url(#cp{uid})">'
        f'<rect x="-320" y="0" width="300" height="{h}" fill="url(#sw{uid})">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0;1240 0;1240 0" keyTimes="0;0.42;1" '
        f'dur="{dur}" begin="{begin}" repeatCount="indefinite"/>'
        f"</rect></g>"
    )


def rail(t, y1, y2, color=None, x=9):
    """FLOW: the signal spine down the left edge of every panel."""
    c = color or t["blue"]
    return (
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{c}" '
        f'stroke-width="3" stroke-linecap="round" stroke-dasharray="11 9" '
        f'opacity="0.85">'
        f'<animate attributeName="stroke-dashoffset" values="0;-40" '
        f'dur="1.9s" repeatCount="indefinite"/></line>'
    )


def rise(delay, dur="0.65s"):
    """SETTLE: fade a node in. Defaults to visible if SMIL is unsupported."""
    return (
        f'<animate attributeName="opacity" from="0" to="1" '
        f'begin="{delay}s" dur="{dur}" fill="freeze"/>'
    )


# --------------------------------------------------------------------------
# 01  header
# --------------------------------------------------------------------------

TAGLINES = [
    "building a voice AI that answers the phone in 300ms",
    "shipping outreach tooling to 13,000+ banking contacts",
    "calling squat depth with computer vision at 90% accuracy",
]


def header(t):
    h, fs = 210, 15
    adv = fs * ADV
    x0 = 40 + 2 * adv          # taglines start after the "$ " prompt
    widths = [len(s) * adv for s in TAGLINES]
    span, n = 6.0, len(TAGLINES)
    total = span * n

    defs = (
        f'<defs>'
        # drifting aurora behind the terminal
        f'<linearGradient id="aur" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{t["blue"]}" stop-opacity="0.16">'
        f'<animate attributeName="offset" values="0;0.35;0" dur="14s" repeatCount="indefinite"/></stop>'
        f'<stop offset="0.55" stop-color="{t["violet"]}" stop-opacity="0.13">'
        f'<animate attributeName="offset" values="0.55;0.8;0.55" dur="14s" repeatCount="indefinite"/></stop>'
        f'<stop offset="1" stop-color="{t["bg"]}" stop-opacity="0"/>'
        f"</linearGradient>"
        # CRT scanlines
        f'<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        f'<rect width="4" height="1" fill="{t["text"]}" opacity="0.055"/></pattern>'
        f'<filter id="glow" x="-25%" y="-60%" width="150%" height="220%">'
        f'<feGaussianBlur stdDeviation="3" result="b">'
        f'<animate attributeName="stdDeviation" values="2.2;5;2.2" dur="5.5s" repeatCount="indefinite"/>'
        f"</feGaussianBlur>"
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'<clipPath id="hc"><rect width="{W}" height="{h}" rx="10"/></clipPath>'
    )
    for i, wd in enumerate(widths):
        defs += (
            f'<clipPath id="typ{i}"><rect x="{x0}" y="150" width="0" height="26">'
            f'<animate attributeName="width" '
            f'values="0;0;{wd:.0f};{wd:.0f};0;0" '
            f'keyTimes="0;{i*span/total:.4f};{(i*span+1.8)/total:.4f};'
            f'{(i*span+4.6)/total:.4f};{(i*span+5.6)/total:.4f};1" '
            f'dur="{total:.0f}s" repeatCount="indefinite"/></rect></clipPath>'
        )
    defs += "</defs>"

    css = ("@keyframes drift{from{transform:translateY(0)}to{transform:translateY(-40px)}}\n"
           ".scan{animation:drift 9s linear infinite}\n")

    s = head(h, defs, css)
    s += panel(t, h)
    s += f'<g clip-path="url(#hc)">'
    s += f'<rect width="{W}" height="{h}" fill="url(#aur)"/>'
    s += f'<rect class="scan" y="-40" width="{W}" height="{h+80}" fill="url(#scan)"/></g>'

    # window chrome
    s += (f'<path d="M0 10a10 10 0 0 1 10-10h880a10 10 0 0 1 10 10v24H0z" fill="{t["panel"]}"/>'
          f'<line x1="0" y1="34" x2="{W}" y2="34" stroke="{t["line"]}"/>')
    for cx, col in ((20, "#ff5f56"), (40, "#ffbd2e"), (60, "#27c93f")):
        s += f'<circle cx="{cx}" cy="17" r="6" fill="{col}"/>'
    s += (f'<text x="450" y="22" font-size="12" fill="{t["muted"]}" '
          f'text-anchor="middle" letter-spacing="0.5">derek@github:~</text>')

    # identity
    s += (f'<text x="40" y="94" font-size="34" font-weight="700" letter-spacing="1.5" '
          f'fill="{t["blue"]}" filter="url(#glow)">Derek Sun{rise(0.1)}</text>')
    s += (f'<text x="40" y="124" font-size="14.5" fill="{t["text"]}" letter-spacing="0.3">'
          f'CS @ University of Toronto — AI specialization, Statistics minor{rise(0.35)}</text>')
    s += (f'<text x="40" y="146" font-size="12.5" fill="{t["muted"]}" letter-spacing="0.3">'
          f'2nd year · 3.93 GPA · Toronto, ON{rise(0.5)}</text>')

    # typing line
    s += f'<text x="40" y="170" font-size="{fs}" fill="{t["green"]}">${rise(0.7)}</text>'
    for i, tl in enumerate(TAGLINES):
        s += (f'<g clip-path="url(#typ{i})"><text x="{x0:.0f}" y="170" font-size="{fs}" '
              f'fill="{t["text"]}">{esc(tl)}</text></g>')

    # cursor rides the typing edge
    kt, vals = ["0"], [f"{x0:.0f}"]
    for i, wd in enumerate(widths):
        b = i * span
        for off, v in ((1.8, x0 + wd), (4.6, x0 + wd), (5.6, x0), (6.0, x0)):
            kt.append(f"{(b+off)/total:.4f}")
            vals.append(f"{v:.0f}")
    kt[-1], vals[-1] = "1", f"{x0:.0f}"
    s += (f'<rect class="cur" y="157" width="9" height="17" fill="{t["green"]}" x="{x0:.0f}">'
          f'<animate attributeName="x" values="{";".join(vals)}" '
          f'keyTimes="{";".join(kt)}" dur="{total:.0f}s" repeatCount="indefinite"/></rect>')
    s += sweep(t, h, "h", dur="9s", begin="1.2s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# 02  section rules  (s01 - s06)
# --------------------------------------------------------------------------

SECTIONS = [
    ("01", "WHOAMI"), ("02", "ECOSYSTEM"), ("03", "PROJECTS"),
    ("04", "TELEMETRY"), ("05", "THE ROUTE"), ("06", "STACK"),
]


def section(t, num, label):
    h = 46
    lx = 40 + 3 * 8.4                      # after the number
    tx = lx + (len(label) + 3) * 8.4 + 20  # where the rule starts
    rule = W - 30 - tx

    s = head(h)
    s += f'<rect width="{W}" height="{h}" rx="6" fill="{t["bg"]}"/>'
    s += (f'<rect x="12" y="14" width="4" height="18" rx="2" fill="{t["amber"]}">'
          f'<animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></rect>')
    s += (f'<text x="30" y="29" font-size="14" font-weight="700" letter-spacing="1" '
          f'fill="{t["amber"]}">{num}</text>')
    s += f'<text x="{lx:.0f}" y="29" font-size="14" fill="{t["line"]}">//</text>'
    s += (f'<text x="{lx+26:.0f}" y="29" font-size="14" font-weight="700" letter-spacing="3.2" '
          f'fill="{t["text"]}">{label}</text>')
    # SETTLE: the rule draws itself, then FLOW: dashes travel along it
    s += (f'<line x1="{tx:.0f}" y1="23" x2="{W-30}" y2="23" stroke="{t["line"]}" '
          f'stroke-width="2" stroke-dasharray="{rule:.0f}">'
          f'<animate attributeName="stroke-dashoffset" from="{rule:.0f}" to="0" '
          f'dur="0.9s" fill="freeze"/></line>')
    s += (f'<line x1="{tx:.0f}" y1="23" x2="{W-30}" y2="23" stroke="{t["blue"]}" '
          f'stroke-width="2" stroke-dasharray="14 26" opacity="0.75">'
          f'<animate attributeName="stroke-dashoffset" values="0;-40" dur="1.6s" '
          f'begin="0.9s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" from="0" to="0.75" begin="0.9s" dur="0.4s" fill="freeze"/></line>')
    s += (f'<rect x="{W-34}" y="19" width="8" height="8" rx="1.5" fill="{t["blue"]}">'
          f'<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" begin="0.9s" '
          f'repeatCount="indefinite"/></rect>')
    return s + "</svg>"


# --------------------------------------------------------------------------
# 03  whoami
# --------------------------------------------------------------------------

WHOAMI = [
    "2nd-year CS at UofT — AI specialization, Statistics minor, 3.93 GPA.",
    "Software Engineer Intern at Nova Vacation Homes: voice AI receptionist,",
    "RAG pipeline, smart-lock integrations. And at Maybole: AI outreach platform.",
    "Hackathons most weekends. 425 lb squat when I'm not at a keyboard.",
]


def whoami(t):
    h = 172
    s = head(h) + panel(t, h)
    s += rail(t, 24, h - 24)
    for i, ln in enumerate(WHOAMI):
        s += (f'<text x="34" y="{46+i*30}" font-size="14.5" fill="{t["text"]}" '
              f'letter-spacing="0.2">{esc(ln)}{rise(0.15 + i * 0.13)}</text>')
    s += sweep(t, h, "w", dur="8s", begin="2s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# 04  ecosystem
# --------------------------------------------------------------------------

NODES = [
    (150, 74, "Nova Vacation Homes", "start"),
    (438, 46, "Maybole", "middle"),
    (752, 74, "AWS x UofT — 1st", "end"),
    (240, 196, "UofT Powerlifting", "start"),
    (690, 196, "Hackathons", "end"),
]


def ecosystem(t):
    h, cx, cy = 250, 450, 128
    s = head(h) + panel(t, h)

    defs = "<defs>"
    for i, (x, y, _, _) in enumerate(NODES):
        defs += f'<path id="e{i}" d="M{x} {y} L{cx} {cy}" fill="none"/>'
    s += defs + "</defs>"

    # FLOW: connectors + particles converging on the centre
    for i, (x, y, label, anchor) in enumerate(NODES):
        s += (f'<line x1="{x}" y1="{y}" x2="{cx}" y2="{cy}" stroke="{t["line"]}" stroke-width="2"/>'
              f'<line x1="{x}" y1="{y}" x2="{cx}" y2="{cy}" stroke="{t["blue"]}" stroke-width="2" '
              f'stroke-dasharray="8 22" opacity="0.7">'
              f'<animate attributeName="stroke-dashoffset" values="0;-30" dur="1.5s" '
              f'repeatCount="indefinite"/></line>')
        s += (f'<circle r="2.6" fill="{t["blue"]}">'
              f'<animateMotion dur="3.2s" begin="{i*0.62:.2f}s" repeatCount="indefinite" '
              f'keyPoints="0;1" keyTimes="0;1" calcMode="linear">'
              f'<mpath xlink:href="#e{i}"/></animateMotion>'
              f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.8;1" '
              f'dur="3.2s" begin="{i*0.62:.2f}s" repeatCount="indefinite"/></circle>')

    # satellites
    for i, (x, y, label, anchor) in enumerate(NODES):
        ax = x + (12 if anchor == "start" else -12 if anchor == "end" else 0)
        s += (f'<circle cx="{x}" cy="{y}" r="6" fill="{t["blue"]}">'
              f'<animate attributeName="r" values="6;9;6" dur="2.6s" begin="{i*0.32:.2f}s" '
              f'repeatCount="indefinite"/></circle>')
        # knock the connector line out from behind the label so it stays legible
        s += (f'<text x="{ax}" y="{y-16 if anchor=="middle" else y+4}" font-size="12.5" '
              f'fill="{t["text"]}" text-anchor="{anchor}" stroke="{t["bg"]}" stroke-width="4" '
              f'paint-order="stroke fill">{esc(label)}{rise(0.2+i*0.1)}</text>')

    # centre: slow orbit ring + expanding sonar rings
    s += (f'<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{t["line"]}" '
          f'stroke-width="1.5" stroke-dasharray="4 10">'
          f'<animateTransform attributeName="transform" type="rotate" '
          f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="34s" repeatCount="indefinite"/></circle>')
    for k in range(3):
        s += (f'<circle cx="{cx}" cy="{cy}" fill="none" stroke="{t["green"]}" stroke-width="2" r="10">'
              f'<animate attributeName="r" values="10;46" dur="3s" begin="{k}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="0.55;0" dur="3s" begin="{k}s" '
              f'repeatCount="indefinite"/></circle>')
    s += f'<circle cx="{cx}" cy="{cy}" r="10" fill="{t["green"]}"/>'
    s += (f'<text x="{cx}" y="{cy+34}" font-size="13" font-weight="700" letter-spacing="1" '
          f'fill="{t["green"]}" text-anchor="middle">derek</text>')
    s += (f'<text x="{cx}" y="{cy+52}" font-size="11" fill="{t["muted"]}" '
          f'text-anchor="middle">you are here</text>')
    s += sweep(t, h, "e", dur="9s", begin="3s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# 05  projects
# --------------------------------------------------------------------------

PROJECTS = [
    ("T-Care", "1st place — AWS x UofT Hackathon",
     'Turns "I lost my TCard" into the exact campus office to visit.',
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
    h, step = 396, 88
    s = head(h) + panel(t, h)
    for i, (name, tag, l1, l2) in enumerate(PROJECTS):
        y = 30 + i * step
        d = 0.15 + i * 0.14
        # SETTLE: the accent bar grows to full height, then holds
        s += (f'<rect x="24" y="{y}" width="3" height="58" rx="1.5" fill="{t["blue"]}">'
              f'<animate attributeName="height" values="0;58" dur="0.6s" begin="{d}s" '
              f'keyTimes="0;1" calcMode="spline" keySplines="0.16 1 0.3 1" fill="freeze"/></rect>')
        s += (f'<text x="42" y="{y+16}" font-size="16" font-weight="700" letter-spacing="0.3" '
              f'fill="{t["blue"]}">{esc(name)}{rise(d)}</text>')
        s += (f'<text x="42" y="{y+36}" font-size="12" letter-spacing="0.4" '
              f'fill="{t["amber"]}">{esc(tag)}{rise(d+0.08)}</text>')
        s += (f'<text x="42" y="{y+56}" font-size="13" fill="{t["text"]}">{esc(l1)}{rise(d+0.14)}</text>')
        s += (f'<text x="42" y="{y+74}" font-size="13" fill="{t["muted"]}">{esc(l2)}{rise(d+0.2)}</text>')
    s += rail(t, 24, h - 24)
    s += sweep(t, h, "p", dur="10s", begin="1.5s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# 06  telemetry
# --------------------------------------------------------------------------

BARS = [("Python", 92), ("TypeScript", 85), ("React / Next.js", 80),
        ("PyTorch", 62), ("SQL", 70)]
BAR_X, BAR_W = 232, 560


def telemetry(t):
    h, step = 220, 36
    s = head(h) + panel(t, h)
    s += "<defs>"
    s += (f'<linearGradient id="shim" x1="0" y1="0" x2="1" y2="0">'
          f'<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
          f'<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.45"/>'
          f'<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>')
    for i, (_, pct) in enumerate(BARS):
        fw = BAR_W * pct / 100
        s += (f'<clipPath id="bc{i}"><rect x="{BAR_X}" y="{30+i*step}" '
              f'width="{fw:.0f}" height="16" rx="4"/></clipPath>')
    s += "</defs>"

    # faint quartile gridlines
    for q in (0.25, 0.5, 0.75, 1.0):
        gx = BAR_X + BAR_W * q
        s += (f'<line x1="{gx:.0f}" y1="22" x2="{gx:.0f}" y2="{22+len(BARS)*step-8}" '
              f'stroke="{t["line"]}" stroke-width="1" opacity="0.55"/>')

    for i, (label, pct) in enumerate(BARS):
        y = 30 + i * step
        fw = BAR_W * pct / 100
        d = 0.2 + i * 0.13
        s += f'<text x="24" y="{y+13}" font-size="13" fill="{t["text"]}">{esc(label)}{rise(d)}</text>'
        s += f'<rect x="{BAR_X}" y="{y}" width="{BAR_W}" height="16" rx="4" fill="{t["panel"]}"/>'
        # SETTLE: eased fill. Static width is the final value, so no-SMIL renders complete.
        s += (f'<rect x="{BAR_X}" y="{y}" width="{fw:.0f}" height="16" rx="4" fill="{t["blue"]}">'
              f'<animate attributeName="width" values="0;{fw:.0f}" dur="1.15s" begin="{d}s" '
              f'keyTimes="0;1" calcMode="spline" keySplines="0.16 1 0.3 1" fill="freeze"/></rect>')
        # SWEEP: shimmer runs along the bar once it has settled
        s += (f'<g clip-path="url(#bc{i})">'
              f'<rect x="{BAR_X-140}" y="{y}" width="120" height="16" fill="url(#shim)" opacity="0.55">'
              f'<animateTransform attributeName="transform" type="translate" '
              f'values="0 0;{BAR_W+280} 0;{BAR_W+280} 0" keyTimes="0;0.35;1" dur="5.5s" '
              f'begin="{d+1.2:.2f}s" repeatCount="indefinite"/></rect></g>')
        s += (f'<text x="{BAR_X+BAR_W+10}" y="{y+13}" font-size="12" fill="{t["muted"]}">'
              f'{pct}%{rise(d + 1.0, "0.5s")}</text>')
    s += rail(t, 24, h - 24)
    return s + "</svg>"


# --------------------------------------------------------------------------
# 07  timeline
# --------------------------------------------------------------------------

TIMELINE = [
    ("2025", "Started coding — first year at UofT", False),
    ("Jan 2026", "AI elderly fall-detection app", False),
    ("Feb 2026", "On-demand demo & testing environments", False),
    ("Mar 2026", "T-Care — 1st place, AWS x UofT Hackathon", False),
    ("Apr 2026", "Founding SWE Intern @ Maybole", False),
    ("May 2026", "SWE Intern @ Nova Vacation Homes", False),
    ("Jun 2026", "AI squat-depth judge (iOS) — in progress", True),
    ("May 2028", "Expected graduation — BSc CS + Stats minor", False),
]
RAIL_X, T_TOP, T_STEP = 148, 36, 32


def timeline(t):
    h = 300
    bottom = T_TOP + (len(TIMELINE) - 1) * T_STEP
    length = bottom - T_TOP
    s = head(h) + panel(t, h)

    # SETTLE: the rail draws itself top to bottom
    s += (f'<line x1="{RAIL_X}" y1="{T_TOP}" x2="{RAIL_X}" y2="{bottom}" stroke="{t["line"]}" '
          f'stroke-width="2" stroke-dasharray="{length}">'
          f'<animate attributeName="stroke-dashoffset" from="{length}" to="0" dur="1.5s" '
          f'fill="freeze"/></line>')

    for i, (when, what, live) in enumerate(TIMELINE):
        y = T_TOP + i * T_STEP
        d = 0.25 + i * 0.15
        col = t["green"] if live else t["blue"]
        s += (f'<text x="24" y="{y+4}" font-size="12" letter-spacing="0.3" '
              f'fill="{t["amber"]}">{when}{rise(d)}</text>')
        s += (f'<circle cx="{RAIL_X}" cy="{y}" r="4.5" fill="{col}">'
              f'<animate attributeName="r" values="0;7;4.5" dur="0.5s" begin="{d}s" '
              f'keyTimes="0;0.65;1" fill="freeze"/></circle>')
        if live:
            s += (f'<circle cx="{RAIL_X}" cy="{y}" r="4.5" fill="none" stroke="{t["green"]}" '
                  f'stroke-width="2">'
                  f'<animate attributeName="r" values="5;15" dur="2.2s" begin="{d}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0.7;0" dur="2.2s" begin="{d}s" '
                  f'repeatCount="indefinite"/></circle>')
        s += (f'<text x="{RAIL_X+18}" y="{y+4}" font-size="13" fill="{t["text"]}">'
              f'{esc(what)}{rise(d+0.06)}</text>')

    # FLOW: a read-head runs down the rail forever
    s += (f'<circle cx="{RAIL_X}" r="3" fill="{t["violet"]}" cy="{T_TOP}">'
          f'<animate attributeName="cy" values="{T_TOP};{bottom}" dur="5s" begin="1.8s" '
          f'repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.9;1" '
          f'dur="5s" begin="1.8s" repeatCount="indefinite"/></circle>')
    s += sweep(t, h, "t", dur="11s", begin="2.5s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# 08  experience
# --------------------------------------------------------------------------

EXPERIENCE = [
    ("Nova Vacation Homes", "Software Engineer Intern — May–Aug 2026",
     "Shipped a voice AI that answers 500+ calls; cut RAG latency from 40s to 300ms."),
    ("Maybole", "Founding Software Engineer Intern — Apr–Aug 2026",
     "Built an outreach platform connecting students to 13,000+ banking contacts."),
]


def experience(t):
    h = 230
    s = head(h) + panel(t, h)
    for i, (org, role, line) in enumerate(EXPERIENCE):
        y = 40 + i * 96
        d = 0.15 + i * 0.2
        s += (f'<rect x="24" y="{y-18}" width="3" height="66" rx="1.5" fill="{t["blue"]}">'
              f'<animate attributeName="height" values="0;66" dur="0.65s" begin="{d}s" '
              f'keyTimes="0;1" calcMode="spline" keySplines="0.16 1 0.3 1" fill="freeze"/></rect>')
        s += (f'<circle cx="{W-34}" cy="{y-6}" r="5" fill="{t["green"]}">'
              f'<animate attributeName="opacity" values="1;0.3;1" dur="1.8s" '
              f'begin="{i*0.4:.1f}s" repeatCount="indefinite"/></circle>')
        s += (f'<text x="{W-46}" y="{y-2}" font-size="11" fill="{t["green"]}" '
              f'text-anchor="end">current{rise(d+0.2)}</text>')
        s += (f'<text x="42" y="{y}" font-size="16" font-weight="700" letter-spacing="0.3" '
              f'fill="{t["blue"]}">{esc(org)}{rise(d)}</text>')
        s += (f'<text x="42" y="{y+20}" font-size="12" letter-spacing="0.3" '
              f'fill="{t["muted"]}">{esc(role)}{rise(d+0.08)}</text>')
        s += (f'<text x="42" y="{y+44}" font-size="13" fill="{t["text"]}">{esc(line)}{rise(d+0.14)}</text>')
    s += rail(t, 24, h - 24)
    s += sweep(t, h, "x", dur="9s", begin="2.2s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# 09  stack
# --------------------------------------------------------------------------

STACK = [
    ("Languages", "Python · TypeScript · JavaScript · Java · Swift · SQL · R · HTML/CSS"),
    ("Frameworks", "React · React Native · Next.js · Node.js · Express · FastAPI · PyTorch · MediaPipe"),
    ("Data / Infra", "PostgreSQL · pgvector · Redis · RabbitMQ · Docker"),
    ("Cloud & Tools", "AWS Bedrock · Git · REST · WebSockets · Twilio · Stripe · Google Maps API"),
]


def stack(t):
    h = 244
    s = head(h) + panel(t, h)
    for i, (cat, items) in enumerate(STACK):
        y = 40 + i * 48
        d = 0.15 + i * 0.14
        s += (f'<text x="34" y="{y}" font-size="12" letter-spacing="1.6" font-weight="700" '
              f'fill="{t["amber"]}">{esc(cat.upper())}{rise(d)}</text>')
        s += (f'<text x="34" y="{y+22}" font-size="13" fill="{t["text"]}">{esc(items)}{rise(d+0.1)}</text>')
        s += (f'<line x1="34" y1="{y+32}" x2="{W-30}" y2="{y+32}" stroke="{t["line"]}" '
              f'stroke-width="1" opacity="0.6"/>' if i < len(STACK) - 1 else "")
    s += rail(t, 24, h - 24)
    s += sweep(t, h, "s", dur="8.5s", begin="1.8s")
    return s + "</svg>"


# --------------------------------------------------------------------------
# 10  footer
# --------------------------------------------------------------------------

def footer(t):
    h = 80
    s = head(h) + panel(t, h)
    # live status dot with sonar rings
    for k in range(2):
        s += (f'<circle cx="34" cy="40" r="7" fill="none" stroke="{t["green"]}" stroke-width="2">'
              f'<animate attributeName="r" values="7;22" dur="2.4s" begin="{k*1.2}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="0.6;0" dur="2.4s" begin="{k*1.2}s" '
              f'repeatCount="indefinite"/></circle>')
    s += f'<circle cx="34" cy="40" r="7" fill="{t["green"]}"/>'
    s += (f'<text x="56" y="45" font-size="13.5" fill="{t["text"]}">'
          f'currently shipping voice AI at Nova and outreach tooling at Maybole</text>')

    # voice-level meter — the subject rendered literally
    heights = [10, 20, 32, 22, 14, 26, 18, 30, 12, 22, 16, 28]
    for i, hh in enumerate(heights):
        x = W - 40 - (len(heights) - i) * 11
        s += (f'<rect x="{x}" y="{40-hh/2:.0f}" width="5" height="{hh}" rx="2.5" fill="{t["blue"]}" '
              f'opacity="0.9">'
              f'<animate attributeName="height" values="{hh};{max(5,hh*0.3):.0f};{hh*1.15:.0f};{hh}" '
              f'dur="1.4s" begin="{i*0.11:.2f}s" repeatCount="indefinite"/>'
              f'<animate attributeName="y" '
              f'values="{40-hh/2:.0f};{40-max(5,hh*0.3)/2:.0f};{40-hh*1.15/2:.0f};{40-hh/2:.0f}" '
              f'dur="1.4s" begin="{i*0.11:.2f}s" repeatCount="indefinite"/></rect>')

    # a light travelling the border
    s += (f'<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="10" fill="none" '
          f'stroke="{t["green"]}" stroke-width="2" stroke-dasharray="90 1870" opacity="0.75">'
          f'<animate attributeName="stroke-dashoffset" values="0;-1960" dur="7s" '
          f'repeatCount="indefinite"/></rect>')
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
            "ecosystem.svg": ecosystem(t),
            "projects.svg": projects(t),
            "telemetry.svg": telemetry(t),
            "timeline.svg": timeline(t),
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
    paths = build()
    for p in sorted(paths):
        print(f"  wrote {p}")
    print(f"\n{len(paths)} files")
