#!/usr/bin/env python3
"""Capture factual FIRST FTC season lists, with source hashes and no full-page copies.

Python 3.10+, standard library only. Existing captures are never overwritten.
FTC's API year is the season's starting year: 2025 means 2025–26.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import urllib.request


def text(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def capture(team, page_season, cutoff):
    url = f"https://ftc-events.firstinspires.org/{page_season}/team/{team}"
    request = urllib.request.Request(url, headers={"User-Agent": "Fort-Wayne-FTC-research/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        raw = response.read()
        resolved = response.url
        headers = {k.lower(): v for k, v in response.headers.items()}
    document = raw.decode("utf-8")
    rookie = re.search(r"Rookie Year:\s*</em></b>\s*(\d{4})", document)
    seasons = re.findall(
        r'href="/(\d{4})/team/' + str(team) + r'">\s*(\d{4}):\s*([^<]+)', document
    )
    heading = re.search(r"<h1[^>]*>(.*?)</h1>", document, re.S)
    heading_text = text(heading.group(1)) if heading else ""
    if not rookie or any(a != b for a, b, _ in seasons) or not re.search(
        rf"Team {team}\b.*\({page_season}\)", heading_text
    ):
        raise ValueError(f"Unexpected FIRST season-list structure for {team}")
    labels = {int(year): html.unescape(game).strip() for year, _, game in seasons}
    # FIRST omits the Other Seasons menu when only the current page exists.
    labels.setdefault(page_season, None)
    all_seasons = sorted(labels)
    eligible = [year for year in all_seasons if year <= cutoff]
    sponsors = re.search(r"Sponsors:\s*</em></b>(.*?)<br", document, re.S)
    return {
        "team_number": team,
        "source_url": url,
        "resolved_url": resolved,
        "page_season": page_season,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "response_bytes": len(raw),
        "response_last_modified": headers.get("last-modified"),
        "page_heading": heading_text,
        "page_season_sponsors_and_affiliations": text(sponsors.group(1)) if sponsors else None,
        "official_rookie_year": int(rookie.group(1)),
        "all_listed_seasons": all_seasons,
        "season_game_labels": {str(year): labels[year] for year in all_seasons},
        "recorded_seasons_through_cutoff": eligible,
        "recorded_season_count": len(eligible),
        "excluded_later_seasons": [year for year in all_seasons if year > cutoff],
        "count_definition": "Season entries linked in FIRST FTC Events Other Seasons menu, plus the verified current page, through the starting-year cutoff; not a count of years with played matches, and not rookie-year subtraction.",
        "history_coverage_note": "FIRST FTC Event Web season lists in these captures begin no earlier than 2019. A rookie year before the first listed season does not establish which missing seasons had activity.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teams", nargs="+", required=True, type=int)
    parser.add_argument("--through", type=int, default=2025)
    parser.add_argument("--page-season", type=int, default=2025)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; choose a new capture filename.")
    if len(args.teams) != len(set(args.teams)):
        parser.error("Duplicate team numbers.")
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda n: capture(n, args.page_season, args.through), sorted(args.teams)))
    result = {
        "schema_version": "1.0",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "season_start_year_cutoff": args.through,
        "source": "FIRST Tech Challenge Events team season pages",
        "teams": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(f"Captured {len(rows)} FIRST FTC season histories: {args.output}")


if __name__ == "__main__":
    main()
