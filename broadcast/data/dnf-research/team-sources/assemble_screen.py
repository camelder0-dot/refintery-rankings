import json,pathlib,datetime,re,hashlib,requests
BASE=pathlib.Path(__file__).parent
ROOT=BASE.parent
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
profiles=json.load(open(BASE/'nearby-profiles.json'))
for r in profiles:r.pop('sourceIntroText',None)
for r in profiles:
 p=BASE/f"{r['program'].lower()}-{r['season']}-{r['teamNumber']}.json"
 if p.exists():p.write_text(json.dumps(r,indent=2)+'\n')
(BASE/'nearby-profiles.json').write_text(json.dumps(profiles,indent=2)+'\n')
# Structured aliases are deliberately narrower than districts: co-located virtual schools, general district members and team sponsors do not inherit affiliation.
positives=[]
def add(name,state,aliases,teams,decision,note,extra=[]):
 evidence=[]
 for prog,num in teams:
  p=next(x for x in profiles if x['program']==prog and x['teamNumber']==num)
  evidence.append({k:p[k] for k in ['program','teamNumber','season','heading','registeredLocation','schoolAffiliationHeadline','sponsorsAndAffiliations','sourceUrl','retrievedAt','sourceSha256']})
 positives.append({'schoolName':name,'state':state,'aliases':aliases,'classification':decision,'note':note,'teamEvidence':evidence,'additionalSources':extra})
A='exclude-active/recent';F='former-review';C='community-participation-review'
add('Huntington North High School','IN',['Huntington North High School'],[('FRC',1501)],A,'Community 4-H team; the school connection is documented separately. Do not infer all Huntington County schools are affiliated.',[{'sourceUrl':'https://huntingtonnhs.ss13.sharpschool.com/get_involved/clubs/robotics','evidence':'Huntington North school robotics page establishes connection to Team THRUST.'},{'sourceUrl':'https://refineryrobotics.org/about/','evidence':'REFINERY identifies Huntington North Team THRUST among local teams.'}])
for name,aliases,num in [('North Side High School',['North Side High School'],9119),('R Nelson Snider High School',['R. Nelson Snider High School','R Nelson Snider High School','Snider High School'],9431),('Homestead High School',['Homestead High School'],4982),('Northrop High School',['Northrop High School'],10434),('East Noble High School',['East Noble High School'],8103),('Carroll High School',['Carroll High School'],10332),('Madison-Grant Jr./Sr. High School',['Madison-Grant Jr./Sr. High School','Madison-Grant Jr Sr High Sch','Madison-Grant High School'],8742),('South Side High School',['South Side High School'],10172),('Wayne High School',['Wayne High School'],10411)]:
 ts=[('FRC',num)]
 if num==8103:ts += [('FRC',8431),('FRC',8432)]
 if num==8742:ts += [('FTC',25638)]
 add(name,'IN',aliases,ts,A,'Current 2027 FRC registration and named school affiliation; played matches are not required to establish a registered team.')
add('Canterbury High School','IN',['Canterbury High School','Canterbury School'],[('FTC',22331)],A,'Current 2026–27 FTC registration names Canterbury High School.')
add('Amp Lab at Electric Works','IN',['Amp Lab at Electric Works','Amp Lab'],[('FTC',36124)],A,'New 2026–27 FTC registration explicitly names Amp Lab at Electric Works. No official matches yet does not imply no team.')
for name,aliases,num in [('CamdenFrontier K12 School',['CamdenFrontier K12 School','Camden-Frontier School','Camden-Frontier K-12 School'],5559),('Waldron Area Schools',['Waldron Area Schools','Waldron School','Waldron High School'],6556),('Sturgis High School',['Sturgis High School'],11407),('Burr Oak High School',['Burr Oak High School','Burr Oak Cmty School'],5501)]:
 add(name,'MI',aliases,[('FRC',num)],A,'Registered for the 2026 FRC season or 2027 season. Burr Oak 5501 has no recorded 2026 district matches; registration is still positive affiliation evidence.' if num==5501 else 'Named school affiliation in the latest official FRC season profile.')
add('Van Wert High School','OH',['Van Wert High School'],[('FTC',14174),('FTC',5501),('FRC',8037)],A,'Two current 2026–27 FTC registrations; also retained former FRC 8037 history.')
add('Coldwater High School','OH',['Coldwater High School'],[('FTC',12802)],A,'Current 2026–27 FTC registration names Coldwater High School in Ohio; distinguish Coldwater, Michigan middle-school teams.')
add('Celina High School','OH',['Celina High School'],[('FTC',30782)],A,'Recent 2025–26 FTC school-affiliated team. Not currently found in 2026–27 roster, so do not present as a school with no team.')
add('Bronson JrSr High School','MI',['Bronson JrSr High School','Bronson Jr Sr High School','Bronson Junior/Senior High School'],[('FTC',20101)],F,'Latest located official FTC affiliation is 2024–25. Not in the 2025 or 2026 regional roster. Recheck for relaunch or current affiliation; absence of a current roster row is not proof of closure.')
add('Rochester Community High School','IN',['Rochester Community High School','Rochester Cmty High School'],[('FRC',2909)],F,'Latest located official FRC season is 2024, with named Rochester school affiliation. No 2025–27 registration in screened rosters; invite a restart conversation with history shown.')
nscc='https://northweststate.edu/wp-content/uploads/2025/04/NSCC-Led-Team-to-Compete-in-State-First-Robotics-Comp.pdf'
for name,aliases in [('Ayersville High School',['Ayersville High School']),('Fairview High School',['Fairview High School']),('Napoleon Junior/Senior High School',['Napoleon Junior/Senior High School','Napoleon High School']),('Four County Career Center',['Four County Career Center'])]:
 add(name,'OH',aliases,[('FRC',6181)],C,'NSCC March 24, 2025 release explicitly lists students from this school on community FRC 6181. This establishes recent student participation, not a separately school-run team. Current affiliation needs confirmation.',[{'sourceUrl':nscc,'evidenceDate':'2025-03-24','publisher':'Northwest State Community College','evidence':'College release names Ayersville, Central Local (Fairview), Delta, Liberty Center, Napoleon, Wauseon and Four County Career Center as schools of team members.'}])
add('Lima Senior High School','OH',['Lima Senior High School'],[('FRC',3777)],C,'Local TV reporting March 17, 2026 identifies a Lima Senior student on the Lima Family YMCA community team. Hold for affiliation confirmation; this is not a separately school-operated team.',[{'sourceUrl':'https://www.hometownstations.com/news/allen_county/lima-bean-city-bots-ready-robot-for-first-robotics-competition-buckeye-regional/article_e5d3d483-ada8-4a44-91a8-361777fc6b54.html','evidenceDate':'2026-03-17','publisher':'WLIO/Hometown Stations','evidence':'Report names a Lima Senior senior as a Bean City Bots participant. Secondary reporting; not official district affiliation.'}])
add('Delta High School','IN',['Delta High School'],[('FRC',1720)],C,'A 2018 report written by the team media group explicitly names Delta High School members. Evidence is historical; current participation is unverified. Keep out of a clean no-team-found assertion unless the historical connection is disclosed.',[{'sourceUrl':'https://www.munciejournal.com/2018/04/phyxtgears-headed-to-world-championship/','evidenceDate':'2018-04-23','publisher':'Muncie Journal; by PhyXTGears Media Team','evidence':'Team-authored article identifies two Delta High School students as PhyXTGears members.'}])
# Capture hash and concise factual digest for non-FIRST evidence.
sourcefacts=[]
for u in sorted({s['sourceUrl'] for p in positives for s in p['additionalSources']}):
 try:
  r=requests.get(u,timeout=30);sourcefacts.append({'sourceUrl':u,'retrievedAt':NOW,'httpStatus':r.status_code,'sha256':hashlib.sha256(r.content).hexdigest(),'bytes':len(r.content),'evidence':next(s['evidence'] for p in positives for s in p['additionalSources'] if s['sourceUrl']==u)})
 except Exception as e:sourcefacts.append({'sourceUrl':u,'retrievedAt':NOW,'error':type(e).__name__})
(BASE/'community-and-school-sources.json').write_text(json.dumps(sourcefacts,indent=2)+'\n')
for p in positives:
 for s in p['additionalSources']:
  s['retrievedAt']=NOW
schools=json.load(open(ROOT/'school-universe.json'))['schools']
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
joined=[]
for s in schools:
 matches=[p for p in positives if p['state']==s['state'] and norm(s['name']) in {norm(x) for x in [p['schoolName']]+p['aliases']}]
 for p in matches:
  p.setdefault('ncesIds',[]).append(s['ncesId'])
 joined.append({'ncesId':s['ncesId'],'schoolName':s['name'],'state':s['state'],'classification':matches[0]['classification'] if matches else 'no-school-affiliation-verified-in-roster-screen','positiveSchoolName':matches[0]['schoolName'] if matches else None})
result={'schemaVersion':'1.0','researchDate':'2026-10-22','retrievedAt':NOW,'publicAbsenceLabel':'No school-affiliated FTC/FRC team verified','method':['Screened official FRC all-team rosters 2023–2027 for Indiana, Michigan and Ohio; checked local candidate team profiles, including registered teams without match statistics.','Screened official FTC regional rosters 2024, 2025, 2026 for USIN, USMI and USOH and official school affiliations for nearby candidates. 2026 FTC means 2026–27 BIOBUZZ.','Town internal points screened a 75-mile buffer; geography of schools is independently determined by the school-universe data. Profiles beyond 60 miles retained for boundary checking.','Named positive school affiliations and documented community-team participants are retained; a nearby community team does not establish that every local school has a team.','Only matching named school/campus is assigned affiliation. A district-level team, co-located virtual academy, sponsor, or career center does not automatically receive the school affiliation.','The absence label describes this public-record screen and is not proof that a team, informal program or new registration does not exist. Robotics activities outside FIRST are outside this screen.'], 'classificationDefinitions':{A:'School named in current 2027 FRC, 2026 FRC or current/recent 2026/2025 FTC registration; excluded even if no matches.',F:'Known former school-affiliated team; disclose prior team and seek current/relaunch confirmation.',C:'Named student participation in a community team; current school affiliation or separate team operation unverified.','no-school-affiliation-verified-in-roster-screen':'No named positive match in screened rosters and supporting research; qualified candidate status, not proof of absence.'},'rosterSources':[{'program':'FRC','seasons':[2023,2024,2025,2026,2027],'sourceUrlTemplate':'https://frc-events.firstinspires.org/{season}/allteams','artifacts':'team-sources/frc-allteams-{season}.json'},{'program':'FTC','seasons':[2024,2025,2026],'regions':['USIN','USMI','USOH'],'sourceUrlTemplate':'https://ftc-events.firstinspires.org/{season}/region/{region}','artifact':'../../../../ftc/artifacts/first/official_region_rosters.json'}],'positiveSchoolAffiliations':positives,'candidateScreen':joined,'boundaryAndOtherProgramsNotes':['New Bremen FTC12166/32403 names New Bremen High School, but the school reference is beyond 60 miles in the earlier geography audit; do not silently include by town point.','Michigan FTC32341 is Legg Middle School, 13028 is St Charles Borromeo School, 22601 is Jonesville Middle School; do not transfer these to an unrelated high school.','FRC5402 Logansport/Lewis Cass school affiliation is outside the 60-mile school universe; current 2027 listing uses a nonstandard city string.','Community FTC32552 NSCC Cryptic Cyborgs only names Family/Community, and its number/name do not establish it inherits FRC6181 former student-school list.','Sponsorship by Vantage Career Center of FRC8037 does not establish school team affiliation.']}
(ROOT/'team-screen.json').write_text(json.dumps(result,indent=2)+'\n')
print('positive school records',len(positives));print('joined',[(c,sum(r['classification']==c for r in joined)) for c in [A,F,C,'no-school-affiliation-verified-in-roster-screen']]);print('unmatched positives',[(p['schoolName'],p['state']) for p in positives if not p.get('ncesIds')])
