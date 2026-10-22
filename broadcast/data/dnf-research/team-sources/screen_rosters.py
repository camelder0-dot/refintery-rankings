import requests,bs4,json,pathlib,gzip,hashlib,datetime,concurrent.futures,zipfile,io,csv,math,re
BASE=pathlib.Path(__file__).parent
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
def fetch(y):
 u=f'https://frc-events.firstinspires.org/{y}/allteams'; cached=BASE/f'frc-allteams-{y}.json'
 if cached.exists():return json.loads(cached.read_text())
 p=BASE/f'frc-allteams-{y}.html'; raw=p.read_bytes() if p.exists() else requests.get(u,timeout=90).content
 s=bs4.BeautifulSoup(raw,'html.parser'); rows=[]
 for a in s.select('#teamList > a'):
  d=[x.get_text(' ',strip=True) for x in a.select(':scope > div > div')];
  if len(d)>=5:rows.append({'number':int(d[1]),'name':d[2],'district':d[3],'location':d[4]})
 # retain factual extract, source hash, rather than page's megabytes of embedded avatar artwork
 r={'season':y,'url':u,'retrievedAt':NOW,'sourceSha256':hashlib.sha256(raw).hexdigest(),'sourceBytes':len(raw),'teams':rows};(BASE/f'frc-allteams-{y}.json').write_text(json.dumps(r,indent=2)+'\n')
 if p.exists():p.unlink()
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: rosters=list(ex.map(fetch,[2023,2024,2025,2026,2027]))
u='https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_place_national.zip'; raw=requests.get(u,timeout=90).content; z=zipfile.ZipFile(io.BytesIO(raw));rr=csv.DictReader(io.StringIO(z.read(z.namelist()[0]).decode()),delimiter='|');places={}
for r in rr:
 r={k.strip():v.strip() for k,v in r.items()}
 if r['USPS'] not in ['IN','OH','MI']:continue
 name=re.sub(r' (city|town|village|CDP)$','',r['NAME'])
 places[(name.lower(),r['USPS'])]=r
lat0,lon0=41.079467666017,-85.137939575106
def dist(la,lo):
 a,b=map(math.radians,[lat0,la]); dl=math.radians(lo-lon0); return 3958.7613*2*math.asin(math.sqrt(math.sin((b-a)/2)**2+math.cos(a)*math.cos(b)*math.sin(dl/2)**2))
near=[];unmatched=[]
for roster in rosters:
 for r in roster['teams']:
  st={'Indiana':'IN','Michigan':'MI','Ohio':'OH'};p=r['location'].split(', ')
  if len(p)<3 or p[-2] not in st:continue
  place=places.get((p[0].lower(),st[p[-2]]))
  if not place:unmatched.append({**r,'season':roster['season']});continue
  d=dist(float(place['INTPTLAT']),float(place['INTPTLONG']))
  if d<=75:near.append({**r,'season':roster['season'],'city':p[0],'state':st[p[-2]],'screeningDistanceMiles':d,'place':place,'sourceUrl':roster['url']})
result={'retrievedAt':NOW,'rosters':[{k:v for k,v in r.items() if k!='teams'} for r in rosters],'gazetteerUrl':u,'gazetteerSha256':hashlib.sha256(raw).hexdigest(),'radiusBufferMiles':75,'nearby':near,'unmatched':unmatched};(BASE/'frc-nearby-screen.json').write_text(json.dumps(result,indent=2)+'\n')
for r in near:print(r['season'],r['number'],r['name'],r['location'],round(r['screeningDistanceMiles'],1))
print('UNMATCHED',unmatched)
