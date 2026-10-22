import json,requests,concurrent.futures,bs4,pathlib,urllib.parse,re
P=pathlib.Path(__file__).resolve().parent.parent
rows=json.loads((P/'leaders-indiana-directory.json').read_text())['records']
S=requests.Session()
def fetch(r):
 url=r['website']
 if not url or not url.strip():return {**r,'currentCheck':'No district homepage in directory'}
 url=url.replace('http:','https:')
 try:
  res=S.get(url,timeout=12)
  soup=bs4.BeautifulSoup(res.text,'html.parser');soupurl=res.url
  links=[]
  for a in soup.select('a[href]'):
   txt=a.get_text(' ',strip=True).lower();href=a['href']
   if any(w in txt for w in ['superintendent','administration','leadership']) and not href.startswith(('mailto:','tel:','#')):
    target=urllib.parse.urljoin(soupurl,href)
    if target not in links:links.append(target)
  links.sort(key=lambda u: 'superintendent' not in u.lower())
  pages=[(soupurl,soup)]
  for target in links[:3]:
   if target==soupurl:continue
   try:
    res=S.get(target,timeout=10);pages.append((res.url,bs4.BeautifulSoup(res.text,'html.parser')))
   except Exception:pass
  found=[];needles=[r['name'].split()[-1].lower()]
  for i,(url,soup) in enumerate(pages):
   for tag in soup(['script','style','nav','footer','header']):tag.decompose()
   text=soup.get_text('\n',strip=True)
   n=r['leaId']+'-'+str(i)+'.txt';(P/'leader-sources'/n).write_text(text)
   if any(a in text.lower() for a in needles):
    pos=text.lower().find(needles[0]);found.append({'url':url,'evidence':text[max(0,pos-250):pos+500],'file':'leader-sources/'+n})
  return {**r,'currentCheck':'Matched surname on official district page' if found else 'No surname match; inspect captured pages','currentPages':[u for u,_ in pages],'currentEvidence':found}
 except Exception as e:return {**r,'currentCheck':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=14) as ex:
 checked=list(ex.map(fetch,rows))
(P/'leaders-indiana-current-checks.json').write_text(json.dumps({'asOf':'2026-10-22','records':checked},indent=2)+'\n')
for r in checked:print(r['districtName'],r['name'],r['currentCheck'])
