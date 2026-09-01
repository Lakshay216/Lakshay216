#!/usr/bin/env python3
import datetime as dt
import json
import os

from common import ROOT, esc, load_profile

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP, STEP = 12, 3, 15


def blank_data(username):
    end = dt.date.today()
    start = end - dt.timedelta(days=370)
    days = []
    cursor = start
    while cursor <= end:
        days.append({"date": cursor.isoformat(), "count": 0})
        cursor += dt.timedelta(days=1)
    return {
        "username": username,
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": 0,
        "current_streak": {"length": 0},
        "longest_streak": {"length": 0},
        "best_day": days[-1],
        "days": days,
    }


def level(count):
    if count == 0: return 0
    if count <= 3: return 1
    if count <= 8: return 2
    if count <= 16: return 3
    if count <= 30: return 4
    return 5


def build_grid(days):
    first = dt.date.fromisoformat(days[0]["date"])
    column = [None] * ((first.weekday() + 1) % 7)
    grid = []
    for day in days:
        column.append(day)
        if len(column) == 7:
            grid.append(column)
            column = []
    if column:
        grid.append(column + [None] * (7 - len(column)))
    return grid


def render(data, profile):
    grid = build_grid(data["days"])
    pad, left, title_h, labels_h = 22, 30, 30, 20
    width = pad + left + len(grid) * STEP + pad
    grid_top = title_h + labels_h
    grid_left = pad + left
    grid_h = 7 * STEP
    height = grid_top + grid_h + 96
    prompt = esc(profile["prompt_name"])
    username = esc(profile["username"])
    static = bool(os.environ.get("STATIC"))
    css = "" if static else "@keyframes cell{0%{opacity:0;transform:translateY(-6px)}100%{opacity:1;transform:translateY(0)}}.c{opacity:0;animation:cell .42s cubic-bezier(.2,.8,.2,1) both}"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
           f'<style>{css}</style><defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#0d1420"/><stop offset="1" stop-color="#0a0e14"/></linearGradient></defs>',
           f'<rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="#1f6feb" stroke-opacity=".55"/>',
           f'<line x1="0" y1="30" x2="{width}" y2="30" stroke="#1f6feb" stroke-opacity=".35"/>']
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        out.append(f'<circle cx="{pad+i*16}" cy="15" r="5" fill="{color}"/>')
    out.append(f'<text x="{width/2}" y="19" fill="#7d8590" font-size="12" text-anchor="middle">{prompt}@github: ~/contributions --graph</text>')
    month_seen = set()
    for ci, column in enumerate(grid):
        for day in column:
            if day:
                date = dt.date.fromisoformat(day["date"])
                key = (date.year, date.month)
                if date.day <= 7 and key not in month_seen:
                    month_seen.add(key)
                    out.append(f'<text x="{grid_left+ci*STEP}" y="44" fill="#7d8590" font-size="10">{date:%b}</text>')
                break
    for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        out.append(f'<text x="{pad}" y="{grid_top+row*STEP+10}" fill="#7d8590" font-size="9">{label}</text>')
    for ci, column in enumerate(grid):
        for ri, day in enumerate(column):
            if not day: continue
            count = day["count"]
            delay = ci * .018 + ri * .045
            cls = "" if static else ' class="c"'
            style = "" if static else f' style="animation-delay:{delay:.3f}s"'
            out.append(f'<rect{cls} x="{grid_left+ci*STEP}" y="{grid_top+ri*STEP}" width="12" height="12" rx="2.5" fill="{PALETTE[level(count)]}"{style}><title>{day["date"]}: {count} contributions</title></rect>')
    legend_y = grid_top + grid_h + 6
    legend_x = width - pad - 138
    out.append(f'<text x="{legend_x}" y="{legend_y+10}" fill="#7d8590" font-size="10">Less</text>')
    for i, color in enumerate(PALETTE):
        out.append(f'<rect x="{legend_x+30+i*14}" y="{legend_y}" width="11" height="11" rx="2" fill="{color}"/>')
    out.append(f'<text x="{legend_x+118}" y="{legend_y+10}" fill="#7d8590" font-size="10">More</text>')
    line_y = legend_y + 27
    total = data["total_contributions"]
    current = data["current_streak"]["length"]
    longest = data["longest_streak"]["length"]
    out.append(f'<line x1="0" y1="{line_y}" x2="{width}" y2="{line_y}" stroke="#1f6feb" stroke-opacity=".25"/>')
    out.append(f'<text x="{pad}" y="{line_y+24}" fill="#39d353" font-size="13" font-weight="700">{total:,}<tspan fill="#7d8590" font-weight="400"> contributions in the last year</tspan></text>')
    out.append(f'<text x="{width-pad}" y="{line_y+24}" fill="#7d8590" font-size="11" text-anchor="end">github.com/{username}</text>')
    out.append(f'<text x="{pad}" y="{line_y+48}" fill="#7d8590" font-size="12">current streak <tspan fill="#22d3ee" font-weight="700">{current} days</tspan>  ·  longest <tspan fill="#22d3ee" font-weight="700">{longest} days</tspan></text></svg>')
    return "".join(out)


if __name__ == "__main__":
    profile = load_profile()
    path = ROOT / "data" / "contributions.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else blank_data(profile["username"])
    (ROOT / "contrib-heatmap.svg").write_text(render(data, profile), encoding="utf-8")
    print("Wrote contrib-heatmap.svg")
