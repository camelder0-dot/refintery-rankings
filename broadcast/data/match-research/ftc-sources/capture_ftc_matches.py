#!/usr/bin/env python3
"""Capture FTCScout match population; primary result pages verify selected matches."""
import datetime,hashlib,json,pathlib,time,urllib.request
OUT=pathlib.Path(__file__).resolve().parent
NUMBERS=[22331,25638,14174,12802,19778,5501,30782,32552]
BASE='https://api.ftcscout.org/rest/v1'
def capture(name,url):
 path=OUT/name
 if path.exists():return json.loads(path.read_text())
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=35) as r:raw=r.read();status=r.status
 path.write_bytes(raw)
 (OUT/(name+'.metadata.json')).write_text(json.dumps({'source':'FTCScout public REST API','url':url,'capturedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'httpStatus':status,'sha256':hashlib.sha256(raw).hexdigest()},indent=2)+'\n')
 print(name,len(raw),flush=True)
 time.sleep(.2)
 return json.loads(raw)
def main():
 events=set()
 for n in NUMBERS:
  es=capture(f'team-{n}-events-2025.json',f'{BASE}/teams/{n}/events/2025')
  events|={e['eventCode'] for e in es}
 for e in sorted(events):
  capture(f'event-2025-{e}.json',f'{BASE}/events/2025/{e}')
  capture(f'event-2025-{e}-matches.json',f'{BASE}/events/2025/{e}/matches')
 capture('team-36124-matches-2025.json',f'{BASE}/teams/36124/matches?season=2025')
if __name__=='__main__':main()
