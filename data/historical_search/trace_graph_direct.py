from __future__ import annotations
import os
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('MKL_NUM_THREADS','1')
import sys,json,time,argparse
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0,'/mnt/data/circle26_strict_work')
import contact_flip as cf
ROOT=Path('/mnt/data/circle26_strict_work');N=cf.n
LO=np.tile([1e-10,1e-10,1e-10],N);HI=np.tile([1-1e-10,1-1e-10,.499999],N)

def keystr(k): return ':'.join(map(str,k))
def vals_jac(z,keys):
 vals=[];jac=[]
 for k in keys:
  v,g=cf.gap_and_grad(z,k); vals.append(v);jac.append(g)
 return np.asarray(vals),np.asarray(jac)
def solve_graph(keys,zstart,max_nfev=5000):
 def f(z): return vals_jac(z,keys)[0]
 def j(z): return vals_jac(z,keys)[1]
 return least_squares(f,zstart,jac=j,bounds=(LO,HI),method='trf',xtol=3e-13,ftol=3e-13,gtol=3e-13,max_nfev=max_nfev,x_scale='jac')
def tangent(z,rem,prev=None):
 _,J=vals_jac(z,rem); _,s,Vh=np.linalg.svd(J,full_matrices=True);v=Vh[-1];v/=np.linalg.norm(v)
 if prev is not None and np.dot(v,prev)<0:v=-v
 return v,float(s[-1]),float(s[0]/s[-1])
def correct(zpred,rem,vplane,max_nfev=80):
 def f(z):
  a,_=vals_jac(z,rem);return np.r_[a,np.dot(vplane,z-zpred)]
 def j(z):
  _,J=vals_jac(z,rem);return np.vstack([J,vplane])
 return least_squares(f,zpred,jac=j,bounds=(LO,HI),method='trf',xtol=3e-13,ftol=3e-13,gtol=3e-13,max_nfev=max_nfev,x_scale='jac')
def evaluate(z):
 vals=np.array([cf.gap_and_grad(z,k)[0] for k in cf.ALL]);R=cf.unpack(z)[1]
 return {'score':float(R.sum()),'min_gap':float(vals.min()),'bad':int(np.sum(vals<-1e-9))}
@lru_cache(maxsize=8)
def load_base(path):
 a=np.load(path)
 if 'z' in a:z=np.array(a['z'],float)
 else:
  C=np.array(a['C'],float);R=np.array(a['R'],float);z=cf.pack(C,R)
 # solve its exact active graph to stabilize
 gg={k:cf.gap_and_grad(z,k)[0] for k in cf.ALL}
 active=sorted([k for k,g in gg.items() if g<1e-7],key=lambda k:gg[k])
 if len(active)!=3*N: raise RuntimeError(f'active count {len(active)}')
 rr=solve_graph(active,z,10000);z=rr.x
 gg={k:cf.gap_and_grad(z,k)[0] for k in cf.ALL}
 inactive=[k for k in cf.ALL if k not in set(active)]
 return z,active,inactive,gg
def trace(path,di,max_steps=180,max_arc=1.2,h0=1.5e-3):
 zbase,active,inactive,gaps=load_base(path)
 drop=active[di];rem=[k for k in active if k!=drop]
 z=zbase.copy();v,_,_=tangent(z,rem)
 gd=cf.gap_and_grad(z,drop)[1]
 if np.dot(gd,v)<0:v=-v
 h=h0;arc=0.;prevz=z.copy();prevgaps={k:cf.gap_and_grad(z,k)[0] for k in inactive};rec=[];event=None
 for it in range(max_steps):
  zpred=z+h*v
  if np.any(zpred<=LO) or np.any(zpred>=HI):h*=.5;continue
  res=correct(zpred,rem,v)
  if (not res.success and res.cost>1e-18) or res.cost>1e-16:
   h*=.5
   if h<1e-7:break
   continue
  zn=res.x;ds=float(np.linalg.norm(zn-z))
  if ds<1e-10:
   h=min(.03,h*1.4);continue
  dropgap=cf.gap_and_grad(zn,drop)[0]
  ingaps={k:cf.gap_and_grad(zn,k)[0] for k in inactive}
  crossed=[k for k,g in ingaps.items() if g<=0 and prevgaps.get(k,1)>0]
  ev=evaluate(zn)
  rec.append({'it':it,'arc':arc+ds,'h':h,'score':ev['score'],'min_gap':ev['min_gap'],'drop_gap':dropgap,'min_inactive':min(ingaps.values()),'cost':float(res.cost)})
  if crossed:
   add=min(crossed,key=lambda k:prevgaps[k]/max(prevgaps[k]-ingaps[k],1e-300))
   frac=prevgaps[add]/max(prevgaps[add]-ingaps[add],1e-300)
   guess=prevz+frac*(zn-prevz); keys=rem+[add]
   rr=solve_graph(keys,guess,10000);ee=evaluate(rr.x)
   _,J=vals_jac(rr.x,keys);grad=np.zeros(3*N);grad[2::3]=1
   lam=np.linalg.solve(J.T,grad)
   event={'drop':keystr(drop),'add':keystr(add),'score':ee['score'],'min_gap':ee['min_gap'],'bad':ee['bad'],'cost':float(rr.cost),'nfev':int(rr.nfev),'distance':float(np.linalg.norm(rr.x-zbase)),'drop_gap':cf.gap_and_grad(rr.x,drop)[0],'add_gap':cf.gap_and_grad(rr.x,add)[0],'lambda_min':float(lam.min()),'lambda_max':float(lam.max()),'arc':arc+frac*ds,'steps':it+1,'z':rr.x.tolist()}
   break
  if dropgap < -1e-8:break
  prevz=z.copy();prevgaps=ingaps;z=zn;arc+=ds;v,_,_=tangent(z,rem,prev=v)
  if res.nfev<=4:h=min(.02,h*1.25)
  elif res.nfev>10:h=max(1e-6,h*.6)
  if arc>=max_arc:break
 return {'di':di,'drop':keystr(drop),'base_score':evaluate(zbase)['score'],'event':event,'trace':rec,'active':[keystr(k) for k in active]}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('base');ap.add_argument('tag');ap.add_argument('di',type=int);a=ap.parse_args();t=time.time()
 q=trace(a.base,a.di);q['elapsed']=time.time()-t
 out=ROOT/f'{a.tag}_trace_{a.di}.json';out.write_text(json.dumps(q,indent=2));print(json.dumps({k:v for k,v in q.items() if k not in ('trace','active')}))
if __name__=='__main__':main()
