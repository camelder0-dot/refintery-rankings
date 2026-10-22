#!/usr/bin/env python3
"""Freeze current Indiana directory grade9+ unmatched campus records and Census geocodes.
Re-run only with network to refresh snapshots. No currentsource overwrites universe.
"""
import json,openpyxl,re,pathlib,urllib.request,urllib.parse,concurrent.futures
HERE=pathlib.Path(__file__).parent
w=openpyxl.load_workbook(HERE/'leader-sources/indiana-school-directory-2025-26.xlsx',read_only=True,data_only=True)
u=json.loads((HERE/'school-universe.json').read_text());counties={re.sub('[^a-z]','',s['county'].replace(' County','').lower()) for s in u['screenedSchools'] if s['state']=='IN' and s['withinRadius']}
known_ids={x['ncesId'] for x in u['screenedSchools']}
def norm(s):return re.sub('[^a-z0-9]','',str(s).lower())
aliases={'A170':'A0792095','A275':'A1701689','A944':'A9701438','B015':'00424857','B136':'A9701532','D914':'A2101740'}
corps=list(w['CORP'].values);corps=[dict(zip(corps[0],r)) for r in corps[1:]];corpmap={r['IDOE_CORPORATION_ID']:r for r in corps}
records=[]
for sheet in ['SCHL','NPSCHL']:
 rows=list(w[sheet].values);rows=[dict(zip(rows[0],r)) for r in rows[1:]]
 for r in rows:
  if not(str(r.get('HIGH_GRADE','')).isdigit() and int(r['HIGH_GRADE'])>=9 and re.sub('[^a-z]','',r['COUNTY_NAME'].lower()) in counties):continue
  if sheet=='SCHL':match=next((s for s in u['screenedSchools'] if s['ncesId']==str(r['NCES_ID'])),None)
  else:match=next((s for s in u['screenedSchools'] if norm(s['name'])==norm(r['SCHOOL_NAME']) and norm(s['city'])==norm(r['CITY'])),None)
  alias=aliases.get(r['IDOE_SCHOOL_ID'])
  if alias:match=next(s for s in u['screenedSchools'] if s['ncesId']==alias)
  # Retain only needed currentaliases/updates plus missing/new schools.
  if match:
   if match['withinRadius']:
    records.append({'stateSchoolId':r['IDOE_SCHOOL_ID'],'matchedNcesId':match['ncesId'],'directory':{k:v for k,v in r.items() if 'EMAIL' not in k and 'PRINCIPAL' not in k},'corporation':{k:v for k,v in corpmap.get(r.get('IDOE_CORPORATION_ID'),{}).items() if 'EMAIL' not in k and 'SUPERINTENDENT' not in k},'requiresNewRecord':False})
   continue
  r={k:v for k,v in r.items() if 'EMAIL' not in k and 'PRINCIPAL' not in k}
  address=r['ADDRESS']
  if r['IDOE_SCHOOL_ID']=='A236':address='3501 Harris Road';r['ADDRESS']=address
  records.append({'stateSchoolId':r['IDOE_SCHOOL_ID'],'matchedNcesId':None,'directory':r,'corporation':{k:v for k,v in corpmap.get(r.get('IDOE_CORPORATION_ID'),{}).items() if 'EMAIL' not in k and 'SUPERINTENDENT' not in k},'requiresNewRecord':True})
def geocode(rec):
 if not rec['requiresNewRecord']:return rec
 r=rec['directory'];addr=f"{r['ADDRESS']}, {r['CITY']}, {r['STATE']} {r['ZIP']}"
 url='https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?'+urllib.parse.urlencode({'address':addr,'benchmark':'Public_AR_Current','format':'json'})
 try:
  data=json.load(urllib.request.urlopen(url,timeout=40));rec['geocoder']={'sourceUrl':url,'response':data};print(r['SCHOOL_NAME'],[(m['matchedAddress'],m['coordinates']) for m in data['result']['addressMatches']],flush=True)
 except Exception as e:rec['geocoder']={'sourceUrl':url,'error':str(e)};print(r['SCHOOL_NAME'],str(e),flush=True)
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:records=list(pool.map(geocode,records))
result={'researchDate':'2026-10-22','sourceUrl':'https://www.in.gov/doe/files/2025-2026-school-directory-2026-03-23.xlsx','sourceLanding':'https://www.in.gov/doe/it/data-center-and-reports/','sourceLabel':'2025–26 Indiana directory, landingpageUpdatedApril1 2026','selection':'Indiana schools with HIGH_GRADE>=9 in anycounty intersecting radius. MatchedNCESrecordsinside60retained for aliases andcurrentgrades; unmatchedrecordsgeocoded forscreening. Pendleton records retainedasoutside-radius evidence.','aliases':aliases,'addressCorrections':[{'stateSchoolId':'A236','address':'3501 Harris Road, Fort Wayne, IN46808','sourceUrl':'https://www.cornerstonecollegeprep.org/','reason':'Officialschoolphysicalcontact replacesdirectoryPOBox'}],'records':records}
(HERE/'school-universe-indiana-supplement.json').write_text(json.dumps(result,indent=2)+'\n')
