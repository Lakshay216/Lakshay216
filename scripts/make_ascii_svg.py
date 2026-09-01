#!/usr/bin/env python3
import html
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from common import ROOT, esc, load_profile

COLS, ROWS, CELL_W, CELL_H = 100, 53, 8, 15
RAMP = " .`:-=+*cs#%@"


def placeholder_rows(name):
    initials = "".join(part[0] for part in name.split()[:2]).upper() or "ME"
    rows = []
    for y in range(ROWS):
        line = [" "] * COLS
        if 6 <= y <= 46:
            edge = int(18 - abs(26 - y) * .30)
            for x in range(50 - edge, 50 + edge):
                if 0 <= x < COLS:
                    line[x] = "#" if y in (6, 46) or x in (50-edge, 50+edge-1) else "."
        rows.append("".join(line))
    label = f"[ add your photo: {initials} ]"
    start = (COLS - len(label)) // 2
    rows[27] = rows[27][:start] + label + rows[27][start+len(label):]
    return rows


def photo_rows(path):
    image = Image.open(path).convert("L")
    if "prepped" not in os.path.basename(path).lower():
        # Public avatars often have a dark or illustrated background. Turning
        # their edges into dark ink on white keeps the ASCII panel legible.
        image = ImageOps.invert(image.filter(ImageFilter.FIND_EDGES))
        image = ImageOps.autocontrast(image, cutoff=2)
        image = ImageEnhance.Brightness(image).enhance(1.22)
    image = ImageEnhance.Contrast(image).enhance(1.05).resize((COLS, ROWS), Image.Resampling.LANCZOS)
    rows = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            lum = pow(image.getpixel((x, y)) / 255, 1.18)
            chars.append(" " if lum >= .80 else RAMP[max(0, min(len(RAMP)-1, round((1-lum)*(len(RAMP)-1))))])
        rows.append("".join(chars))
    return rows


if __name__ == "__main__":
    profile = load_profile()
    if len(sys.argv) > 1:
        source = sys.argv[1]
    elif (ROOT / "source-prepped.png").exists():
        source = str(ROOT / "source-prepped.png")
    else:
        source = str(ROOT / "source-photo.jpg")
    rows = photo_rows(source) if os.path.exists(source) else placeholder_rows(profile["name"])
    static = bool(os.environ.get("STATIC"))
    width, height, pad, title_h = 840, 875, 20, 30
    art_top = title_h + 6
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"><defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
           f'<rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="839" height="874" rx="12" fill="none" stroke="#30363d"/><line x1="0" y1="30" x2="840" y2="30" stroke="#30363d"/>']
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        out.append(f'<circle cx="{pad+i*16}" cy="15" r="5" fill="{color}"/>')
    out.append(f'<text x="420" y="19" fill="#7d8590" font-size="12" text-anchor="middle">{esc(profile["prompt_name"])}@github: ~$ ./portrait.sh</text>')
    for i, line in enumerate(rows):
        y = art_top + i * CELL_H + CELL_H * .74
        text = f'<text xml:space="preserve" x="{pad}" y="{y:.1f}" fill="#c9d1d9" font-size="12.9" textLength="800" lengthAdjust="spacing">{html.escape(line)}</text>'
        if static:
            out.append(text)
        else:
            delay = i * .11
            out.append(f'<clipPath id="r{i}"><rect x="20" y="{art_top+i*CELL_H:.1f}" height="15" width="0"><animate attributeName="width" from="0" to="800" begin="{delay:.2f}s" dur=".11s" fill="freeze"/></rect></clipPath><g clip-path="url(#r{i})">{text}</g>')
    status_y = 850
    out.append(f'<line x1="0" y1="820" x2="840" y2="820" stroke="#30363d"/><text x="20" y="{status_y}" fill="#7d8590" font-size="13">{esc(profile["prompt_name"])}@github:~$ whoami <tspan fill="#c9d1d9">{esc(profile["name"])}</tspan><tspan fill="#c9d1d9"> █<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" repeatCount="indefinite"/></tspan></text></svg>')
    (ROOT / "profile-ascii.svg").write_text("".join(out), encoding="utf-8")
    print("Wrote profile-ascii.svg")
