#!/usr/bin/env python3
"""Photo -> character art. Uses macOS `sips` for decode/resize, pure-python BMP parse."""
import subprocess, sys, os, struct, argparse
from collections import deque

def load_bmp_resized(src, cols, rows, tmp):
    subprocess.run(["sips","-s","format","bmp","-z",str(rows),str(cols),src,"--out",tmp],
                   check=True, capture_output=True)
    d = open(tmp,"rb").read()
    off = struct.unpack_from("<I", d, 10)[0]
    w, h = struct.unpack_from("<ii", d, 18)
    bpp  = struct.unpack_from("<H", d, 28)[0]
    assert bpp in (24,32), f"unexpected bpp {bpp}"
    npx, stride = bpp//8, ((bpp//8)*abs(w)+3)//4*4
    flip = h > 0; h = abs(h)
    px = []
    for y in range(h):
        row_i = (h-1-y) if flip else y
        base = off + row_i*stride
        row = []
        for x in range(w):
            b,g,r = d[base+x*npx], d[base+x*npx+1], d[base+x*npx+2]
            row.append((r,g,b))
        px.append(row)
    return px, w, h

def luma(p): return 0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2]

def sat(p):
    mx, mn = max(p), min(p)
    return 0.0 if mx == 0 else (mx-mn)/mx

def bg_mask(px, w, h, thresh, soft=None, satmax=0.16):
    """Flood-fill from the border over background-looking pixels -> True where bg.
    A pixel is bg-ish if it is very bright, OR moderately bright and desaturated
    (the photo's white backdrop and its soft shadow; skin stays saturated)."""
    soft = thresh if soft is None else soft
    def isbg(p):
        L = luma(p)
        return L >= thresh or (L >= soft and sat(p) <= satmax)
    m = [[False]*w for _ in range(h)]
    q = deque()
    def seed(x,y):
        if not m[y][x] and isbg(px[y][x]): m[y][x]=True; q.append((x,y))
    for x in range(w):
        seed(x,0); seed(x,h-1)
    for y in range(h):
        seed(0,y); seed(w-1,y)
    while q:
        x,y = q.popleft()
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny = x+dx, y+dy
            if 0<=nx<w and 0<=ny<h: seed(nx,ny)
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("--cols", type=int, default=78)
    ap.add_argument("--aspect", type=float, default=0.60, help="char cell w/h")
    ap.add_argument("--ramp", default=" .:-=+*#%@")
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--floor", type=float, default=0.0, help="black point 0-1")
    ap.add_argument("--ceil",  type=float, default=1.0, help="white point 0-1")
    ap.add_argument("--bg-thresh", type=float, default=225.0)
    ap.add_argument("--bg-soft", type=float, default=None, help="looser luma for desaturated bg")
    ap.add_argument("--bg-sat", type=float, default=0.16, help="max saturation to count as bg")
    ap.add_argument("--no-bg-strip", action="store_true")
    ap.add_argument("--dither", action="store_true")
    ap.add_argument("--despeckle", type=int, default=0, help="drop chars with < N filled neighbours")
    ap.add_argument("--pad", action="store_true", help="pad every line to full width")
    ap.add_argument("--out", default="-")
    a = ap.parse_args()

    sw, sh = [int(v.split(": ")[1]) for v in subprocess.run(
        ["sips","-g","pixelWidth","-g","pixelHeight",a.src],
        capture_output=True, text=True).stdout.strip().split("\n")[1:3]]
    rows = max(1, round(a.cols * (sh/sw) * a.aspect))
    tmp = "/tmp/_asciify.bmp"
    px, w, h = load_bmp_resized(a.src, a.cols, rows, tmp)

    mask = None if a.no_bg_strip else bg_mask(px, w, h, a.bg_thresh, a.bg_soft, a.bg_sat)

    # normalized brightness field, background forced to 0
    f = [[0.0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if mask and mask[y][x]: f[y][x] = 0.0; continue
            v = luma(px[y][x])/255.0
            v = (v - a.floor) / max(1e-6, a.ceil - a.floor)
            v = min(1.0, max(0.0, v)) ** a.gamma
            f[y][x] = v

    ramp = a.ramp; n = len(ramp)-1
    out = []
    for y in range(h):
        line = []
        for x in range(w):
            v = f[y][x]
            q = round(v*n)
            if a.dither:  # Floyd-Steinberg on the quantization error
                err = v - q/n
                for dx,dy,wt in ((1,0,7/16),(-1,1,3/16),(0,1,5/16),(1,1,1/16)):
                    nx,ny = x+dx, y+dy
                    if 0<=nx<w and 0<=ny<h: f[ny][nx] = min(1.0,max(0.0,f[ny][nx]+err*wt))
            line.append(ramp[q])
        out.append("".join(line))
    if a.despeckle:
        grid=[list(r) for r in out]
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x]==" ": continue
                n=sum(1 for dx in(-1,0,1) for dy in(-1,0,1) if (dx or dy)
                      and 0<=y+dy<len(grid) and 0<=x+dx<len(grid[y+dy]) and grid[y+dy][x+dx]!=" ")
                if n < a.despeckle: grid[y][x]=" "
        out=["".join(r) for r in grid]
    if not a.pad: out=[r.rstrip() for r in out]
    # trim fully-blank leading/trailing rows
    while out and not out[0].strip():  out.pop(0)
    while out and not out[-1].strip(): out.pop()
    if a.pad:
        wmax=max(len(r) for r in out); out=[r.ljust(wmax) for r in out]
    txt = "\n".join(out)
    if a.out == "-": print(txt)
    else: open(a.out,"w").write(txt+"\n"); print(f"wrote {a.out} ({w}x{h})", file=sys.stderr)

main()
