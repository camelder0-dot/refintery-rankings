# FTC roster, affiliations, and geography research

Research date: 2026-10-22. Completed season is FIRST API season 2025 = DECODE 2025–26. 2026 is the new 2026–27 BIOBUZZ season and is a separate watch list.

## Completed-season roster interpretation

Six school-based competitive teams have strong school-reference evidence inside 60 miles: 22331 random() (Canterbury), 25638 MG (Madison-Grant), 5501 and 14174 (Van Wert High), 12802 (Coldwater OH High), and 30782 (Celina High). 19778 Wire Monkeys has an official registered Alvordton OH location and Country Club Robotics / Home School affiliation; the 54.4064-mile town reference is screening only, because no physical workshop address was verified. Include provisionally and state this.

32552 NSCC is registered in Archbold OH with a 52.7604-mile town screening reference and 2025 Family/Community affiliation. Its official profile explicitly reports no official events. Give it an unranked / registered-only entry. Its 2026 name is NSCC Cryptic Cyborgs and sponsors are Wieland & Family/Community. A physical Northwest State Community College host link was NOT verified for this FTC number. The NSCC website's well-documented FRC 6181 connection does not establish FTC 32552's host or mentors.

36124 R.Amp Robotics is a 2026 rookie and belongs in a new-season watch list, separate from completed 2025 results. Official sponsors identify Family/Community & Amp Lab at Electric Works, The REFINERY, BioNanomics, Indiana Department of Education. 8710 Frostbyte reappears in the retrieved 2026 roster with E3 Robotics Center affiliation; use the existing repository's E3 host at 3709 Cassopolis Street, outside 60 miles, rather than its Elkhart place point.

## Boundary resolutions

- 12166 and 32403 New Bremen: town point 59.6862 miles and Census street interpolation 59.9647 would suggest inclusion. The NCES school point at 40.436403, -84.362067 gives 60.191191 miles. Use the school point and exclude, with a near-boundary qualification.
- 13028 Cougar-Bots (St Charles Borromeo, Coldwater MI): NCES private-school point 41.94287, -85.007401 gives 60.036504 miles, just outside the fixed radius. It is extremely close to the threshold; estimated coordinates and origin choice matter. Preserve unrounded decision and do not pretend survey precision.
- 32341 Iron Talons (Legg, Coldwater MI): NCES point 41.9501, -85.0167 gives 60.481080 miles, outside.
- 24051 Technopups (Centreville MI): NCES point 41.917966, -85.525614 gives 61.309706 miles, outside.
- 22601 RoboComets Jr (Jonesville MI): NCES middle-school point is outside, about 67 miles.
- 25638 MG is INSIDE using Madison-Grant's NCES school reference point, 55.623002 miles. Its registered Fairmount town point is 52.97 miles; do not accidentally classify Fairmount outside based on driving distance.
- Osceola's 12014 / 14596 / 26448 screen at 63.4 miles; Fort Loramie's 14279 screens at 64.69. These are screening exclusions; no precise team-workshop claim was made.

## Prior-season historical candidates

Five prior-season local MI teams are in 2024 regional records and absent from both retrieved 2025 and 2026 regional lists: 10540 Gear Grinders Junior (Camden-Frontier), 20101 Triple B (Bronson), 11714 Burr Oak BossCats, 15322 Bosscats 2.0 (Burr Oak), 26536 Waldron Spartans (Waldron Area Schools). All linked NCES school references are within 60. Label them historical / no current registration observed, not dissolved. This historical scan covered 2024; it is not an all-time inventory. An older Van Wert club page also mentions 20116 Where's The Tape Measure in 2022; it is not in any inspected 2024–26 regional roster, so was not promoted into the current cohort.

## Census coverage and limits

This is a thorough roster screening attempt, not a guaranteed census of every team or every workshop. Official regional pages are regional registrations. A team physically in the study area could be assigned to another region; no global all-region census was performed. Teams omitted from FIRST's registration lists or using a different registered city could be missed.

All returned 2024/25/26 IN/MI/OH region rows were inspected by registered location. Matching Census places were screened to a 75-mile buffer to find near-boundary candidates. The exported screening rows retain all matches <=75 miles. Unmatched rows are explicitly retained. Most are obvious distant city/township variants (Indianapolis; southeast/northern Michigan; Lewis Center/West Chester OH) rather than local border towns. The ambiguous `IN, IN, USA` record is 32814 CC Skraps; its official 2025 sponsor is Central Catholic Jr Sr High School, not evidence of a local unknown Fort Wayne team. We did not manufacture numerical distances for these unmatched places.

The 2025 regional lists return no teams registered to Huntington, Angola, Kendallville, New Haven, Decatur, Bluffton, Wabash, Marion, Warsaw, Goshen, Sturgis, Defiance, Bryan, or Lima. This is absence from inspected regional registration snapshots, not a claim that those places have no robotics or no FTC group at all. Those school systems often have FRC/FLL teams; program numbers must not be substituted.

Additional targeted web queries for FTC in Huntington IN, Angola IN, Sturgis MI found no new numbered current FTC team. Michigan's FY26 Section 99h official award list identifies Sturgis 11407 explicitly as FIRST Robotics Competition; it is not an FTC candidate.

## Primary sources

- NCES method: https://nces.ed.gov/programs/edge/geographic/schoollocations
- Census Gazetteer: https://www.census.gov/geographies/reference-files/2025/geo/gazetter-file.html
- Gazetteer source ZIP: https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_place_national.zip
- Canterbury address: https://www.canterburyschool.org/contact-us
- Madison-Grant contact: https://mghs.mgusc.k12.in.us/page/contact-us (page has both 11580 S E00W and 11700 S E00W; NCES specific high-school point uses 11700)
- St Charles school address: https://scbcatholicschool.org/
- Legg address: https://www.coldwaterschools.org/o/lms/
- New Bremen address: https://www.newbremenschools.org/schools.aspx
- Wire Monkeys team: https://www.countryclub.io/wire-monkeys/
- Van Wert team club, linked from official FIRST profile: https://van-wert-robotics-club.webnode.page/l/2023-van-wert-ftc-competition/
- E3 host: https://www.e3robotics.org/findoutmore.html
- FIRST Indiana state event includes team 22331: https://www.firstindianarobotics.org/ftc/events/indiana-state-championship/
- Refinery affiliations including Madison-Grant FTC25638: https://refineryrobotics.org/about/

The [geographic inputs](../data/geography.json) retain the exact coordinates and arithmetic. Source extracts are preserved under [FIRST artifacts](../artifacts/first/). Full news articles and school pages remain linked to their publishers.
