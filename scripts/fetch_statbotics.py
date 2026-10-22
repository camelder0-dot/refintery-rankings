#!/usr/bin/env python3
"""Preserve or verify the fixed 17-team, 2026 Statbotics research snapshot.

Only Python's standard library is required. Network access is opt-in with
--download. Every saved capture gets a new timestamped directory; the script
never overwrites the research baseline, previous captures, or the project roster.
Exit codes: 0 = baseline match; 1 = invalid/unavailable data; 2 = review changes.
"""

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys
import urllib.request
import zlib


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "statbotics"
BASELINE_PATH = ARTIFACTS / "expected-rankings-2026.json"
YEAR = 2026
ENDPOINT = "https://storage.googleapis.com/site_v1/team_years/2026"
ROSTER = (1501, 1720, 9119, 9431, 4982, 10434, 8103, 10332, 8742,
          10172, 8431, 10411, 8432, 5559, 3777, 6556, 11407)
SOURCE_COMMIT = "169330ecef38a4f614356ac0b0caa156f2180021"
SOURCE_BASE = "https://raw.githubusercontent.com/avgupta456/statbotics/" + SOURCE_COMMIT
SOURCE_FILES = {
    # Keep relevant lines only: unrelated frontend constants are not needed.
    "frontend/src/constants.tsx": ("constants.excerpt.tsx", ((3, 10), (14, 15))),
    "frontend/src/api/teams.tsx": ("teams.tsx", None),
    "frontend/src/api/storage.tsx": ("storage.tsx", None),
    "LICENSE": ("LICENSE", None),
}


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def utc_text(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Refintery-Rankings-Public-Research/1.0",
        "Accept-Encoding": "identity",
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        if response.status != 200:
            raise ValueError("Unexpected HTTP status: " + str(response.status))
        body = response.read()
        headers = {key.lower(): value for key, value in response.headers.items()}
        effective_url = response.url
    return body, headers, effective_url


def load_baseline():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    if baseline["year"] != YEAR or tuple(x["team"] for x in baseline["teams"]) != ROSTER:
        raise ValueError("Frozen baseline roster/year changed; explicit code review required")
    return baseline


def decode_snapshot(raw):
    decoder = zlib.decompressobj()
    decoded = decoder.decompress(raw) + decoder.flush()
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError("Expected one complete zlib stream with no trailing bytes")
    payload = json.loads(decoded)
    if not isinstance(payload, dict) or not isinstance(payload.get("team_years"), list):
        raise ValueError("Unexpected snapshot schema: missing team_years list")
    rows = payload["team_years"]
    by_team = {}
    for row in rows:
        if not isinstance(row, dict) or type(row.get("team")) is not int:
            raise ValueError("Every team-year row must have an integer team number")
        if row.get("year") != YEAR:
            raise ValueError("Unexpected year in snapshot")
        if row["team"] in by_team:
            raise ValueError("Duplicate team-year: " + str(row["team"]))
        by_team[row["team"]] = row
    missing = [team for team in ROSTER if team not in by_team]
    if missing:
        raise ValueError("Fixed roster is incomplete; missing teams: " + str(missing))
    subset = {"year": payload["year"], "team_years": [by_team[t] for t in ROSTER]}
    return decoded, subset, len(rows)


def ranking_values(row):
    # This archived snapshot uses a distribution object with mean and sd.
    # Refuse a schema change instead of guessing a replacement EPA field.
    epa = row["epa"]["total_points"]["mean"]
    if isinstance(epa, bool) or not isinstance(epa, (int, float)) or not math.isfinite(epa):
        raise ValueError("Invalid EPA for team " + str(row["team"]))
    state_rank = row["epa"]["ranks"]["state"]
    world_rank = row["epa"]["ranks"]["total"]
    for ranking in (state_rank, world_rank):
        if (type(ranking["rank"]) is not int or type(ranking["team_count"]) is not int
                or not 1 <= ranking["rank"] <= ranking["team_count"]):
            raise ValueError("Invalid rank or denominator for team " + str(row["team"]))
    return {
        "team": row["team"], "epa": epa, "state": row["state"],
        "state_rank": state_rank["rank"], "state_team_count": state_rank["team_count"],
        "world_rank": world_rank["rank"], "world_team_count": world_rank["team_count"],
    }


def compare(raw, subset, row_count, baseline, headers):
    observed = [ranking_values(row) for row in subset["team_years"]]
    differences = []
    for expected, actual in zip(baseline["teams"], observed):
        for field, expected_value in expected.items():
            if actual[field] != expected_value:
                differences.append({"team": expected["team"], "field": field,
                                    "expected": expected_value, "observed": actual[field]})
    result = {
        "year": YEAR, "expected_team_numbers": list(ROSTER),
        "expected_team_count": len(ROSTER), "observed_team_count": len(observed),
        "global_team_year_count": row_count,
        "global_team_year_count_matches": row_count == baseline["global_team_year_count"],
        "rankings_match_baseline": not differences, "ranking_differences": differences,
        "raw_sha256": digest(raw),
        "raw_bytes_match_baseline": digest(raw) == baseline["raw_sha256"],
        "source_last_modified": headers.get("last-modified"),
        "source_last_modified_matches": (
            headers["last-modified"] == baseline["source_last_modified"]
            if "last-modified" in headers else None),
        "observed_rankings": observed,
    }
    result["review_required"] = (
        not result["rankings_match_baseline"] or not result["raw_bytes_match_baseline"]
        or not result["global_team_year_count_matches"]
        or result["source_last_modified_matches"] is False)
    return result


def source_evidence():
    files = {}
    manifest = {"repository": "https://github.com/avgupta456/statbotics",
                "commit": SOURCE_COMMIT, "files": []}
    for upstream_path, (local_name, ranges) in SOURCE_FILES.items():
        url = SOURCE_BASE + "/" + upstream_path
        full, _, _ = fetch(url)
        output = full
        if ranges:
            lines = full.decode("utf-8").splitlines(keepends=True)
            chunks = ["// Excerpts from " + url + "\n"]
            for start, end in ranges:
                chunks.append("// Original lines " + str(start) + "-" + str(end) + "\n")
                chunks.extend(lines[start - 1:end])
            output = "".join(chunks).encode("utf-8")
        files[local_name] = output
        manifest["files"].append({
            "upstream_path": upstream_path, "source_url": url,
            "upstream_sha256": digest(full), "upstream_bytes": len(full),
            "saved_file": local_name, "saved_sha256": digest(output),
            "line_ranges": ranges,
        })
    files["manifest.json"] = json_bytes(manifest)
    return files


def write_new(path, data):
    with path.open("xb") as output:
        output.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--download", action="store_true", help="Fetch the official public cache")
    mode.add_argument("--input", type=Path, help="Verify/decode existing exact compressed bytes")
    parser.add_argument("--check-only", action="store_true", help="Print comparison; write no files")
    parser.add_argument("--include-source-evidence", action="store_true",
                        help="Also download pinned public frontend source and MIT license")
    parser.add_argument("--output-root", type=Path, default=ARTIFACTS / "snapshots")
    args = parser.parse_args()
    if args.include_source_evidence and (not args.download or args.check_only):
        parser.error("--include-source-evidence requires --download without --check-only")

    baseline = load_baseline()
    headers = {}
    effective_url = None
    retrieved_at = None
    if args.download:
        raw, headers, effective_url = fetch(ENDPOINT)
        retrieved_at = utc_text(utc_now())
    else:
        raw = args.input.read_bytes()
    decoded, subset, row_count = decode_snapshot(raw)
    comparison = compare(raw, subset, row_count, baseline, headers)
    evidence = source_evidence() if args.include_source_evidence else {}

    if not args.check_only:
        processed_at = utc_now()
        name = processed_at.strftime("%Y-%m-%dT%H-%M-%S-%fZ") + "_" + digest(raw)[:12]
        folder = args.output_root / name
        args.output_root.mkdir(parents=True, exist_ok=True)
        # mkdir and exclusive file creation refuse to overwrite any previous capture.
        folder.mkdir(exist_ok=False)
        subset_bytes = json_bytes(subset)
        metadata = {
            "schema_version": 1, "season": YEAR,
            "processed_at_utc": utc_text(processed_at),
            "source": {"url": ENDPOINT, "effective_url": effective_url,
                       "retrieved_at_utc": retrieved_at,
                       "source_kind": "official_statbotics_public_cache",
                       "read_mode": "download" if args.download else "local_file",
                       "http_headers": {key: headers[key] for key in (
                           "last-modified", "date", "etag", "content-type", "content-length",
                           "x-goog-generation", "x-goog-stored-content-length") if key in headers}},
            "compression": "zlib", "raw_bytes": len(raw), "raw_sha256": digest(raw),
            "decoded_bytes": len(decoded), "decoded_sha256": digest(decoded),
            "subset_bytes": len(subset_bytes), "subset_sha256": digest(subset_bytes),
            "global_team_year_count": row_count, "subset_team_numbers": list(ROSTER),
            "subset_team_count": len(ROSTER),
            "source_commit": SOURCE_COMMIT,
            "endpoint_provenance": [SOURCE_BASE + "/" + p for p in SOURCE_FILES],
            "baseline_file": "artifacts/statbotics/expected-rankings-2026.json",
            "baseline_sha256": digest(BASELINE_PATH.read_bytes()),
            "review_required": comparison["review_required"],
            "notes": [
                "HTTP Last-Modified is the cache object's timestamp, not this retrieval date.",
                "Ranks are copied from EPA ranks; district_rank is a different FIRST points ranking.",
                "No competing filter or geography filter was applied before extracting the fixed roster.",
                "Pinned frontend source identifies this bucket; DISABLE_GCS=true at that commit means it is not proof of current live frontend use.",
            ],
        }
        write_new(folder / "team-years-2026.json.zlib", raw)
        write_new(folder / "team-years-2026-subset.json", subset_bytes)
        write_new(folder / "rankings-comparison.json", json_bytes(comparison))
        write_new(folder / "metadata.json", json_bytes(metadata))
        if evidence:
            source_folder = folder / "source-evidence"
            source_folder.mkdir()
            for filename, contents in evidence.items():
                write_new(source_folder / filename, contents)
        print("Saved new capture: " + str(folder), file=sys.stderr)
    print(json_bytes(comparison).decode("utf-8"), end="")
    if comparison["review_required"]:
        print("REVIEW REQUIRED: observed data differs from the frozen June 12 baseline. "
              "No existing data or roster was overwritten.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, zlib.error) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        sys.exit(1)
