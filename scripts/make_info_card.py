#!/usr/bin/env python3
import os

from common import ROOT, esc, load_profile

ROWS = [
    ("Role", "role", "#22d3ee"),
    ("Location", "location", "#39d353"),
    ("Now", "now", "#f2cc60"),
    ("Focus", "focus", "#a371f7"),
    ("Stack", "stack", "#58a6ff"),
    ("Highlights", "highlights", "#ff7b72"),
]


if __name__ == "__main__":
    p = load_profile()
    static = bool(os.environ.get("STATIC"))
    width, height = 820, 645
    css = "" if static else "@keyframes row{to{opacity:1;transform:translateX(0)}}.row{opacity:0;transform:translateX(-12px);animation:row .42s ease-out forwards}"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"><style>{css}</style>',
           '<defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
           f'<rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="#30363d"/>',
           '<line x1="0" y1="30" x2="820" y2="30" stroke="#30363d"/>']
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        out.append(f'<circle cx="{20+i*16}" cy="15" r="5" fill="{color}"/>')
    out.append(f'<text x="410" y="20" fill="#7d8590" font-size="14" text-anchor="middle">{esc(p["prompt_name"])}@github: ~$ neofetch</text>')
    out.append(f'<text x="28" y="76" fill="#e6edf3" font-size="28" font-weight="700">{esc(p["name"])}</text><text x="28" y="101" fill="#7d8590" font-size="15">{esc(p["username"])}@github</text><line x1="28" y1="118" x2="792" y2="118" stroke="#30363d"/>')
    for i, (label, key, color) in enumerate(ROWS):
        y = 158 + i * 70
        style = "" if static else f' style="animation-delay:{.16+i*.15:.2f}s"'
        out.append(f'<g class="row"{style}><text x="28" y="{y}" fill="{color}" font-size="17" font-weight="700">{label}</text><text x="150" y="{y}" fill="#c9d1d9" font-size="17">{esc(p[key])}</text></g>')
    out.append(f'<line x1="28" y1="570" x2="792" y2="570" stroke="#30363d"/><text x="28" y="610" fill="#7d8590" font-size="15">{esc(p["prompt_name"])}@github:~$ <tspan fill="#c9d1d9">open to connect</tspan></text><rect x="286" y="596" width="9" height="16" fill="#c9d1d9"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" repeatCount="indefinite"/></rect></svg>')
    (ROOT / "info-card.svg").write_text("".join(out), encoding="utf-8")
    print("Wrote info-card.svg")
