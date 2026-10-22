#!/usr/bin/env python3
"""Verify the broadcast ordering, source joins, leadership roles, and static files."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import re
import struct

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    data = load(HERE / "dist/data.json")
    frc = load(ROOT / "data/teams.json")
    ftc = load(ROOT / "ftc/data/teams.json")
    regional = sorted([r for r in frc["teams"] if r["scope_group"] == "northeast_indiana"],
                      key=lambda r: (-r["rankings"]["epa_mean"], r["team_number"]))
    require(len(regional) == 13 and len(data["top10"]) == 10, "Unexpected Top 10 population")
    require([r["number"] for r in data["top10"]] == [r["team_number"] for r in regional[:10]], "Top 10 does not match source EPA ordering")
    scope = load(HERE / "data/first-fin-scope-audit.json")
    require(len(scope["teams"]) == 69 and scope["capture_failure_count"] == 0, "Official roster screening is incomplete")
    require(set(scope["included_team_numbers"]) == {r["team_number"] for r in regional}, "Official district and research regional selections differ")
    require(data["edition"]["rankingsDate"] == "2026-06-12" and data["edition"]["season"] == 2026, "Historical snapshot date lost")
    people_count = 0
    for t, r in zip(data["top10"], regional[:10]):
        k, h, l = r["rankings"], r["season_history"], r["leadership"]
        require(t["epa"] == k["epa_mean"] and t["stateRank"] == k["state_rank"] and t["worldRank"] == k["world_rank"], "Source performance value changed")
        require(t["stateCount"] == k["state_team_count"] and t["worldCount"] == k["world_team_count"], "Source ranking denominator changed")
        require(t["seasons"] == h["recorded_season_count"] and t["rookieYear"] == h["official_rookie_year"], "Source history changed")
        require(t["gaps"] == l["gaps"] and t["affiliationNote"] == r["affiliation_notes"], "Qualification lost")
        for to_key, from_key in (("students", "students"), ("adults", "adults"), ("representatives", "other_representatives")):
            require(len(t[to_key]) == len(l[from_key]), "People dropped from evidence")
            for p, original in zip(t[to_key], l[from_key]):
                require((p["name"], p["role"], p["date"], p["note"], p["sourceUrls"]) ==
                        (original["name"], original["role"], original["evidence_date"], original["notes"], original["source_urls"]), "Published role or date changed")
                people_count += 1
    source_ftc = {r["team_number"]: r for r in ftc["teams"]}
    require({r["number"] for r in data["ftc"]["teams"]} == {22331, 25638}, "FTC features escaped regional scope")
    for t in data["ftc"]["teams"]:
        r = source_ftc[t["number"]]
        require(t["opr"] == r["rankings"]["value"] and t["regionalOpr"] == r["rankings"]["regional_value"], "FTC world/regional values conflated")
    require([r["number"] for r in data["ftc"]["newTeams"]] == [36124], "New-season watch changed")
    require(data["hero"]["attributionUrl"] == "https://first.global/sport/", "Hero attribution lost")
    require("not assigned by school enrollment" in data["formatExplainer"]["analogy"], "Enrollment distinction lost")
    for name in ("index.html", "styles.css", "app.js", "press-kit.md", "assets/refinery-logo.svg", "assets/refinery-shop.jpeg"):
        require((HERE / "dist" / name).is_file(), f"Missing static asset: {name}")
    for asset in load(HERE / "data/asset-manifest.json")["assets"]:
        require(hashlib.sha256((HERE / asset["file"]).read_bytes()).hexdigest() == asset["sha256"], "Official asset checksum changed")
    for name in ("nei-top10-2026.png", "team-spotlight-9119.png", "ftc-features.png"):
        raw = (HERE / "dist/exports" / name).read_bytes()
        require(raw[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", raw[16:24]) == (1920, 1080), f"Broadcast graphic has incorrect dimensions: {name}")
    for file in (HERE / "dist").rglob("*"):
        if file.suffix not in {".html", ".css", ".js", ".md", ".json", ".svg"}:
            continue
        value = file.read_text(encoding="utf-8")
        require("/tmp/" not in value and "/Users/" not in value, f"Machine path leaked: {file.name}")
        require(not re.search(r"github_pat_[A-Za-z0-9_]{30,}|gh[pousr]_[A-Za-z0-9]{30,}", value), "Credential-like value in static output")
    print(f"Verified broadcast: Top 10 of {len(regional)} regional FRC teams; {people_count} sourced person-role rows; two separate FTC features and one rookie watch.")


if __name__ == "__main__":
    main()
