import json,pathlib,re,difflib
P=pathlib.Path(__file__).resolve().parent.parent
universe=json.loads((P/'school-universe.json').read_text())['schools']
base=json.loads((P/'leaders-indiana-directory.json').read_text())['records']
esc=json.loads((P/'leaders-ohio-esc.json').read_text())['records']
coras=json.loads((P/'leaders-ohio-coras.json').read_text())['records'] if (P/'leaders-ohio-coras.json').exists() else []
verified=json.loads((P/'leaders-verified.json').read_text())['records']
def norm(n):
 n=re.sub(r'\b(community|school|schools|corporation|corp|sch|schls|district|schl|exempted|village|com|co|county|area|city)\b','',n.lower());n=re.sub('[^a-z0-9]','',n)
 n=n.replace('careerctr','careercenter')
 return n
records=[]
for leaId in sorted({s.get('leaId') for s in universe if s['sector']=='public' and s.get('leaId')}):
 schools=[s for s in universe if s.get('leaId')==leaId];d=schools[0]['district'];state=schools[0]['state'];picks=[]
 for group in [base,coras,esc,verified]:
  matches=[r for r in group if r['state']==state and (r.get('leaId')==leaId or norm(r['districtName'])==norm(d))]
  if not matches:
   matches=[r for r in group if r['state']==state and difflib.SequenceMatcher(a=norm(r['districtName']),b=norm(d)).ratio()>.91]
  if matches:picks.append(matches[-1])
 if picks:r={**picks[-1],'leaId':leaId,'districtName':d,'schoolNames':[s['name'] for s in schools]}
 else:r={'leaId':leaId,'districtName':d,'state':state,'name':None,'role':None,'sourceUrl':None,'sourceLabel':None,'verifiedCurrent':False,'evidence':'Leader not verified in available official sources','schoolNames':[s['name'] for s in schools]}
 records.append(r)
schoolRecords=[r for r in verified if r.get('schoolId')]
(P/'leaders.json').write_text(json.dumps({'asOf':'2026-10-22','description':'Public district and charter leaders joined to the current school universe. Current official district/ESC evidence overrides the dated Indiana 2025–26 directory; role labels preserve interim and school-leader titles. Null names mean not verified. Website retrieval is not an assurance of a 2026–27 appointment unless stated in the evidence.','records':records,'schoolRecords':schoolRecords},indent=2)+'\n')
for r in records:
 if not r['name'] or not r['verifiedCurrent']: print('NEEDS CURRENT',r['state'],r['leaId'],r['districtName'],r['name'])
print('Total',len(records),'named',sum(bool(r['name']) for r in records),'current',sum(r['verifiedCurrent'] for r in records))
