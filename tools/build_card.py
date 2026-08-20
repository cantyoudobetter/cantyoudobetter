#!/usr/bin/env python3
"""Build assets/card.svg -- the terminal-style profile card.

GitHub markdown strips CSS, so the styled layout lives inside an SVG that is
committed to the repo and referenced with <img>. Regenerate with:
    python3 tools/build_card.py
"""
import os, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---------------------------------------------------------------- palette
BG, CARD, BORDER = "#06070a", "#0a0d12", "#1b2230"
DIM, FG, WHITE, ART = "#6e7681", "#adbac7", "#e6edf3", "#9aa7b4"
GREEN, BLUE, CYAN = "#7ee787", "#79c0ff", "#56d4dd"
MAG, PINK, ORANGE, YELLOW, RED = "#d2a8ff", "#ff7bd7", "#ffa657", "#e3b341", "#ff7b72"

MONO = "'SF Mono','SFMono-Regular',ui-monospace,'DejaVu Sans Mono',Menlo,Consolas,'Liberation Mono',monospace"

# ---------------------------------------------------------------- content
HANDLE = "cantyoudobetter"

def b(txt, c=FG):           return [(">  ", DIM), (txt, c)]
def plain(txt, c=FG):       return [(txt, c)]

ROWS = [
    ("OS:",        GREEN,  [plain("Human 1.0 "), plain("— aggressively upgrading", DIM)]),
    ("Role:",      GREEN,  [plain("CTO @ Ways2Well + ReviveRX")]),
    ("Mission:",   GREEN,  [plain("Make humans healthier. Keep technology human.")]),
    ("Home Base:", GREEN,  [plain("Texas / wherever the airplane lands")]),
    ("Education:", GREEN,  [plain("Texas A&M "), plain("— Mechanical Engineering", DIM)]),
    (None, None, None),
    ("Languages.Code:",  BLUE, [plain("Python, C#, Java, JavaScript/TypeScript,"),
                                [("SQL, Ruby, Lua ", FG), ("+ whatever the problem requires", DIM)]]),
    ("Languages.Human:", BLUE, [plain("English, Bad Spanish, Engineer")]),
    (None, None, None),
    ("Currently:",  GREEN, [b("AI-native healthcare"), b("Clinical intimacy at scale"),
                            b("Human optimization + longevity"), b("Agentic systems"),
                            b("Still writing actual code", WHITE)]),
    (None, None, None),
    ("Previously:", BLUE,  [b("Healthcare systems"), b("Pharmacy robotics + remote dispensing"),
                            b("EHRs before SaaS was cool"), b("Enterprise architecture"),
                            b("Mobile + cloud"), b("Neural nets before transformers")]),
    (None, None, None),
    ("Side.Quests:", GREEN, [
        [("Airplanes ", FG), ("✈", CYAN), ("  |  ", DIM), ("Weird hardware", FG), ("  |  ", DIM),
         ("Running", FG), ("  |  ", DIM), ("Skiing", FG)],
        [("Cooking", FG), ("  |  ", DIM), ("Writing", FG), ("  |  ", DIM), ("Thinking about AGI", FG),
         ("  |  ", DIM), ("Fighting entropy", FG)]]),
    (None, None, None),
    ("Books:", ORANGE, [[("The Black Swan", FG), ("  |  ", DIM), ("Garden of Lies", FG)]]),
    (None, None, None),
    ("Operating.System:", YELLOW, [
        [("Ambitious + honest", FG), ("  |  ", DIM), ("Agency without abandonment", FG)],
        plain("Fight destructive entropy."),
        plain("Preserve generative disorder.")]),
    (None, None, None),
    ("Current.Hypothesis:", PINK, [
        plain("Technology's highest purpose may be to create"),
        plain("the conditions in which humans can afford to"),
        plain("be more human.")]),
    (None, None, None),
    ("Status:", GREEN, [b("Still curious."), b("Still building."), b("Still sharpening the stone.")]),
]

FOOTER = [
    ("github.stats", GREEN, [
        [("since",      DIM), ("2015", BLUE)],
        [("repos",      DIM), ("39",   BLUE)],
        [("languages",  DIM), ("8+",   BLUE)],
        [("stars",      DIM), ("go ahead", BLUE)],
        [("ego",        DIM), ("negotiable", BLUE)]]),
    ("currently.building", GREEN, [
        [("◈ ", CYAN),   ("AI-native healthcare platform", FG)],
        [("★ ", YELLOW), ("Clinical workflows that put humans first", FG)],
        [("◈ ", CYAN),   ("Agentic systems that reduce friction", FG)],
        [("◈ ", CYAN),   ("Developer experience that doesn't suck", FG)]]),
    ("toolkit.exe", GREEN, [
        [("▸ ", BLUE), ("VS Code",  FG), ("PostgreSQL", FG)],
        [("▸ ", BLUE), ("JetBrains",FG), ("Redis",      FG)],
        [("▸ ", BLUE), ("Docker",   FG), ("AWS",        FG)],
        [("▸ ", BLUE), ("Linux",    FG), ("Git",        FG)]]),
    ("contact.ping", GREEN, [
        [("✉ ", DIM), ("mike@ways2well.com", FG)],
        [("◉ ", DIM), ("mikebordelon.com", FG)],
        [("✕ ", DIM), ("x.com/mikebordelon", FG)],
        [("in ", DIM),     ("linkedin.com/in/mikebordelon", FG)]]),
]

# ---------------------------------------------------------------- geometry
PAD        = 40
A_FS, A_LH = 11.5, 12.25          # portrait font-size / line-height
A_ADV      = A_FS * 0.6
R_FS, R_LH = 15.0, 23.0           # info rows
R_ADV      = R_FS * 0.6
R_GAP      = 13.0                 # extra space at a group divider
F_FS, F_LH = 12.5, 19.0           # footer
F_ADV      = F_FS * 0.6
LABEL_COLS = 20

art = [l.rstrip("\n") for l in open(os.path.join(HERE, "art.txt")).read().split("\n") if l.strip()]
ART_COLS = max(len(l) for l in art)
art = [l.ljust(ART_COLS) for l in art]

def seg_w(segs, adv): return sum(len(t) for t, _ in segs) * adv

LEFT_W  = ART_COLS * A_ADV
RIGHT_W = max(seg_w(l, R_ADV) for _, _, ls in ROWS if ls for l in ls) + LABEL_COLS * R_ADV + 10
GUTTER  = 46

TITLE_H = 92
left_x  = PAD
right_x = PAD + LEFT_W + GUTTER

body_h_left  = len(art) * A_LH + 64          # + shell prompt lines
rows_h = 0
for lab, _, ls in ROWS:
    rows_h += R_GAP if lab is None else len(ls) * R_LH
body_h_right = 34 + rows_h

BODY_H   = max(body_h_left, body_h_right)
FOOT_H   = 24 + 4 + max(len(v) for _, _, v in FOOTER) * F_LH + 22
W = int(right_x + RIGHT_W + PAD)
H = int(TITLE_H + BODY_H + 34 + FOOT_H + PAD)

# ---------------------------------------------------------------- emit
o = []
def add(s): o.append(s)
def esc(s):  return html.escape(s, quote=False)

def text(x, y, segs, fs, weight="400", extra=""):
    parts = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in segs)
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{fs}" '
        f'font-weight="{weight}" xml:space="preserve"{extra}>{parts}</text>')

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="{HANDLE} profile card">')
add(f'<rect width="{W}" height="{H}" rx="16" fill="{BG}"/>')
add(f'<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="13" fill="{CARD}" stroke="{BORDER}"/>')

# titlebar
for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
    add(f'<circle cx="{PAD + i*22}" cy="42" r="7" fill="{c}"/>')
text(PAD, 84, [(HANDLE, WHITE), (" / ", DIM), ("README.md", FG)], 16, "600")

# right header + dashed rule
text(right_x, 47, [(HANDLE, GREEN)], 17, "600")
add(f'<line x1="{right_x}" y1="60" x2="{W-PAD}" y2="60" stroke="{BORDER}" '
    f'stroke-dasharray="4 5"/>')

# portrait
ay = TITLE_H + 26
for i, line in enumerate(art):
    text(left_x, ay + i*A_LH, [(line, ART)], A_FS,
         extra=f' textLength="{LEFT_W:.1f}" lengthAdjust="spacing"')

# shell prompt under portrait
py = ay + len(art)*A_LH + 30
text(left_x, py, [("mike@human", GREEN), (":~$ ", DIM),
                  ("still_curious.still_building.sh", FG)], 13.5)
text(left_x, py + 24, [(">  ", DIM), ("status: ", CYAN),
                       ("always learning, always shipping", FG)], 13.5)

# info rows
y = TITLE_H + 34
for lab, lc, ls in ROWS:
    if lab is None:
        add(f'<line x1="{right_x}" y1="{y - R_LH + 8:.1f}" x2="{W-PAD}" y2="{y - R_LH + 8:.1f}" '
            f'stroke="{BORDER}"/>')
        y += R_GAP
        continue
    text(right_x, y, [(lab, lc)], R_FS, "600")
    vx = right_x + LABEL_COLS * R_ADV
    for line in ls:
        text(vx, y, line, R_FS)
        y += R_LH

# footer panel
fy = TITLE_H + BODY_H + 22
add(f'<rect x="{PAD-14}" y="{fy}" width="{W-2*(PAD-14)}" height="{FOOT_H}" rx="8" '
    f'fill="none" stroke="{BORDER}"/>')
col_x = [PAD, PAD + 300, PAD + 300 + 420, PAD + 300 + 420 + 260]
for (title, tc, items), cx in zip(FOOTER, col_x):
    text(cx, fy + 26, [(title, tc)], 13, "600")
    for j, segs in enumerate(items):
        yy = fy + 26 + 22 + j*F_LH
        if title == "github.stats":
            text(cx, yy, [(segs[0][0], segs[0][1])], F_FS)
            text(cx + 150, yy, [(segs[1][0], segs[1][1])], F_FS)
        elif title == "toolkit.exe":
            text(cx, yy, [segs[0], segs[1]], F_FS)
            text(cx + 160, yy, [(segs[0][0], segs[0][1]), segs[2]], F_FS)
        else:
            text(cx, yy, segs, F_FS)
add('</svg>')

out = os.path.join(ROOT, "assets", "card.svg")
open(out, "w").write("\n".join(o) + "\n")
print(f"wrote {out}  ({W}x{H})")
