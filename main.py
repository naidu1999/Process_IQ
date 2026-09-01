from __future__ import annotations
import csv, threading
from pathlib import Path
from typing import Optional, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ProcessIQ backend: data-driven, explainable, and modular.
BACKEND_DIR=Path(__file__).resolve().parents[1]
PROJECT_DIR=BACKEND_DIR.parent
DATA_FILE=BACKEND_DIR/'data'/'processes.csv'
FRONTEND_DIR=PROJECT_DIR/'frontend'
LOCK=threading.Lock()
NUMERIC=['annual_volume','manual_effort_pct','error_rate_pct','business_impact','data_quality','implementation_complexity','risk_level']
CSV_FIELDS=['id','name','department','industry','description',*NUMERIC]

app=FastAPI(title='ProcessIQ API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=False,allow_methods=['*'],allow_headers=['*'])

class ProcessCreate(BaseModel):
    name:str=Field(...,min_length=2,max_length=120)
    department:str=Field(...,min_length=2,max_length=80)
    industry:str=Field(default='General',min_length=2,max_length=80)
    description:str=Field(...,min_length=5,max_length=500)
    annual_volume:float=Field(...,ge=0)
    manual_effort_pct:float=Field(...,ge=0,le=100)
    error_rate_pct:float=Field(...,ge=0,le=100)
    business_impact:float=Field(...,ge=0,le=10)
    data_quality:float=Field(...,ge=0,le=10)
    implementation_complexity:float=Field(...,ge=0,le=10)
    risk_level:float=Field(...,ge=0,le=10)

def score(p:dict[str,Any]):
    # Transparent weighted scoring. Higher opportunity = stronger automation case.
    b={
      'volume':min(float(p['annual_volume'])/25000*20,20),
      'manual_effort':float(p['manual_effort_pct'])/100*20,
      'error_exposure':min(float(p['error_rate_pct'])/20*15,15),
      'business_impact':float(p['business_impact'])/10*20,
      'data_readiness':float(p['data_quality'])/10*10,
      'ease_of_implementation':(10-float(p['implementation_complexity']))/10*10,
      'risk_adjustment':(10-float(p['risk_level']))/10*5,
    }
    return min(round(sum(b.values()),1),100.0),{k:round(v,1) for k,v in b.items()}

def recommendation(s:float):
    if s>=75:return 'High priority — strong automation candidate'
    if s>=55:return 'Medium priority — pilot recommended'
    return 'Lower priority — investigate before investment'

def solution(p):
    if p['manual_effort_pct']>=60 and p['data_quality']>=7:return 'Workflow automation with AI classification/copilot support and human approval for exceptions.'
    if p['error_rate_pct']>=10:return 'AI-assisted validation and anomaly detection combined with deterministic business rules.'
    if p['data_quality']<5:return 'Improve data quality first, then begin with analytics and decision support.'
    return 'Start with AI-assisted decision support and automate stable high-confidence steps after validation.'

def enrich(p):
    s,b=score(p); x=dict(p); x['opportunity_score']=s; x['score_breakdown']=b; x['recommendation']=recommendation(s); x['suggested_solution']=solution(x)
    x['explanation']=(f"Score {s}/100 is based on annual volume ({int(x['annual_volume']):,}), manual effort ({x['manual_effort_pct']}%), error rate ({x['error_rate_pct']}%), business impact ({x['business_impact']}/10), data quality ({x['data_quality']}/10), implementation complexity ({x['implementation_complexity']}/10), and risk ({x['risk_level']}/10).")
    return x

def load():
    rows=[]
    with DATA_FILE.open(encoding='utf-8',newline='') as f:
      for r in csv.DictReader(f):
        if not r.get('id'):continue
        r['id']=int(r['id'])
        for k in NUMERIC:r[k]=float(r[k])
        rows.append(enrich(r))
    return rows

@app.get('/api/health')
def health():return {'status':'ok','service':'ProcessIQ'}

@app.get('/api/processes')
def processes(department:Optional[str]=None,industry:Optional[str]=None,search:Optional[str]=None):
    rows=load()
    if department:rows=[p for p in rows if p['department'].lower()==department.lower()]
    if industry:rows=[p for p in rows if p['industry'].lower()==industry.lower()]
    if search:
      q=search.lower().strip(); rows=[p for p in rows if q in p['name'].lower() or q in p['description'].lower() or q in p['department'].lower() or q in p['industry'].lower()]
    return sorted(rows,key=lambda x:x['opportunity_score'],reverse=True)

@app.get('/api/processes/{process_id}')
def process(process_id:int):
    for p in load():
      if p['id']==process_id:return p
    raise HTTPException(404,'Process not found')

@app.post('/api/processes',status_code=201)
def add_process(process:ProcessCreate):
    # Runtime onboarding: new data is persisted without code or deployment changes.
    with LOCK:
      rows=load(); raw=process.model_dump(); raw['id']=max((p['id'] for p in rows),default=0)+1
      with DATA_FILE.open('a',encoding='utf-8',newline='') as f:
        csv.DictWriter(f,fieldnames=CSV_FIELDS).writerow({k:raw[k] for k in CSV_FIELDS})
    return enrich(raw)

@app.get('/api/dashboard')
def dashboard():
    rows=load(); n=len(rows)
    if not n:return {'total_processes':0,'average_score':0,'high_priority':0,'medium_priority':0,'department_scores':[],'industry_scores':[]}
    def group(field):
      d={}
      for p in rows:d.setdefault(p[field],[]).append(p['opportunity_score'])
      return sorted([{field:k,'average_score':round(sum(v)/len(v),1)} for k,v in d.items()],key=lambda x:x['average_score'],reverse=True)
    return {'total_processes':n,'average_score':round(sum(p['opportunity_score'] for p in rows)/n,1),'high_priority':sum(p['opportunity_score']>=75 for p in rows),'medium_priority':sum(55<=p['opportunity_score']<75 for p in rows),'department_scores':group('department'),'industry_scores':group('industry')}

@app.get('/api/ask')
def ask(question:str=Query(...,min_length=2,max_length=500)):
    rows=load(); q=question.lower(); ranked=sorted(rows,key=lambda x:x['opportunity_score'],reverse=True)
    if any(w in q for w in ['top','best','automate','first','priority']):
      ans='Top opportunities: '+'; '.join(f"{p['name']} ({p['opportunity_score']}/100, {p['department']})" for p in ranked[:5])
    elif 'department' in q:
      top=dashboard()['department_scores'][0]; ans=f"{top['department']} currently has the highest average opportunity score at {top['average_score']}/100."
    elif 'industry' in q:
      ans='Industry comparison: '+'; '.join(f"{x['industry']} ({x['average_score']}/100)" for x in dashboard()['industry_scores'])
    else:ans='ProcessIQ uses explainable scoring based on volume, manual effort, error exposure, business impact, data quality, implementation complexity and risk. Try asking which processes should be automated first.'
    return {'question':question,'answer':ans}

# Static frontend is mounted last so API routes remain available.
app.mount('/',StaticFiles(directory=str(FRONTEND_DIR),html=True),name='frontend')
