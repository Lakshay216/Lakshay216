#!/usr/bin/env python3
import datetime as dt
import json
import re
import sys

import requests
from bs4 import BeautifulSoup

from common import ROOT, load_profile


def fetch_days(username):
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(
        url,
        headers={"User-Agent": "github-profile-readme/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    days = []
    for cell in soup.select(".ContributionCalendar-day[data-date]"):
        date = cell.get("data-date")
        count = cell.get("data-count")
        if count is None:
            tip = soup.find("tool-tip", attrs={"for": cell.get("id")})
            text = tip.get_text(" ", strip=True) if tip else ""
            match = re.search(r"([\d,]+) contribution", text, re.I)
            count = match.group(1).replace(",", "") if match else "0"
        days.append({"date": date, "count": int(count)})
    unique = {day["date"]: day for day in days}
    days = [unique[key] for key in sorted(unique)]
    if not days:
        raise RuntimeError("GitHub returned no contribution calendar cells")
    return days


def streaks(days):
    longest = current = run = 0
    for day in days:
        run = run + 1 if day["count"] else 0
        longest = max(longest, run)
    i = len(days) - 1
    if i >= 0 and days[i]["count"] == 0:
        i -= 1
    while i >= 0 and days[i]["count"]:
        current += 1
        i -= 1
    return current, longest


def build_data(username, days):
    current, longest = streaks(days)
    total = sum(day["count"] for day in days)
    best = max(days, key=lambda item: item["count"])
    return {
        "username": username,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": sum(day["count"] > 0 for day in days),
        "current_streak": {"length": current},
        "longest_streak": {"length": longest},
        "best_day": best,
        "days": days,
    }


if __name__ == "__main__":
    username = load_profile()["username"]
    if username == "YOUR_GITHUB_USERNAME":
        sys.exit("Set username in profile.json before fetching contributions.")
    data = build_data(username, fetch_days(username))
    output = ROOT / "data" / "contributions.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}: {data['total_contributions']} contributions")
