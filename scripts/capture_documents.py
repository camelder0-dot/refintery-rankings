#!/usr/bin/env python3
"""Record the versions of linked source PDFs; retain links and hashes, not full copies."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

DOCUMENTS = [
    {
        "id": "fwcs-board-robotics-2026-02-09",
        "title": "FIRST Robotics: FWCS High Schools",
        "publisher": "Fort Wayne Community Schools",
        "source_date": "2026-02-09",
        "url": "https://resources.finalsite.net/images/v1770749036/fwcsk12inus/v2dggvv52hkh9sfiqsme/2-9-26Presentation_Roboticshighschool.pdf",
        "relevant_pages": [2, 7],
        "supports": "Page 2 lists program years; page 7 names representatives for North Side, Northrop, Snider, South Side, and Wayne. The title is representative, not captain.",
    },
    {
        "id": "fairmount-minutes-2025-09-08",
        "title": "Fairmount Town Council regular meeting minutes, September 8, 2025",
        "publisher": "Town of Fairmount, Indiana",
        "source_date": "2025-09-08",
        "url": "https://static1.squarespace.com/static/5dc440cbaed3360b099cc5e8/t/68e97523a86b466f4093381a/1760130339609/Regular%2BMeeting%2BMinutes%2B09.08.2025.pdf",
        "relevant_section": "Madison Grant Argyll Attack Robotics Team presentation",
        "supports": "Names Ava Stanley as team spokesperson; does not establish student status or captain title.",
    },
]


def capture(item):
    request = urllib.request.Request(item["url"], headers={"User-Agent": "Fort-Wayne-FRC-research/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        headers = {k.lower(): v for k, v in response.headers.items()}
        resolved = response.url
    if not raw.startswith(b"%PDF"):
        raise ValueError(f"Source did not return a PDF: {item['url']}")
    return dict(item, retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                resolved_url=resolved, response_sha256=hashlib.sha256(raw).hexdigest(),
                response_bytes=len(raw), response_last_modified=headers.get("last-modified"),
                full_document_republished=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output path; source manifests are immutable captures.")
    with ThreadPoolExecutor(max_workers=2) as pool:
        documents = list(pool.map(capture, DOCUMENTS))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as file:
        json.dump({"schema_version": "1.0", "documents": documents}, file, indent=2)
        file.write("\n")
    print(f"Captured {len(documents)} linked PDF hashes in {args.output}")
