#!/usr/bin/env python3
"""Independently corroborate selected matches against FIRST's result pages."""
import datetime,hashlib,html,json,pathlib,re,urllib.request
P=pathlib.Path(__file__).resolve().parent
research=json.loads((P.parent/'ftc-candidates.json').read_text())
seen=set();records=[]
for team in research['teams']:
 for field in ['selected','closestPlayoff']:
  m=team[field]
  if not m or m['key']in seen:continue
  seen.add(m['key']);url=m['officialResultUrl']
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=35)as r:raw=r.read();status=r.status
  text=raw.decode('utf-8')
  title=' '.join(html.unescape(re.search(r'<title>(.*?)</title>',text,re.S)[1]).split())
  red=int(re.search(r'deep-scoreboard-totalpoints-red">\s*(\d+)',text)[1])
  blue=int(re.search(r'deep-scoreboard-totalpoints-blue">\s*(\d+)',text)[1])
  teams={key:int(re.search(r'var '+key+r' = (\d+);',text)[1])for key in['red1','red2','blue1','blue2']}
  assert red==m['redScore']and blue==m['blueScore'],(m['key'],red,blue)
  assert sorted([teams['red1'],teams['red2']])==sorted(m['redTeams'])
  assert sorted([teams['blue1'],teams['blue2']])==sorted(m['blueTeams'])
  records.append({'key':m['key'],'sourceUrl':url,'httpStatus':status,'retrievedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'responseSha256':hashlib.sha256(raw).hexdigest(),'pageTitle':title,'redScore':red,'blueScore':blue,'teams':teams,'matchesFtcScoutPayload':True})
  print('Verified',m['key'],red,blue,flush=True)
(P.parent/'ftc-first-verification.json').write_text(json.dumps({'source':'FIRST Tech Challenge Event Web','scope':'Selected closest overall matches and separately offered closest playoff alternatives. All displayed final alliance scores and all four robot assignments agree with FTCScout.','records':records},indent=2)+'\n')
