# FTC evidence and source captures

The completed comparison season is **2025–26 DECODE**, represented as starting year **2025** by FIRST and FTCScout. Research date: **October 22, 2026**. These files are frozen evidence, not a live leaderboard.

## Rankings

The [FTCScout snapshot](ftcscout/snapshots/2026-10-22/) contains 24 exact response bodies with request URLs, HTTP statuses, response headers, byte counts, SHA-256 hashes, and UTC retrieval times. Fourteen quick-stat responses supply world and event-region values/ranks for seven teams. Team 32552 has two preserved HTTP 404 quick-stat responses and an empty successful event list. Eight team-event responses preserve the event OPR values underlying the peaks.

The [snapshot manifest](ftcscout/snapshots/2026-10-22/manifest.json) records a retrieval interval of **05:15:39–05:16:58 UTC**. This is a sequence of queries, not an atomic database transaction. The HTTP Date and cache headers describe the response; the API does not provide a separate metric computation timestamp. The world denominator is 8,368; the USIN event cohort has 71 teams and USOH has 113. These are source denominators, not counts of local teams.

The [normalized extract](ftcscout/snapshots/2026-10-22/local-ranking-extract.json) is reproduced from those bodies by the [offline normalizer](../scripts/normalize_ftcscout.py). The selected [ranking input](../data/rankings.json) retains those fields and adds explicit interpretation. JSON and CSV retain the source numbers; Markdown tables display two decimal places.

Five additional [best-event metadata responses](ftcscout/snapshots/2026-10-22/event-metadata/) establish names, dates, assigned region codes, and eligibility. Canterbury 22331's worldwide best event is the Michiana Premier Croft division in June, assigned **FPE**, whereas its USIN best is Westfield QT. An event's physical state does not override its assigned region code.

The algorithm is documented against [FTCScout commit 05c44a2](https://github.com/ftc-scout/ftc-scout/blob/05c44a28fe0f0a80101e63134db9a518d9d7ed6c/packages/server/src/graphql/resolvers/Team.ts#L54-L151). No upstream source code is copied here. See the [methodology](../docs/methodology.md) for qualification-match OPR, peak selection, ties, populations, and limitations.

## FIRST identities, history, and geography

- [Season histories](first/season-history-through-2025.json) preserve factual official team-season menu extracts, rookie years, and original page hashes for the included teams and principal boundary candidates. Counts exclude later registrations and can omit pre-2019 history.
- [Current-season rookie](first/current-season-new-teams.json) preserves FTC 36124's 2026–27 registration separately; it has no recorded season through the 2025 cutoff.
- [Official regional rosters](first/official_region_rosters.json) preserve full factual IN, OH, and MI regional team-list extracts for 2024–26, source hashes, and retrieval dates.
- [Official profile facts](first/official_profile_facts.json) preserve affiliation/sponsor text and registration qualifications.
- [NCES school records](first/nces_school_source_records.json), [Census address matches](first/census_address_source_records.json), and [place screening](first/census_place_screening.json) preserve coordinate source evidence. Public-school records refer to 2024–25 and private-school records to 2023–24; these are estimated school references.
- [Geographic research extract](first/geography_research.json) retains the original candidate decisions. The selected [geographic input](../data/geography.json) includes the origin, qualified town references, school references, exclusions, and the [REFINERY host geocode](first/refinery-host-geocode.json) used for the current-season addition.

Full FIRST HTML pages and third-party school pages remain at their publishers. These files contain factual extracts and response hashes rather than full-page copies.

## Leadership and exports

The [leadership preservation manifest](source-preservation-manifest.json) records original byte counts and response hashes for six accessible role-bearing sources. Direct LinkedIn access was blocked; the profile's search-visible, self-reported coach/mentor lead is preserved with that access limitation and uncertain seasonal currency. An error response is not treated as a successful copy of the profile.

The [role extracts](role-source-factual-extracts.json) and [portfolio extract](random-portfolio-role-extract.json) preserve relevant facts and locators. Canterbury's portfolio version date is not represented as a publication date. Its educator/engineer biographies do not establish coach or mentor titles. Full portfolios and news stories remain linked to their publishers.

The [CSV matrices](export-tables.json) retain typed export values. The [combined JSON](../data/teams.json), [team CSV](../data/teams.csv), [leadership CSV](../data/leadership.csv), and Markdown directories are generated offline.

## Reproduction and new captures

From the repository root:

```bash
python ftc/scripts/build.py
python ftc/scripts/verify.py
python scripts/verify.py
```

To inspect the frozen ranking derivation without contacting a service:

```bash
python ftc/scripts/normalize_ftcscout.py ftc/artifacts/ftcscout/snapshots/2026-10-22
```

Fresh captures require a new output path:

```bash
python ftc/scripts/capture_ftcscout.py --out /tmp/ftcscout-new-capture
python ftc/scripts/capture_first.py --teams 22331 25638 5501 14174 12802 19778 30782 32552 --through 2025 --output /tmp/ftc-first-history-new.json
```

A fresh capture does not update the selected publication. Review its source, metric, population, season, and missing responses before changing curated inputs. The repository-wide [SHA-256 manifest](../../SHA256SUMS) covers all published files. After an intentional correction and rebuild, regenerate it with `python scripts/verify.py --write-checksums`, then rerun verification.
