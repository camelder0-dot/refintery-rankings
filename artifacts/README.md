# Evidence and supporting artifacts

This directory preserves the factual evidence, capture metadata, and reproducible export inputs used for the Fort Wayne-area FIRST Robotics study. The research date is **October 22, 2026**. The preserved Statbotics object was last modified **June 12, 2026**; its October retrieval date does not make the rankings October-current.

The earlier research was discussed in chat. This publication creates a durable evidence package from the recorded findings and fresh preservation captures. It does not claim that every file here existed during the original discussion.

## Preserved Statbotics response

The fixed capture is under [the dated snapshot directory](statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/).

| Artifact | What it contains |
|---|---|
| [Original compressed response](statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/team-years-2026.json.zlib) | The exact 714,810 bytes downloaded from the official Statbotics cache; 3,724 team-year records when decoded. |
| [Decoded 17-team subset](statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/team-years-2026-subset.json) | Every original field for the study teams and the original top-level year object. |
| [Capture metadata](statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/metadata.json) | Retrieval time, source URL, selected HTTP headers, file sizes, and checksums. |
| [Baseline comparison](statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/rankings-comparison.json) | Verification that the saved response matches the frozen study rankings and denominators. |
| [Expected rankings](statbotics/expected-rankings-2026.json) | The explicit baseline used by the Statbotics capture script. |
| [Pinned source evidence and license](statbotics/snapshots/2026-10-22T04-29-18-072314Z_0059dfe792a0/source-evidence/) | Official Statbotics frontend files and a relevant constants excerpt establishing the endpoint and format, with the upstream MIT notice. |

The [Statbotics provenance document](../docs/statbotics-provenance.md) explains field definitions, source-code provenance, the cache's freshness limit, and commands to decode or verify the saved data. The raw response SHA-256 is `0059dfe792a03f257cf20d94580daab4d669e955e8a08c409d98acf80fd790b3`.

## FIRST season histories and linked documents

| Artifact | What it contains |
|---|---|
| [FIRST season-history extract](first/season-history-through-2026.json) | Official rookie years, recorded season entries through 2026, explicit registered-without-competition years, and retrieval metadata for all 17 teams. Full source pages remain linked. |
| [Document manifest](source-manifests/documents.json) | Source URLs, relevant pages or sections, response sizes, retrieval dates, and hashes for the FWCS robotics board presentation and Fairmount council minutes. The complete third-party PDFs are linked at their publishers. |
| [CSV input matrices](export-tables.json) | Typed headers and values used to author the 17-row team CSV and 37-row leadership CSV. |

The separate [geographic evidence](../data/geography.json) records the origin, coordinates, address sources, boundary checks, and exclusions. [Leadership evidence](../data/leadership.json) records each person's documented role, evidence date, source links, limitations, and unfilled roles. The [complete source catalog](../docs/sources.md) and [machine-readable catalog](../data/sources.json) join these materials to the relevant teams.

## Reproduction and integrity

Run the commands in the [repository README](../README.md) to rebuild the combined data and reports offline. The committed [checksum manifest](../SHA256SUMS) covers all published files except the manifest itself. `python scripts/verify.py` checks those hashes alongside the source joins, rankings, season counts, distances, CSV values, and documentation links.

The source articles, public profiles, social posts, podcasts, and third-party PDFs remain linked to their publishers. The repository retains factual findings and their qualifications, the official Statbotics data response, and the small licensed source-code evidence described above. See [third-party notices](../THIRD_PARTY_NOTICES.md).
