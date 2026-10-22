import requests,bs4,json,pathlib,hashlib,datetime,concurrent.futures,re
BASE=pathlib.Path(__file__).parent
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
frc=json.load(open(BASE/'frc-nearby-screen.json'))['nearby']
ftc=json.load(open('ftc/artifacts/first/census_place_screening.json'))['nearby_screening_rows']
latest={}
for prog,rows in [('FRC',frc),('FTC',ftc)]:
 for r in rows:
  n=int(r['number']);y=r['season']; k=(prog,n)
  if k not in latest or y>latest[k]['season']:latest[k]={**r,'program':prog}
# Mosherville is unmatched to incorporated-place gazetteer and is north of study area, still capture newest relocated CRTechnic affiliation
latest[('FRC',11778)]={'program':'FRC','number':11778,'season':2027,'location':'Mosherville, Michigan, USA'}
def fetch(r):
 p=r['program'];n=int(r['number']);y=r['season']; cached=BASE/f'{p.lower()}-{y}-{n}.json'
 if cached.exists():return json.loads(cached.read_text())
 u=f'https://{p.lower()}-events.firstinspires.org/{y}/team/{n}';raw=requests.get(u,timeout=60).content;s=bs4.BeautifulSoup(raw,'html.parser');text=s.get_text('\n',strip=True);lines=text.splitlines();heading=next((x for x in lines if x.startswith(f'Team {n} -')),'')
 school='';sponsors='';location=''
 if heading:
  idx=lines.index(heading)
  if p=='FRC': school=lines[idx+1] if not lines[idx+1].startswith('From:') else ''
  if 'From:' in lines:location=lines[lines.index('From:')+1].replace('\xa0',' ')
  tag=f'{y} Sponsors:'
  if tag in lines:sponsors=lines[lines.index(tag)+1]
 other=sorted(set(int(x) for x in re.findall(r'(20\d\d): ',text)))
 facts={'program':p,'teamNumber':n,'season':y,'sourceUrl':u,'retrievedAt':NOW,'sourceSha256':hashlib.sha256(raw).hexdigest(),'sourceBytes':len(raw),'heading':heading,'registeredLocation':location,'schoolAffiliationHeadline':school,'sponsorsAndAffiliations':sponsors,'listedOtherSeasons':other,'screeningDistanceMiles':r.get('screeningDistanceMiles',r.get('screening_distance_miles')),'noEventsStatement':bool(re.search('has not yet participated at any official events',text)),'sourceIntroText':text[:min(text.find('Qualification Matches') if 'Qualification Matches' in text else 3000,3000)]}
 (BASE/f'{p.lower()}-{y}-{n}.json').write_text(json.dumps(facts,indent=2)+'\n');return facts
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:result=list(ex.map(fetch,latest.values()))
(BASE/'nearby-profiles.json').write_text(json.dumps(result,indent=2)+'\n')
for r in result:print(r['program'],r['teamNumber'],r['season'],r['registeredLocation'],'|',r['schoolAffiliationHeadline'],'|',r['sponsorsAndAffiliations'])
