from pathlib import Path
import sys,csv,json
import mpmath as mp
import numpy as np
sys.path.insert(0,'/mnt/data/circle26_strict_work')
import contact_flip as cf
ROOT=Path('/mnt/data/circle26_strict_work')
mp.mp.dps=120
# refine float seed first
rr=cf.solve_graph(cf.ACTIVE,cf.z0,max_nfev=10000)
zf=rr.x
N=cf.n
keys=cf.ACTIVE

def m(x):
    # exact conversion of a 17-digit roundtrip decimal for the binary float
    return mp.mpf(format(float(x),'.17g'))
z=[m(x) for x in zf]

def fj(z):
    F=[]; J=[[mp.mpf('0') for _ in range(3*N)] for __ in range(3*N)]
    for row,k in enumerate(keys):
        if k[0]=='W':
            _,i,s=k; x=z[3*i];y=z[3*i+1];r=z[3*i+2]
            if s=='L': F.append(x-r); J[row][3*i]=1;J[row][3*i+2]=-1
            elif s=='R': F.append(1-x-r); J[row][3*i]=-1;J[row][3*i+2]=-1
            elif s=='B': F.append(y-r); J[row][3*i+1]=1;J[row][3*i+2]=-1
            elif s=='T': F.append(1-y-r); J[row][3*i+1]=-1;J[row][3*i+2]=-1
        else:
            _,i,j=k
            dx=z[3*i]-z[3*j];dy=z[3*i+1]-z[3*j+1]
            d=mp.sqrt(dx*dx+dy*dy)
            F.append(d-z[3*i+2]-z[3*j+2])
            ux=dx/d;uy=dy/d
            J[row][3*i]=ux;J[row][3*i+1]=uy;J[row][3*i+2]=-1
            J[row][3*j]=-ux;J[row][3*j+1]=-uy;J[row][3*j+2]=-1
    return mp.matrix(F),mp.matrix(J)

hist=[]
for it in range(12):
    F,J=fj(z); maxf=max(abs(x) for x in F); hist.append(mp.nstr(maxf,30)); print('it',it,'maxf',mp.nstr(maxf,40),flush=True)
    if maxf < mp.mpf('1e-100'): break
    dz=mp.lu_solve(J,-F)
    # full Newton should be safe this close; backtrack if needed
    alpha=mp.mpf(1)
    cur=maxf
    while alpha>mp.mpf('1e-8'):
        zt=[z[i]+alpha*dz[i] for i in range(3*N)]
        Ft,_=fj(zt); nxt=max(abs(x) for x in Ft)
        if nxt < cur: z=zt; break
        alpha/=2
    else: raise RuntimeError('Newton backtrack failed')

# All strict gaps at the exact contact root.
def gap(z,k):
    if k[0]=='W':
        _,i,s=k;x=z[3*i];y=z[3*i+1];r=z[3*i+2]
        return {'L':x-r,'R':1-x-r,'B':y-r,'T':1-y-r}[s]
    _,i,j=k;dx=z[3*i]-z[3*j];dy=z[3*i+1]-z[3*j+1]
    return mp.sqrt(dx*dx+dy*dy)-z[3*i+2]-z[3*j+2]
allg=[gap(z,k) for k in cf.ALL]
activeg=[gap(z,k) for k in cf.ACTIVE]
inactiveg=[gap(z,k) for k in cf.INACTIVE]
score=sum(z[2::3])
print('score exact graph',mp.nstr(score,110))
print('max active abs',mp.nstr(max(abs(x) for x in activeg),50))
print('min inactive',mp.nstr(min(inactiveg),50))
# Round to 90 decimal places, then shrink each radius enough to absorb all rounding.
places=90
q=mp.mpf(10)**(-places)
def quant(x): return mp.nint(x/q)*q
zq=[quant(x) for x in z]
# determine min gap after coordinate/radius quantization before shrink
ming_q=min(gap(zq,k) for k in cf.ALL)
# uniform shrink: for walls gap increases delta; pairs increase 2 delta.
# ensure at least 1e-75 margin, much larger than 90-digit quantization uncertainty.
target_margin=mp.mpf('1e-75')
delta=max(mp.mpf('0'),target_margin-ming_q)
# walls need delta, pair only delta*2; using target-ming is conservative
zs=zq[:]
for i in range(N): zs[3*i+2]-=delta
strictg=[gap(zs,k) for k in cf.ALL]
strictscore=sum(zs[2::3])
print('quant min gap',mp.nstr(ming_q,50),'delta',mp.nstr(delta,50))
print('strict score',mp.nstr(strictscore,110))
print('strict min gap',mp.nstr(min(strictg),50))
# output CSV with fixed 90 decimals
csvp=ROOT/'strict_high_precision.csv'
with csvp.open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['circle','x','y','radius'])
    for i in range(N):
        w.writerow([i,mp.nstr(zs[3*i],places+3,strip_zeros=False),mp.nstr(zs[3*i+1],places+3,strip_zeros=False),mp.nstr(zs[3*i+2],places+3,strip_zeros=False)])
report={
 'mp_dps':mp.mp.dps,'newton_history':hist,
 'contact_graph_score':mp.nstr(score,115),
 'strict_score':mp.nstr(strictscore,115),
 'strict_min_gap':mp.nstr(min(strictg),80),
 'strict_max_gap_violation':mp.nstr(min(mp.mpf(0),min(strictg)),80),
 'min_inactive_gap_at_root':mp.nstr(min(inactiveg),80),
 'quantization_places':places,'uniform_radius_shrink':mp.nstr(delta,80),
 'num_active':len(cf.ACTIVE),'num_constraints':len(cf.ALL)
}
(ROOT/'high_precision_report.json').write_text(json.dumps(report,indent=2))
print('saved',csvp)
