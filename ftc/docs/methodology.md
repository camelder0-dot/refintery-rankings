# FTC methodology and field definitions

## Scope and season

This companion directory covers FIRST Tech Challenge separately from the repository's FRC research. It uses the same **60 straight-line miles from Citizens Square, 200 East Berry Street, Fort Wayne**, with the origin and earth-radius convention preserved in the [geographic evidence](../data/geography.json). Distances refer to documented schools, hosts, or explicitly qualified town screening points, rather than driving distance or verified robot workshops.

The comparison season is **2025–26 DECODE**. FIRST FTC Events and FTCScout identify this season by its **starting year, 2025**. This differs from the FRC 2026 season label. The 2026–27 registrations are a separate current-season appendix; they do not receive a 2025–26 ranking. Research and capture dates are separate from competition dates.

Roster discovery starts with the official FIRST Indiana, Ohio, and Michigan regional team lists. The geographic notes record the screening method, inspected boundary cases, inactive historical candidates, and unresolved host locations. This is an evidence-backed directory of located teams, with the coverage limits stated, rather than a guarantee that every community team has been found.

## FTCScout metric and ranking population

The ranking metric is **peak event non-penalty OPR**, called **Best OPR** on FTCScout. The pinned [FTCScout implementation](https://github.com/ftc-scout/ftc-scout/blob/05c44a28fe0f0a80101e63134db9a518d9d7ed6c/packages/server/src/graphql/resolvers/Team.ts#L54-L151) takes each team's maximum event `total_points_np` OPR among nonremote events that have statistics and do not use modified rules. OPR estimates an individual robot's contribution from scored qualification-match alliance results, using the source's [least-squares calculation](https://github.com/ftc-scout/ftc-scout/blob/05c44a28fe0f0a80101e63134db9a518d9d7ed6c/packages/common/src/logic/stats/calculate-opr.ts). It is a model, not a directly measured individual score. A larger value ranks higher. It is an event peak, not a season-wide average, and it is not Statbotics EPA.

The source's eligibility rule does not impose a FIRST Championship cutoff. Later eligible events, including postseason events, can affect the captured result. The directory reports a frozen source retrieval with its actual precision and qualifications; it does not imply an April or June snapshot that was never captured.

FTCScout's world rank and regional rank are distinct source queries. **A regional rank filters by the event's assigned `regionCode`, not by the team's home state or the event's street address.** A traveling team can enter that region's comparison. Tables therefore label this field **event-region rank**, never home-state rank. The region code, source denominator, and unavailable fields remain explicit. SQL `rank()` gives tied values the same position and skips later positions; a local sort does not replace the source rank.

The world and regional values are separate maxima. For 22331, the worldwide best comes from the June 2026 Michiana Premier Croft division, assigned region **FPE**, while the USIN best comes from Westfield QT. The Premier event is physically in Indiana but does not enter the USIN query. Both values are shown beside their corresponding ranks.

FRC EPA, FTC OPR, an event's qualification rank, advancement points, and judged awards answer different questions. They must not be combined into one numerical leaderboard. A registered team without qualifying statistics has an unavailable rank, not a score or rank of zero.

## Recorded seasons and rookie year

The [FIRST extracts](../artifacts/first/season-history-through-2025.json) retain the linked **Other Seasons** entries and the verified season page. For a one-season team whose page omits the menu, the displayed season is the record. Counts include only starting-year labels through 2025; later registrations are excluded. These are recorded season entries, not a guarantee of played matches.

The observed FIRST FTC Event Web histories in this capture list no season earlier than 2019. Older rookie teams can therefore have a shorter recorded history than their total lifetime participation. The official rookie year is reported separately. Missing years are not filled by subtraction, interpolation, or an anniversary claim.

FTCScout's `activeSeasons` is not used as evidence of current-season activity: its [pinned resolver](https://github.com/ftc-scout/ftc-scout/blob/05c44a28fe0f0a80101e63134db9a518d9d7ed6c/packages/server/src/graphql/resolvers/Team.ts#L159-L169) appends the current season to the match-derived list. FIRST registration pages and actual statistics are kept separate.

## School, community, and leadership evidence

Official season sponsor/affiliation text and public school/team sources establish the school or community connection. A sponsor field is retained as evidence, not treated as proof that all sponsors host the team. Wire Monkeys is a home-school/community program; its town does not establish a Hilltop school connection. NSCC's name does not establish a college affiliation or authorize importing a different FRC team's advisor.

Leadership records preserve the published spelling, exact role, relevant season, evidence date or undated status, source links, and limits. Partial names remain partial. A program coach covering two FTC teams is identified at that level. Undated self-reported roles do not establish a particular season's appointment. A driver, coder, lead programmer, notebook manager, mentor, or quoted participant is not silently relabeled as a captain or head coach.

An alliance-selection **Captain** field in event results refers to a team's alliance role, not a named student leader. An empty leadership list or null captain means no qualifying public identification was found in the reviewed sources; it does not mean no leader exists. Names of an organization's general staff are not assigned to individual teams without team-specific evidence.

## Preservation and corrections

The data files preserve factual extracts, source URLs, capture metadata, and qualifications. Full articles and third-party portfolios remain linked to their publishers. The build runs offline against selected captures. Fresh capture commands must write new files; a new response does not silently replace the publication's snapshot.

For a correction, supply the team number, exact role or fact, applicable season, and a public team/school or official FIRST source. Update curated inputs, rebuild, and verify both program directories and the root checksum manifest. Preserve historical evidence as historical.
