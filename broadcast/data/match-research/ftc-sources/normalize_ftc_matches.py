#!/usr/bin/env python3
"""Derive close-score FTC selections from preserved public match payloads."""
import datetime,json,pathlib
P=pathlib.Path(__file__).resolve().parent
OUT=P.parent/'ftc-candidates.json'
NUMBERS=[22331,25638,14174,12802,19778,5501,30782,32552,36124]
NAMES={t['team_number']:t['team_name']for t in json.loads((P.parents[3]/'ftc/data/teams.json').read_text())['teams']}
NAMES[36124]='R.Amp'
events={json.loads(f.read_text())['code']:json.loads(f.read_text()) for f in P.glob('event-2025-*.json')if'-matches'not in f.name and'metadata'not in f.name}
raw_matches=[m for f in P.glob('event-2025-*-matches.json')for m in json.loads(f.read_text())]
def reasons(m,n):
 ts=[t for t in m['teams']if t['teamNumber']==n]
 r=[]
 if not m['hasBeenPlayed']:r.append('unplayed')
 if not m.get('scores'):r.append('missing scores')
 if not any(t.get('onField')and not t.get('noShow')for t in ts):r.append('target team off-field or no-show')
 if any(not t.get('onField')or t.get('noShow')for t in m['teams']):r.append('a participant off-field or no-show')
 if any(t.get('dq')for t in m['teams']):r.append('a participant disqualified')
 if events[m['eventCode']]['modifiedRules']:r.append('modified event rules')
 return r
def normalized(m,n):
 e=events[m['eventCode']];s=m['scores'];r=s['red']['totalPoints'];b=s['blue']['totalPoints'];alliance=next(t['alliance']for t in m['teams']if t['teamNumber']==n)
 playoff=m['tournamentLevel']!='Quals';number=m['series']if playoff else m['id']
 winner='Red'if r>b else 'Blue'if b>r else 'Tie'
 return {'key':f"2025-{m['eventCode']}-{m['id']}",'teamNumber':n,'program':'FTC','season':2025,'seasonLabel':'2025–26 DECODE','eventCode':m['eventCode'],'eventName':e['name'],'eventType':e['type'],'eventStartDate':e['start'],'eventEndDate':e['end'],'date':(m.get('actualStartTime')or e['end'])[:10],'playedAtUtc':m.get('actualStartTime'),'tournamentLevel':m['tournamentLevel'],'phase':'Playoff'if playoff else'Qualification','matchNumber':number,'sourceMatchId':m['id'],'matchLabel':f'Playoff Match {number}'if playoff else f'Qualification {number}','redTeams':[t['teamNumber']for t in m['teams']if t['alliance']=='Red'],'blueTeams':[t['teamNumber']for t in m['teams']if t['alliance']=='Blue'],'participation':[{'teamNumber':t['teamNumber'],'alliance':t['alliance'],'station':t['station'],'allianceRole':t['allianceRole'],'onField':t['onField'],'noShow':t['noShow'],'dq':t['dq'],'surrogate':t['surrogate']}for t in m['teams']],'redScore':r,'blueScore':b,'margin':abs(r-b),'teamAlliance':alliance,'teamScore':r if alliance=='Red'else b,'opponentScore':b if alliance=='Red'else r,'winningAlliance':winner,'outcome':'Tie'if winner=='Tie'else'Win'if winner==alliance else'Loss','officialResultUrl':f"https://ftc-events.firstinspires.org/2025/{m['eventCode']}/playoff/{number}/1"if playoff else f"https://ftc-events.firstinspires.org/2025/{m['eventCode']}/qualifications/{number}",'officialScheduleUrl':f"https://ftc-events.firstinspires.org/2025/{m['eventCode']}/"+('playoffs'if playoff else'qualifications'),'sourceUrl':f"https://api.ftcscout.org/rest/v1/events/2025/{m['eventCode']}/matches",'rawSourcePath':f"ftc-sources/event-2025-{m['eventCode']}-matches.json",'videoUrl':None}
teams=[]
for n in NUMBERS:
 population=[m for m in raw_matches if any(t['teamNumber']==n for t in m['teams'])]
 candidates=sorted([normalized(m,n)for m in population if not reasons(m,n)],key=lambda m:(m['margin'],0 if m['phase']=='Playoff'else 1,-int(m['date'].replace('-','')),-m['matchNumber'],m['key']))
 playoff=[m for m in candidates if m['phase']=='Playoff']
 selected=(candidates or[None])[0]
 teams.append({'teamNumber':n,'teamName':NAMES[n],'listedEventCodes':sorted({m['eventCode']for m in population}),'populationCount':len(population),'eligibleMatchCount':len(candidates),'eligiblePlayoffCount':len(playoff),'selected':selected,'closestPlayoff':playoff[0]if playoff else None,'closestOverall':candidates[0]if candidates else None,'closestOverallAlternates':[m for m in candidates if m['margin']==candidates[0]['margin']]if candidates else [],'selectionReason':'Closest final-score match across all eligible played matches; the closest playoff is supplied separately when available.'if candidates else'No 2025-season played match participation returned by FTCScout.','noPriorMatchSourceUrl':f'https://api.ftcscout.org/rest/v1/teams/{n}/'+('matches?season=2025'if n==36124 else'events/2025')if not candidates else None,'candidates':candidates,'excluded':[{'eventCode':m['eventCode'],'sourceMatchId':m['id'],'tournamentLevel':m['tournamentLevel'],'reasons':reasons(m,n),'match':normalized(m,n)if m.get('scores')else None}for m in population if reasons(m,n)]})
d={'program':'FTC','season':2025,'seasonLabel':'2025–26 DECODE','asOf':'2026-10-22','methodology':{'population':'Every match returned for the 2025-season event participations of the eight FTC research teams, plus the new 2026 R.Amp team checked for prior matches. The 2025 token means the 2025–26 DECODE game, including official Premier play in June 2026.','score':'Absolute difference of final alliance totalPoints including penalties, not an individual robot score. Wins, losses and ties are eligible.','eligibility':'Played, scored and all assigned participants actually on the field with no no-shows or disqualifications; no modified game rules. Incomplete lineups are excluded for a representative match even if the recorded final score is close.','selection':'Use the minimum absolute final score margin across all eligible played matches and preserve the closest playoff separately. Equal minimum margins prefer playoff phase, then later played date and later match number; video availability may break an exact tie later.','rivalry':'One close opposing alliance is a representative matchup; this evidence does not establish a recurring named rivalry.','video':'No verified individual-match video in this file; use the exact FIRST result link unless a separately verified video becomes available.'},'teams':teams}
OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
print(OUT)
for t in teams:
 s=t['selected'];print(t['teamNumber'],s and(s['eventName'],s['matchLabel'],s['teamScore'],s['opponentScore'],s['margin']),t['eligibleMatchCount'])
