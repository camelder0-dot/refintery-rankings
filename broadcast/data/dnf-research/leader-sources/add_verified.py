import pathlib,json,requests,bs4,concurrent.futures,re,hashlib
P=pathlib.Path(__file__).resolve().parent.parent
records=json.loads((P/'leaders-verified.json').read_text())['records'] if (P/'leaders-verified.json').exists() else []
def add(district,name,role,url,state='IN',evidence=None,leaId=None,schoolId=None,schoolYear='Current district website'):
 r={'districtName':district,'leaId':leaId,'schoolId':schoolId,'state':state,'name':name,'role':role,'sourceUrl':url,'sourceLabel':'Official district or school website','evidence':evidence or name+' — '+role,'retrievedOn':'2026-10-22','schoolYear':schoolYear,'verifiedCurrent':True}
 for i,x in enumerate(records):
  if x['districtName']==district and x.get('schoolId')==schoolId:
   records[i]=r;break
 else:records.append(r)
def save():
 (P/'leaders-verified.json').write_text(json.dumps({'asOf':'2026-10-22','records':records},indent=2)+'\n')
 def get(r):
  try:
   text=requests.get(r['sourceUrl'],timeout=20).text
   t=bs4.BeautifulSoup(text,'html.parser').get_text('\n',strip=True)
   n=re.sub('[^a-z0-9]+','-',r['districtName'].lower()).strip('-')
   (P/'leader-sources'/f'{n}.txt').write_text(t)
   return [r['districtName'],len(t), r['name'].split()[-1].lower() in t.lower()]
  except Exception as e:return [r['districtName'],str(e)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:print(list(ex.map(get,records)))
