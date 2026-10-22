#!/usr/bin/env python3
"""Join frozen official NCES EDGE/CCD/PSS snapshots and screen a 60 mile circle.
Raw files live alongside this script. PSS CSV was fetched from the sourceUrl
recorded in its raw subset and joined by PPIN; grade labels from official SAS formats.
"""
import json, math, pathlib, collections
HERE=pathlib.Path(__file__).parent
ORIGIN=json.loads((HERE.parents[2]/'data/geography.json').read_text())['origin']
R=3958.7613

def load(name): return json.loads((HERE/name).read_text())
def distance(lat,lon):
    a,b=ORIGIN['coordinates']['latitude'],ORIGIN['coordinates']['longitude']
    k=math.sin(math.radians(lat-a)/2)**2+math.cos(math.radians(a))*math.cos(math.radians(lat))*math.sin(math.radians(lon-b)/2)**2
    return R*2*math.atan2(math.sqrt(k),math.sqrt(1-k))
def pss_grade(value):
    return {'1':'UG','2':'PK','3':'KG','4':'TK','5':'T1'}.get(value,str(int(value)-5) if value else None)
def public_grade(value):
    return str(int(value)) if value.isdigit() else value

def build():
    pubraw=load('school-universe-raw-public-geocodes.json');priraw=load('school-universe-raw-private-geocodes.json');ccd=load('school-universe-raw-public-characteristics.json');pss=load('school-universe-raw-private-characteristics.json')
    pubchar={}
    for f in ccd['response']['features']:
        x={k.rsplit('.',1)[-1]:v for k,v in f['attributes'].items()};pubchar[x['NCESSCH']]=x
    prichar={x['PPIN']:x for x in pss['records']}
    records=[]
    for sector,raw,chars,idfield in [('public',pubraw,pubchar,'NCESSCH'),('private',priraw,prichar,'PPIN')]:
        for feature in raw['response']['features']:
            g=feature['attributes'];c=chars.get(g[idfield]);d=distance(g['LAT'],g['LON'])
            if sector=='public':
                low=public_grade(c['GSLO']) if c else None;high=public_grade(c['GSHI']) if c else None;typ=c['SCHOOL_TYPE_TEXT'] if c else None
                status=c['SY_STATUS_TEXT'] if c else None;virtual=c['VIRTUAL'] if c else None;charter=c['CHARTER_TEXT']=='Yes' if c else None
                district=c['LEA_Name'] if c else None;stId=c['ST_SCHID'] if c else None
                source='https://nces.ed.gov/ccd/schoolsearch/school_detail.asp?ID='+g[idfield]
            else:
                low=pss_grade(c['LOGR2024']) if c else None;high=pss_grade(c['HIGR2024']) if c else None
                typ={'1':'Regular','2':'Montessori','3':'Special Program Emphasis','4':'Special Education','5':'Career/Technical/Vocational','6':'Alternative/Other','7':'Early Childhood'}.get(c['P415']) if c else None
                status='Reported in 2023–24 PSS';virtual=None;charter=False;district=None;stId=None
                source='https://nces.ed.gov/surveys/pss/privateschoolsearch/school_detail.asp?ID='+g[idfield]
            highschool=bool(high and high.isdigit() and int(high)>=9)
            cls='ordinary-campus'
            if not c: cls='characteristics-missing-review'
            elif not highschool: cls='below-grade-9'
            elif status in ['Closed','Inactive','Future','Temporarily Closed']: cls='inactive-review'
            elif virtual in ['Full Virtual','Virtual with face to face options']: cls='virtual-review'
            elif typ and ('Vocational' in typ or 'Career/' in typ or 'Career and Technical' in typ): cls='career-technical-review'
            elif typ and ('Alternative' in typ or 'Special Education' in typ): cls='alternative-special-review'
            if d>60: cls='outside-radius'
            record={'ncesId':g[idfield],'leaId':g.get('LEAID'),'stateSchoolId':stId,'name':g['NAME'],'sector':sector,'district':district,'state':g['STATE'],'city':g['CITY'],'address':g['STREET'],'zip':g['ZIP'],'county':g['NMCNTY'],'latitude':g['LAT'],'longitude':g['LON'],'distanceMiles':round(d,6),'withinRadius':d<=60,'gradesLow':low,'gradesHigh':high,'highSchoolGrades':highschool,'schoolType':typ,'charter':charter,'virtual':virtual,'status':status,'scopeClass':cls,'geocodeYear':g['SCHOOLYEAR'],'characteristicsYear':c.get('SURVYEAR') if sector=='public' and c else ('2023–24' if c else None),'sourceUrls':[source,raw['sourceUrl'].split('/query?')[0],ccd['sourceUrl'].split('/query?')[0] if sector=='public' else pss['sourceUrl']]}
            if record['name'].startswith('Excel Center -') and record['highSchoolGrades']:
                record['scopeClass']='adult-only-excluded';record['scopeNote']='Officialoperator describes these campuses as adult high schools, outside youth-school invitation scope.';record['sourceUrls'].append('https://excelcenter.org/locations/')
            record['id']=record['ncesId']
            records.append(record)
    # Update lagged NCES with official current Indiana directory, keeping frozen raw rows above.
    sup=load('school-universe-indiana-supplement.json')
    for row in sup['records']:
        r=row['directory'];glo=public_grade(str(r['LOW_GRADE']));ghi=public_grade(str(r['HIGH_GRADE']))
        if not row['requiresNewRecord']:
            rec=next(x for x in records if x['ncesId']==row['matchedNcesId'])
            rec['ncesName']=rec['name'];rec['name']=r['SCHOOL_NAME'];rec['stateSchoolId']=r['IDOE_SCHOOL_ID'];rec['gradesLow']=glo;rec['gradesHigh']=ghi;rec['characteristicsYear']='2025–26 Indiana directory';rec['sourceUrls'].append(sup['sourceUrl'])
            rec['schoolUrl']=r.get('SCHOOL_HOMEPAGE')
            if row.get('matchNote'):rec['scopeNote']=row['matchNote'];rec['sourceUrls']+=row['additionalSources'];rec['address']=r['ADDRESS']
            continue
        geo=row.get('geocoder',{});matches=geo.get('response',{}).get('result',{}).get('addressMatches',[])
        point=matches[0]['coordinates'] if matches else None
        miles=distance(point['y'],point['x']) if point else None
        public=bool(r.get('IDOE_CORPORATION_ID'));corp=row.get('corporation',{})
        cls='ordinary-campus'
        if any(k in r['SCHOOL_NAME'] for k in ['Youth Services','Juvenile','Justice Center','Spec Ed','Area Prog','North Central Indiana Academy','Crossroad','Alternative']):cls='alternative-special-review'
        if 'Online' in r['SCHOOL_NAME']:cls='virtual-review'
        if r['IDOE_SCHOOL_ID']=='A178':cls='grade-conflict-review'
        if point is None:cls='geocode-missing-review'
        elif miles>60:cls='outside-radius'
        sources=[sup['sourceUrl']]
        if r.get('SCHOOL_HOMEPAGE') and r['SCHOOL_HOMEPAGE'].strip():sources.append(r['SCHOOL_HOMEPAGE'].strip().replace('http://','https://'))
        if geo.get('sourceUrl'):sources.append(geo['sourceUrl'])
        if r['IDOE_SCHOOL_ID']=='A178':sources.append('https://www.in.gov/sboe/files/St.-Gregory-the-Great-Academy-Recommendation-for-Accreditation.pdf')
        rec={'id':'IN-'+r['IDOE_SCHOOL_ID'],'ncesId':r.get('NCES_ID'),'leaId':corp.get('NCES_ID'),'stateSchoolId':r['IDOE_SCHOOL_ID'],'name':r['SCHOOL_NAME'],'sector':'public' if public else 'private','district':r.get('CORPORATION_NAME'),'state':r['STATE'],'city':r['CITY'],'address':r['ADDRESS'],'zip':r['ZIP'],'county':r['COUNTY_NAME']+' County','latitude':point['y'] if point else None,'longitude':point['x'] if point else None,'distanceMiles':round(miles,6) if miles is not None else None,'withinRadius':miles is not None and miles<=60,'gradesLow':glo,'gradesHigh':ghi,'highSchoolGrades':int(ghi)>=9,'schoolType':'Alternative/Special Education' if cls=='alternative-special-review' else ('Regular School' if cls!='grade-conflict-review' else 'Grade conflict'),'charter':corp.get('CORPORATION_TYPE')=='Charter','virtual':None,'status':'Listed in 2025–26 Indiana directory','scopeClass':cls,'geocodeYear':'Census current observed2026-10-22','characteristicsYear':'2025–26 Indiana directory','sourceUrls':sources,'schoolUrl':r.get('SCHOOL_HOMEPAGE')}
        if r['IDOE_SCHOOL_ID']=='A178':rec['scopeNote']='Directory says K–12, but April2025 accreditationpetition says initialK–4 and gradualyearly expansion. Currenthighschoolgrades notverified; withholdfrominvitationcount.'
        if row.get('geocodeNote'):rec['scopeNote']=row['geocodeNote']
        records.append(rec)
    for r in load('school-universe-manual-review.json')['records']:
        point=r.get('geocoder',{}).get('response',{}).get('result',{}).get('addressMatches',[])
        lat=r.get('latitude',point[0]['coordinates']['y'] if point else None);lon=r.get('longitude',point[0]['coordinates']['x'] if point else None);miles=distance(lat,lon)
        sources=r['sources']+[r.get('geocodeSource',r.get('geocoder',{}).get('sourceUrl'))]
        rec={'id':r['id'],'ncesId':None,'leaId':None,'stateSchoolId':None,'name':r['name'],'sector':r['sector'],'district':None,'state':r['state'],'city':r['city'],'address':r['address'],'zip':r['zip'],'county':r['county'],'latitude':lat,'longitude':lon,'distanceMiles':round(miles,6),'withinRadius':miles<=60,'gradesLow':r['gradesLow'],'gradesHigh':r['gradesHigh'],'highSchoolGrades':True,'schoolType':r['schoolType'],'charter':False,'virtual':'Not Virtual','status':'Current official school site','scopeClass':('outside-radius' if miles>60 else ('alternative-special-review' if 'Alternative' in r['schoolType'] else 'ordinary-campus')),'geocodeYear':'Censuscurrent2026-10-22','characteristicsYear':'Currentsite2026-10-22','sourceUrls':sources,'schoolUrl':r['sources'][0],'scopeNote':r['note']}
        records.append(rec)
    # PSS returned three IDs for the exact same special-school campus. Keep one card,
    # all IDs and raw records, and explicitly mark the two superseded aliases.
    road=[x for x in records if x['ncesId'] in ['A1702905','A1903506','A2302063']]
    canonical=next(x for x in road if x['ncesId']=='A2302063');canonical['allNcesIds']=[x['ncesId'] for x in road];canonical['scopeNote']='Onecampus returned underthreePSSIDs atsameaddress; canonicalcardretainsthreeIDs.'
    for r in road:
        if r is not canonical:r['scopeClass']='duplicate-campus-excluded';r['duplicateOf']=canonical['id']
    crossroad=next(x for x in records if x['id']=='A1701689')
    crossroad['allStateSchoolIds']=['A275','D928'];crossroad['scopeNote']='One Crossroad Academy campus serves both day students and residential treatment students. Combined campus card retains separate state program identifiers.';crossroad['sourceUrls'].append('https://crossroadcares.org/how-we-help/crossroad-academy-alternative-education/')
    prtf=next(x for x in records if x['id']=='IN-D928');prtf['scopeClass']='duplicate-campus-excluded';prtf['duplicateOf']='A1701689'
    ohio=load('school-universe-ohio-ncnp-2026-27.json')
    for update in ohio['confirmedUpdates']:
        rec=next(x for x in records if x['ncesId']==update['ncesId'])
        rec['gradesLow']=update['gradesLow'];rec['gradesHigh']=update['gradesHigh'];rec['highSchoolGrades']=True;rec['scopeClass']='ordinary-campus';rec['schoolUrl']=update['schoolUrl'];rec['sourceUrls']+=[update['sourceUrl'],ohio['sourceUrl']];rec['characteristicsYear']='Current official school site +2026–27 Ohio NCNP filing';rec['scopeNote']='Older PSS reported grades through8; current official school site explicitly offers high school. Grade update is based on the school site, not the state instructional-hour category.'
    for name,id in ohio['possibleReviewIds'].items():
        row=next(r for r in ohio['targetCountyScreen'] if r['name']==name);point=row['geocoder']['response']['result']['addressMatches'][0]['coordinates']
        rec={'id':id,'ncesId':None,'leaId':None,'stateSchoolId':None,'name':name,'sector':'private','district':None,'state':'OH','city':row['address'].split(',')[1].strip(),'address':row['address'].split(',')[0],'zip':row['address'][-5:],'county':row['county']+' County','latitude':point['y'],'longitude':point['x'],'distanceMiles':round(row['distanceMiles'],6),'withinRadius':row['distanceMiles']<=60,'gradesLow':None,'gradesHigh':None,'gradesLabel':'State instructional-hour category7–12; actual grades unverified','highSchoolGrades':None,'schoolType':'Nonchartered Nonpublic School','charter':False,'virtual':None,'status':'Listed in2026–27 Ohio NCNP filing','scopeClass':'grade-range-review','geocodeYear':'Census current observed2026-10-22','characteristicsYear':'2026–27 Ohio NCNP filing','sourceUrls':[ohio['sourceUrl'],ohio['certificationFormSource'],row['geocoder']['sourceUrl']],'schoolUrl':None,'scopeNote':'The filing lists the Grades7–12/1001hours category. That could mean only grades7–8; actual highschool offering is not verified. Hold outside DNF candidates until clarified.','schoolContact':row['schoolContact'],'schoolContactRole':'School Contact'}
        records.append(rec)
    mi=load('school-universe-michigan-current-audit.json');lake=next(x for x in records if x['ncesId']=='A9303515');lake['sourceUrls'].append(mi['sourceUrl']);lake['stateAgreementId']='750304703';lake['status']='Listed in Michigan May2026 final approved nonpublic school directory'
    candidates=[x for x in records if x['withinRadius'] and x['highSchoolGrades'] and x['scopeClass'] not in ['duplicate-campus-excluded','adult-only-excluded','virtual-review','grade-conflict-review','grade-range-review']]


    result={'schemaVersion':'1.0','researchDate':'2026-10-22','origin':ORIGIN,'radiusMiles':60,'method':'Join NCES EDGE public2024–25 and private2023–24 school geocodes to CCD2024–25/PSS2023–24 characteristics by institutional ID; choose any offered grade9–12, not school title; haversine distance <=60 on unrounded double using Earth radius3958.7613mi. Bounding envelope -86.5,40.0,-83.8,42.1 fully contains the circle.','scopeNotes':['Universe includes public district schools, public charters, ordinary private schools, and alternative/special/career/virtual records for review. No school has yet been assigned a team-presence status here.','Ordinary-campus records can enter the school invitation list after team screen and leadercheck. Review classes need editorial decision before publishing. Virtual administrative addresses do not establish a local physical student campus.','The CCD school map characteristics records current2024–25 status are Open/New; NCES is lagged and does not establish2026–27 operating status. Current state directory/site review is required for closures/renames and new openings.','Private PSS is a survey universe; nonresponding/unlisted/new private schools can be absent. PSS2023–24 can include duplicate legacy IDs for a single campus; duplicate candidates are separately flagged.','Any school offering grades9–12 is included; this does not require all four grades. Ungraded special schools require individual review and are not silently classified as high schools.','Distance uses school location rather than school district centroid. Names/addresses are as reported to NCES, with current corrections recorded separately.'], 'sources':[{'url':'https://nces.ed.gov/programs/edge/Geographic/SchoolLocations','purpose':'EDGE geocode methodology and years'},{'url':'https://nces.ed.gov/surveys/pss/pssdata.asp','purpose':'PSS public-use data'},{'url':'https://nces.ed.gov/surveys/pss/zip/pss2324_pu_sas.zip','purpose':'Official LOGR2024/HIGR2024/P415 value labels. Grade9code14 to Grade12code17.'}], 'counts':{'screened':len(records),'publicScreened':len(pubraw['response']['features']),'privateScreened':len(priraw['response']['features']),'withinRadius':sum(x['withinRadius'] for x in records),'candidates':len(candidates),'candidateByState':dict(collections.Counter(x['state'] for x in candidates)),'candidateByClass':dict(collections.Counter(x['scopeClass'] for x in candidates)), 'reviewCandidates':sum(x['withinRadius'] and (x['highSchoolGrades'] or x['scopeClass']=='grade-range-review') and x['scopeClass'] in ['virtual-review','grade-conflict-review','adult-only-excluded','duplicate-campus-excluded','grade-range-review'] for x in records)},'reviewSchools':[x for x in records if x['withinRadius'] and (x['highSchoolGrades'] or x['scopeClass']=='grade-range-review') and x['scopeClass'] in ['virtual-review','grade-conflict-review','adult-only-excluded','duplicate-campus-excluded','grade-range-review']], 'schools':sorted(candidates,key=lambda x:(x['state'],x['name'])),'screenedSchools':sorted(records,key=lambda x:(x['state'],x['name']))}
    (HERE/'school-universe.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['counts'])
    for x in result['schools']:print(x['ncesId'],x['leaId'],x['name'],x['district'],x['city'],x['state'],x['gradesLow']+'–'+x['gradesHigh'],x['scopeClass'],round(x['distanceMiles'],2),sep=' | ')

if __name__=='__main__':build()
