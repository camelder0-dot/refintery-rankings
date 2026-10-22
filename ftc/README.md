# FIRST Tech Challenge around Fort Wayne

**2025–26 DECODE · research date 2026-10-22**

New to robotics? Our [introduction for football and baseball fans](../README.md#new-to-robotics-a-guide-for-football-and-baseball-fans) explains FTC, FRC, alliances, and how to read the ratings. [The REFINERY](https://refineryrobotics.org/) supports local teams; learn how to [find a team or get involved](https://refineryrobotics.org/get-involved/).

8 season-rostered teams in the study area, with school/community affiliations, geographic qualifications, recorded FIRST seasons, and public leadership evidence. Current-season additions are listed separately.

Rankings use FTCScout peak event non-penalty OPR for 2025–26 DECODE, captured October 22, 2026. World and event-region best OPR are shown separately. USIN and USOH rank teams that competed in events assigned those region codes, regardless of home state; they are not home-state rankings. Values display two decimals; JSON and CSV preserve the source numbers.

| Resource | Contents |
|---|---|
| [Team directory](docs/team-directory.md) | Rankings, schools/programs, distances, seasons, and leadership |
| [Combined JSON](data/teams.json) / [team CSV](data/teams.csv) | Joined facts, sources, and qualifications |
| [Leadership evidence](docs/leadership-findings.md) / [CSV](data/leadership.csv) | Exact adult/student roles, dates, uncertainty, and gaps |
| [Methodology](docs/methodology.md) | Metric, population, season labels, and evidence policy |
| [Geographic scope](docs/geographic-scope.md) | Origin, reference points, boundary exclusions, and census limits |
| [Sources](docs/sources.md) / [artifacts](artifacts/README.md) | URLs, preserved facts, metadata, and reproduction |

| Team | School / community program | Approx. miles | World Best NP OPR | World rank | Region Best NP OPR | Event-region rank | Recorded seasons |
|---|---|---:|---:|---|---:|---|---|
| [22331 random()](https://ftc-events.firstinspires.org/2025/team/22331) | [Canterbury High School](https://www.canterburyschool.org/) | 4.1 | 88.85 | 861 / 8,368 | 78.67 | USIN 13 / 71 | 4 (2022, 2023, 2024, 2025) |
| [14174 Cougar Robotics](https://ftc-events.firstinspires.org/2025/team/14174) | [Van Wert High School](https://www.vwcs.net/) | 32.0 | 42.02 | 3138 / 8,368 | 42.02 | USOH 34 / 113 | 7 (2019, 2020, 2021, 2022, 2023, 2024, 2025) |
| [25638 MG (Microchips & Guac)](https://ftc-events.firstinspires.org/2025/team/25638) | [Madison-Grant Jr./Sr. High School](https://mghs.mgusc.k12.in.us/) | 55.6 | 39.17 | 3455 / 8,368 | 39.17 | USIN 30 / 71 | 2 (2024, 2025) |
| [12802 We Will Bot You](https://ftc-events.firstinspires.org/2025/team/12802) | [Coldwater High School](https://www.coldwatercavs.org/) | 49.1 | 34.65 | 4030 / 8,368 | 34.65 | USOH 48 / 113 | 7 (2019, 2020, 2021, 2022, 2023, 2024, 2025) |
| [19778 Wire Monkeys](https://ftc-events.firstinspires.org/2025/team/19778) | [Country Club Robotics / home-school community](https://www.countryclub.io/wire-monkeys/) | 54.4 † | 33.34 | 4209 / 8,368 | 33.34 | USOH 50 / 113 | 5 (2021, 2022, 2023, 2024, 2025) |
| [5501 VW Robotics](https://ftc-events.firstinspires.org/2025/team/5501) | [Van Wert High School](https://www.vwcs.net/) | 32.0 | 23.12 | 5718 / 8,368 | 23.12 | USOH 71 / 113 | 7 (2019, 2020, 2021, 2022, 2023, 2024, 2025) |
| [30782 ROBO DOGS](https://ftc-events.firstinspires.org/2025/team/30782) | [Celina High School](https://www.celinaschools.org/CHS.aspx) | 47.2 | 14.99 | 7014 / 8,368 | 14.99 | USOH 92 / 113 | 1 (2025) |
| [32552 NSCC](https://ftc-events.firstinspires.org/2025/team/32552) | Family/Community; school or physical host unconfirmed | 52.8 † | Unavailable | Unavailable | Unavailable | USOH Unavailable | 1 (2025) |

† Town screening point; physical meeting/workshop address remains unconfirmed. Other distances use school/host reference points. FIRST season-entry counts can omit pre-2019 history and do not count only seasons with played matches. A missing ranking or leader is left unavailable rather than inferred.

## 2026–27 registrations

- [36124 R.Amp Robotics](https://ftc-events.firstinspires.org/2026/team/36124) — Amp Lab at The REFINERY; current-season rookie, outside the 2025–26 rankings.

## Rebuild and verify

From the repository root, using Python's standard library:

```bash
python ftc/scripts/build.py
python ftc/scripts/verify.py
python scripts/verify.py
```

A fresh source capture must use a new output filename or directory. Review its metric, season, population, and qualifications before changing the selected publication. See the [artifact inventory](artifacts/README.md).

[Return to both FIRST programs](../README.md).
