#!/usr/bin/env python3
"""Refresh broadcast/data/calendar-2026-27.json: every Indiana FTC and FRC event for the season.

FTC events come from FTCScout (no key needed). FRC events come from The Blue Alliance API v3
when a TBA key is set (TBA_AUTH_KEY or tba.env); without it, the hand-checked FRC entries in calendar-manual.json are kept.
See docs/tba-api.md.

    python scripts/fetch_calendar.py                     # FTC refresh, FRC from the manual file
    TBA_AUTH_KEY=... python scripts/fetch_calendar.py    # FTC and FRC refresh
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import date
from pathlib import Path

from tba_key import tba_key

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "broadcast/data"
FTC_SEASON, FRC_YEAR, FRC_OFFSEASON_YEAR = 2026, 2027, 2026
TBA = "https://www.thebluealliance.com/api/v3"
FTC_TYPES = {"Kickoff": "Kickoff", "Qualifier": "Qualifier", "LeagueMeet": "League meet", "LeagueTournament": "League tournament",
             "Championship": "Championship", "Scrimmage": "Scrimmage", "Premier": "Premier", "OffSeason": "Offseason"}
FTC_ABOUT = {"Kickoff": "Season launch: the new FTC game is revealed and teams start building.",
             "Qualifier": "Qualifying tournament. Top teams and award winners earn spots at the Indiana FTC State Championship."}
TBA_TYPES = {1: "District", 2: "Championship", 99: "Offseason", 100: "Preseason"}


def get(url, headers=None):
    request = urllib.request.Request(url, headers={"User-Agent": "refintery-rankings", **(headers or {})})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def ftc_events():
    rows = get(f"https://api.ftcscout.org/rest/v1/events/search/{FTC_SEASON}?region=USIN&limit=500")
    return [{"id": f"ftc-{e['code'].lower()}", "program": "FTC", "type": FTC_TYPES.get(e["type"], e["type"]),
             "name": f"FTC {FTC_TYPES.get(e['type'], e['type'])} · {e['name'].removesuffix(' QT')}",
             "startDate": e["start"][:10], "endDate": e["end"][:10], "venue": e.get("venue") or "", "city": e.get("city") or "",
             "state": e.get("state") or "", "description": FTC_ABOUT.get(e["type"], ""), "url": f"https://ftcscout.org/events/{FTC_SEASON}/{e['code']}",
             "source": "FTCScout"} for e in rows if not e.get("remote")]


def frc_events(key):
    headers = {"X-TBA-Auth-Key": key}
    rows = []
    for year in (FRC_OFFSEASON_YEAR, FRC_YEAR):
        for e in get(f"{TBA}/events/{year}/simple", headers):
            indiana = e.get("state_prov") == "IN" and e["event_type"] in TBA_TYPES
            if not indiana or (year == FRC_OFFSEASON_YEAR and e["event_type"] != 99):
                continue
            rows.append({"id": f"frc-{e['key']}", "program": "FRC", "type": TBA_TYPES[e["event_type"]], "name": e["name"],
                         "startDate": e["start_date"], "endDate": e["end_date"], "venue": "", "city": e.get("city") or "",
                         "state": "IN", "description": "", "url": f"https://www.thebluealliance.com/event/{e['key']}", "source": "The Blue Alliance"})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", default=str(DATA / "calendar-2026-27.json"))
    args = parser.parse_args()
    manual = {e["id"]: e for e in json.loads((DATA / "calendar-manual.json").read_text(encoding="utf-8"))["events"]}
    fetched = ftc_events()
    key = tba_key()
    if key:
        fetched += frc_events(key)
    events = dict(manual)
    for e in fetched:
        # Hand-written descriptions and venues survive an API refresh.
        hand = manual.get(e["id"], {})
        events[e["id"]] = {**e, **{k: hand[k] for k in ("description", "venue", "week") if hand.get(k)}}
    rows = sorted(events.values(), key=lambda e: (e["startDate"], e["program"], e["name"]))
    output = Path(args.output)
    previous = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else {}
    # Keep the old date when nothing changed, so a quiet week makes no diff (and no pull request).
    checked = previous["retrievedDate"] if previous.get("events") == rows else date.today().isoformat()
    doc = {"season": "2026–27", "retrievedDate": checked,
           "sources": ["FTCScout events API", "The Blue Alliance API v3" if key else "The Blue Alliance (hand-checked; no API key set)", "FIRST and FIRST Indiana calendars"],
           "events": rows}
    Path(args.output).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} events ({sum(e['program'] == 'FTC' for e in rows)} FTC) to {args.output}" + ("" if key else "; FRC from calendar-manual.json (no TBA key)"))


if __name__ == "__main__":
    main()
