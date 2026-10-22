# The REFINERY · NEI Robotics Top 10

A broadcast-style screen and media rundown for introducing regional robotics teams to football and baseball audiences. The hero message leads into a 2026 FRC Top 10, individual team profiles, and separate FTC features. Student and adult names retain their exact published roles and evidence dates.

## Use the screen

[Open the public interactive site](https://horner.github.io/refintery-rankings/). Visitors can select a team in the Top 10, switch to its spotlight, explore FTC features, and open presenter notes and sources. Direct profile links work, for example [North Side / 9119](https://horner.github.io/refintery-rankings/#team/9119) and [FTC features](https://horner.github.io/refintery-rankings/#ftc).

The [GitHub Pages workflow](../.github/workflows/pages.yml) rebuilds and verifies the research on every push to `main`, then publishes only `broadcast/dist`. The public site uses the same interactive files as the broadcast screen; PNGs remain optional downloads.

Serve the static files from the repository root:

```bash
python3 -m http.server 8765 --directory broadcast/dist
```

Open `http://localhost:8765`. Use the on-screen controls to select a team, switch between FRC and FTC, show presenter notes, enter fullscreen, and export a 1920 × 1080 graphic. Keyboard shortcuts are listed in the interface. Auto-cycle is on by default and advances FRC teams every 12 seconds; uncheck it to stop. It pauses while the page is hidden, on FTC features, and during PNG export. The controls also link directly to the GitHub source. Presenter notes belong with the announcer; the clean frame is intended for the audience.

The [press kit](dist/press-kit.md) includes an opening script, team rundown, source qualifications, and a draft pitch. It does not send anything to a station.

Ready-to-use 1920 × 1080 graphics: [FRC Top 10](dist/exports/nei-top10-2026.png), [North Side spotlight](dist/exports/team-spotlight-9119.png), and [FTC features](dist/exports/ftc-features.png). The same browser export produces each graphic; dates and role qualifications remain on screen.

School marks appear before the identity text and team marks after it. List thumbnails are compact; team details and spotlights use larger images. Logos are also embedded in PNG exports. All ten FRC teams and both FTC features have verified team marks. PhyXTGears is a community team without a single school logo; R.Amp has no verified published team mark. The [logo manifest](data/logos.json) records source pages, asset URLs, retrieval dates, and checksums; [readable credits](dist/logo-credits.md) travel with the site.

## What the ranking means

The Top 10 sorts the 13 FRC teams in The REFINERY's 12-county Northeast Indiana region by **2026 Statbotics EPA** in the frozen **June 12, 2026** source. A [fresh official FIRST Indiana district roster/profile screening](data/first-fin-scope-audit.json) supports the regional hometown selection. It does not establish workshop locations or student residences. The list is an independent performance ranking, not a voted poll or a live scoreboard.

FTCs 22331 and 25638 are separate 2025–26 features. Rookie 36124 is a 2026–27 watch item. FTC OPR and FRC EPA remain separate. A school-size division is an analogy only: FIRST does not assign FTC/FRC by enrollment; a school can offer either or both.

## Rebuild

```bash
python3 broadcast/scripts/build.py
python3 broadcast/scripts/verify.py
```

The [editorial inputs](data/editorial.json) preserve source-aware spotlight suggestions. The build reads the canonical FRC and FTC research and writes the shared browser data and press kit. No network access is needed for the build. Static assets are hosted locally with the page.

## Credits

- [The REFINERY](https://refineryrobotics.org/): logo and photograph of robots at its practice field, obtained from its public [website source repository](https://github.com/BioNanomics/REFINERY-site). The photograph is a facility image, not a selected-team portrait.
- [FIRST Global's Robotics Is a Sport campaign](https://first.global/sport/): the hero campaign phrase, presented with attribution and career-skills context.
- [FIRST](https://www.firstinspires.org/), [Statbotics](https://www.statbotics.io/), and [FTCScout](https://ftcscout.org/): program, team, and performance evidence documented in the main research.

The on-screen dates and role qualifications travel with the graphics. Confirm current-season appointments with the team when arranging a new interview.
