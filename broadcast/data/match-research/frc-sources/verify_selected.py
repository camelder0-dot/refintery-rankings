#!/usr/bin/env python3
"""Cross-check preserved selected FRC matches against official detail scorecards."""
import concurrent.futures,datetime as dt,hashlib,json,urllib.request,re
from pathlib import Path
from bs4 import BeautifulSoup
HERE=Path(__file__).resolve().parent
DATA=HERE.parent/'frc-candidates.json'

def txt(n): return n.get_text(' ',strip=True)
def verify(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Refintery-Rankings-Public-Research/1.0'})
    with urllib.request.urlopen(req,timeout=30) as response:
        raw=response.read()
    s=BeautifulSoup(raw,'html.parser')
    extracted={}
    for tr in s.select('table tr'):
        cells=tr.find_all('td',recursive=False)
        if len(cells)==3:
            k=txt(cells[0])
            if k in ('Teams','Final Score','Penalties','Fouls Committed','Foul Points'):
                if k=='Teams': extracted[k]={'blue':list(map(int,re.findall(r'\d+',txt(cells[1])))),'red':list(map(int,re.findall(r'\d+',txt(cells[2]))))}
                else: extracted[k]={'blue':txt(cells[1]),'red':txt(cells[2])}
    return {'url':url,'fetchedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'htmlSha256':hashlib.sha256(raw).hexdigest(),'officialTitle':txt(s.select_one('h1')),'scorecard':extracted,'videoUrlsFound':[a['href'] for a in s.select('a[href]') if any(x in a['href'] for x in ('youtu','twitch','vimeo'))]}

if __name__=='__main__':
    data=json.loads(DATA.read_text()); urls=sorted({r[field]['matchUrl'] for r in data['records'] for field in ('selected','absoluteClosest') if r[field]})
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: details=list(pool.map(verify,urls))
    byurl={x['url']:x for x in details}
    for r in data['records']:
      for field in ('selected','absoluteClosest'):
        x=r[field]; d=byurl[x['matchUrl']]; v=d['scorecard']
        assert x['redScore']==int(v['Final Score']['red']),x
        assert x['blueScore']==int(v['Final Score']['blue']),x
        assert x['redTeams']==v['Teams']['red'],x
        assert x['blueTeams']==v['Teams']['blue'],x
        assert v['Penalties']=={'blue':'None','red':'None'},v
        x['verification']={'officialMatchDetailConfirmed':True,'penalties':v['Penalties'],'detailSourceUrl':d['url']}
        x['partnerTeams']=[t for t in x[x['teamAlliance']+'Teams'] if t!=x['team']]
        x['opponentTeams']=x['blueTeams' if x['teamAlliance']=='red' else 'redTeams']
        x['selectionReason']=('Closest played score in the 2026 official season' if field=='absoluteClosest' else 'Closest played playoff score in the 2026 official season' if x['phase']=='playoff' else 'Closest played qualification score; no 2026 playoff appearance listed')
    (HERE.parent/'frc-match-scorecards.json').write_text(json.dumps({'year':2026,'sources':details},indent=2,ensure_ascii=False)+'\n')
    data['policy']['verification']='All published main selections and playoff alternatives agree with official FIRST scorecards for final scores, all six assigned robots and disqualification status. Replay evidence is joined separately by exact official result URL.'
    (HERE.parent/'frc-verified.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    for r in data['records']:
        x=r['selected'];print(r['team'],x['eventCode'],x['matchLabel'],x['redScore'],x['blueScore'],x['teamResult'],x['partnerTeams'],x['opponentTeams'])
