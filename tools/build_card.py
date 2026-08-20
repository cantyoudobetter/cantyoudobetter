#!/usr/bin/env python3
"""Build assets/card.svg -- the terminal-style profile card.

GitHub markdown strips CSS, so the styled layout is rendered into an SVG that
is committed to the repo and referenced with <img> from README.md.

Sizing constraint: GitHub's profile-README column maxes out at ~846px wide, and
an <img> is scaled down to fit it. So the card's *character density* -- not its
pixel size -- decides legibility. Keep W near LEGIBLE_W and keep value lines
under VALUE_COLS; the assert at the bottom guards this.

    python3 tools/build_card.py
"""
import os, html, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

LEGIBLE_W = 846          # GitHub profile README container width
VALUE_COLS = 45          # max chars in a value line

# ---------------------------------------------------------------- palette
BG, CARD, BORDER = "#06070a", "#0a0d12", "#1b2230"
DIM, FG, WHITE, ART = "#6e7681", "#adbac7", "#e6edf3", "#9aa7b4"
GREEN, BLUE, CYAN = "#7ee787", "#79c0ff", "#56d4dd"
MAG, PINK, ORANGE, YELLOW = "#d2a8ff", "#ff7bd7", "#ffa657", "#e3b341"
MONO = ("'SF Mono','SFMono-Regular',ui-monospace,'DejaVu Sans Mono',"
        "Menlo,Consolas,'Liberation Mono',monospace")

HANDLE = "cantyoudobetter"
SEP    = "  ·  "

def P(t, c=FG):  return [(t, c)]                      # a plain line
def B(t, c=FG):  return [(">  ", DIM), (t, c)]        # a bulleted line
def J(*parts):                                        # join with dim separators
    out = []
    for i, p in enumerate(parts):
        if i: out.append((SEP, DIM))
        out.append(p if isinstance(p, tuple) else (p, FG))
    return out

DIV = (None, None, None)

ROWS = [
    ("Role:",      GREEN, [P("CTO @ Ways2Well + ReviveRX")]),
    ("Home Base:", GREEN, [P("Texas / wherever the airplane lands")]),
    ("Education:", GREEN, [[("Texas A&M ", FG), ("— Mechanical Engineering", DIM)]]),
    DIV,
    ("Platform.Shifts:", BLUE,
        [P("8-bit → PC → mainframe → web → mobile → AI")]),
    ("Shipped.To:", BLUE, [P("500K+ practitioners & patients"),
                           P("100K+ construction pros")]),
    ("Patents:", BLUE, [[("4 granted", FG),
                         ("  —  glucose, trucking, dispensing", DIM)]]),
    ("Exits:", BLUE, [[("5", FG),
                       ("  —  founded, built, grown", DIM)]]),
    DIV,
    ("Languages.Code:",  BLUE, [P("Python, C#, Java, JavaScript/TypeScript,"),
                                [("SQL, Ruby, Lua ", FG),
                                 ("+ whatever the job needs", DIM)]]),
    ("Languages.Human:", BLUE, [J("English", "Engineer", "Chilton"),
                                J("Hex", "NOTAM", "METAR")]),
    DIV,
    ("Currently:", GREEN, [B("AI-native healthcare platform"),
                           B("Clinical intimacy at scale"),
                           B("Human optimization + longevity"),
                           B("Agentic systems that cut friction"),
                           B("Developer experience that doesn't suck"),
                           B("Still writing actual code", WHITE)]),
    DIV,
    ("Previously:", BLUE, [B("Healthcare systems"), B("Pharmacy robotics + remote dispensing"),
                           B("EHRs before SaaS was cool"), B("Enterprise architecture"),
                           B("Non-invasive blood glucose monitor"), B("Construction tech")]),
    DIV,
    ("Side.Quests:", GREEN, [J(("Airplanes ✈", CYAN), "Handbuilt Race Cars"),
                             J("Sailing", "Camping", "Snowboarding"),
                             J("Running", "Cooking", "Writing")]),
    DIV,
    ("Books:", ORANGE, [J("The Black Swan", "Garden of Lies")]),
    DIV,
    ("Long.Game:", YELLOW, [P("Live long enough to die on Mars")]),
]

# blocks stacked under the portrait in the left pane
LEFT_BLOCKS = [
    ("Current.Hypothesis:", PINK, ["Technology's highest purpose may be to",
                                   "create the conditions in which humans",
                                   "can afford to be more human."], False),
    ("Status:", GREEN, ["Still curious.", "Still sharpening the stone."], True),
]

# footer laid out 2x2 so each cell gets half the card width
FAMILY = [("Sheri",   "Events By Sheri, LLC"),
          ("Blake",   "AI PhD, Researcher at SpaceXAI"),
          ("Camilla", "Polymath Economist"),
          ("Grant",   "Tech and Ops at SF 49ers"),
          ("Jayce",   "Tech Lead @ TasteLabs"),
          ("Zoe",     "Canine Extraordinaire")]
_NW = max(len(n) for n, _ in FAMILY) + 2

FOOTER = [
    ("family.tree", [[(n.ljust(_NW), BLUE), (r, FG)] for n, r in FAMILY], "seg"),
    ("contact.ping", [[("✉  ", DIM), ("michael.d.bordelon@gmail.com", FG)],
                      [("✕  ", DIM), ("x.com/cantyoudobester", FG)],
                      [("in ", DIM), ("linkedin.com/in/mikebordelon", FG)]], "seg"),
]

# ---------------------------------------------------------------- geometry
PAD        = 26
A_FS, A_LH = 12.0, 12.8       # portrait
R_FS, R_LH = 14.0, 20.5       # info rows
F_FS, F_LH = 13.0, 18.5       # footer
A_ADV, R_ADV, F_ADV = A_FS*0.6, R_FS*0.6, F_FS*0.6
R_GAP, LABEL_COLS, GUTTER, TITLE_H = 12.0, 21, 30, 68
S_FS, S_LH = 13.0, 18.5       # status block under the portrait
S_HDR, S_GAP = 20, 24         # header offset / gap between left blocks
LEFT_EXTRA = (30 + sum(S_HDR + len(b[2])*S_LH + S_GAP for b in LEFT_BLOCKS)
              - S_GAP)

art = [l for l in open(os.path.join(HERE, "art.txt")).read().split("\n") if l.strip()]
ART_COLS = max(len(l) for l in art)
art = [l.ljust(ART_COLS) for l in art]

def seg_len(segs): return sum(len(t) for t, _ in segs)

LEFT_W  = ART_COLS * A_ADV
RIGHT_W = LABEL_COLS*R_ADV + VALUE_COLS*R_ADV
right_x = PAD + LEFT_W + GUTTER
W = int(right_x + RIGHT_W + PAD)

rows_h = sum(R_GAP if lab is None else len(ls)*R_LH for lab, _, ls in ROWS)
BODY_H = max(len(art)*A_LH + LEFT_EXTRA, 34 + rows_h)
FOOT_ROW  = 24 + max(len(v) for _, v, _ in FOOTER)*F_LH + 14
FOOT_ROWS = -(-len(FOOTER) // 2)          # 2 panels per row, rounded up
FOOT_H    = FOOT_ROWS*FOOT_ROW + 12
H = int(TITLE_H + BODY_H + 30 + FOOT_H + PAD)

# ---------------------------------------------------------------- emit
o, add = [], lambda s: o.append(s)
esc = lambda s: html.escape(s, quote=False)

def text(x, y, segs, fs, weight="400", extra=""):
    parts = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in segs)
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{fs}" '
        f'font-weight="{weight}" xml:space="preserve"{extra}>{parts}</text>')

ALT = ("Terminal-style profile card for Michael Bordelon (cantyoudobetter): CTO at "
       "Ways2Well and ReviveRX, building AI-native healthcare, clinical intimacy at "
       "scale, human optimization and longevity, and agentic systems. Still curious, "
       "still building.")

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(ALT)}">')
add(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>')
add(f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="11" fill="{CARD}" stroke="{BORDER}"/>')

# header: just the handle over the info column
text(right_x, 48, [(HANDLE, GREEN)], 16, "600")
add(f'<line x1="{right_x}" y1="60" x2="{W-PAD}" y2="60" stroke="{BORDER}" stroke-dasharray="4 5"/>')

# portrait, vertically centred in the left pane
ay = TITLE_H + 30 + max(0, (BODY_H - (len(art)*A_LH + LEFT_EXTRA)) / 2)
for i, line in enumerate(art):
    text(PAD, ay + i*A_LH, [(line, ART)], A_FS,
         extra=f' textLength="{LEFT_W:.1f}" lengthAdjust="spacing"')
py = ay + len(art)*A_LH + 30
for hdr, hc, lines, bullet in LEFT_BLOCKS:
    text(PAD, py, [(hdr, hc)], 13.5, "600")
    for i, line in enumerate(lines):
        segs = [(">  ", DIM), (line, FG)] if bullet else [(line, FG)]
        text(PAD, py + S_HDR + i*S_LH, segs, S_FS)
    py += S_HDR + len(lines)*S_LH + S_GAP

# info rows
y = TITLE_H + 34
for lab, lc, ls in ROWS:
    if lab is None:
        yy = y - R_LH + 9
        add(f'<line x1="{right_x}" y1="{yy:.1f}" x2="{W-PAD}" y2="{yy:.1f}" stroke="{BORDER}"/>')
        y += R_GAP
        continue
    text(right_x, y, [(lab, lc)], R_FS, "600")
    for line in ls:
        text(right_x + LABEL_COLS*R_ADV, y, line, R_FS)
        y += R_LH

# footer 2x2
fy = TITLE_H + BODY_H + 20
add(f'<rect x="{PAD-12}" y="{fy}" width="{W-2*(PAD-12)}" height="{FOOT_H}" rx="8" '
    f'fill="none" stroke="{BORDER}"/>')
half = (W - 2*(PAD-12)) / 2
for idx, (title, items, kind) in enumerate(FOOTER):
    cx = PAD + (idx % 2) * half
    cy = fy + 14 + (idx // 2) * FOOT_ROW
    text(cx, cy + 14, [(title, GREEN)], 12.5, "600")
    for j, segs in enumerate(items):
        yy = cy + 14 + 20 + j*F_LH
        if kind == "kv":
            text(cx, yy, [segs[0]], F_FS)
            text(cx + 22*F_ADV, yy, [segs[1]], F_FS)
        else:
            text(cx, yy, segs, F_FS)
add('</svg>')

open(os.path.join(ROOT, "assets", "card.svg"), "w").write("\n".join(o) + "\n")

# guard the legibility budget
over = [ (lab, seg_len(l)) for lab, _, ls in ROWS if ls for l in ls if seg_len(l) > VALUE_COLS ]
scale = LEGIBLE_W / W
print(f"wrote assets/card.svg  {W}x{H}")
print(f"at GitHub width {LEGIBLE_W}: scale {scale:.2f}, "
      f"info text {R_FS*scale:.1f}px, footer {F_FS*scale:.1f}px, art {A_FS*scale:.1f}px")
if over: print("OVER BUDGET:", over)
assert not over, "value lines exceed VALUE_COLS"

# Regenerating the portrait from the source photo:
#   sips -c 1240 1000 tools/photo-source.jpg --out /tmp/c.jpg
#   sips -c 1240 700  /tmp/c.jpg            --out /tmp/h.jpg
#   python3 tools/asciify.py /tmp/h.jpg --cols 44 --gamma 0.85 --floor 0.20 \
#       --ceil 0.71 --bg-thresh 240 --bg-soft 120 --bg-sat 0.10 \
#       --ramp '  .:-=+*#%@' --despeckle 3 --pad --out tools/art.txt
