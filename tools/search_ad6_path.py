import numpy as np,json,heapq,math
from pathlib import Path
w=Path('tmp/ad6-reroute');o=json.loads((w/'obstacles.json').read_text())
step=.15;xs=np.arange(35,60+step,step);ys=np.arange(62,88+step,step);X,Y=np.meshgrid(xs,ys);ny,nx=X.shape
occ=np.zeros((3,ny,nx),bool);vocc=np.zeros((ny,nx),bool)
clear=.22
for l,ax,ay,bx,by,width in o['segments']:
 dx=bx-ax;dy=by-ay;den=dx*dx+dy*dy
 u=np.clip(((X-ax)*dx+(Y-ay)*dy)/den,0,1) if den else 0
 dist=np.hypot(X-(ax+u*dx),Y-(ay+u*dy))
 occ[l]|=dist<(width/2+.125+clear+.04)
 vocc|=dist<(width/2+.3+clear+.04)
for layers,x1,y1,x2,y2 in o['pads']:
 dx=np.maximum(np.maximum(x1-X,X-x2),0);dy=np.maximum(np.maximum(y1-Y,Y-y2),0);d=np.hypot(dx,dy)
 for l in layers:occ[l]|=d<(.125+clear+.04)
 vocc|=d<(.3+clear+.04)
for x,y,rad in o['vias']:
 d=np.hypot(X-x,Y-y);occ|=d<(rad+.125+clear+.04);vocc|=d<(rad+.3+clear+.04)
startxy=(44.2958,66.862);endxy=(57,82.6)
node=lambda a:(round((a[1]-ys[0])/step),round((a[0]-xs[0])/step))
sy,sx=node(startxy);ey,ex=node(endxy)
starts=[(l,sy,sx) for l in [1,2] if not occ[l,sy,sx]]
print('start',starts,'end free',[not occ[l,ey,ex] for l in range(3)],flush=True)
best={a:0 for a in starts};prev={};q=[];i=0
h=lambda y,x:math.hypot(xs[x]-endxy[0],ys[y]-endxy[1])
for n in starts:heapq.heappush(q,(h(n[1],n[2]),0,i,n));i+=1
while q:
 _,cost,_,n=heapq.heappop(q)
 if cost>best.get(n,math.inf)+1e-9:continue
 l,y,x=n
 if (y,x)==(ey,ex):break
 neigh=[]
 for dy,dx in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
  yy,xx=y+dy,x+dx
  if 0<=yy<ny and 0<=xx<nx and not occ[l,yy,xx] and not occ[l,y,xx] and not occ[l,yy,x]:neigh.append(((l,yy,xx),step*math.hypot(dx,dy)))
 if not vocc[y,x]:
  for ll in range(3):
   if ll!=l and not occ[ll,y,x]:neigh.append(((ll,y,x),2.0))
 for nn,d in neigh:
  nd=cost+d
  if nd<best.get(nn,math.inf)-1e-9:best[nn]=nd;prev[nn]=n;i+=1;heapq.heappush(q,(nd+h(nn[1],nn[2]),nd,i,nn))
else:raise SystemExit('no path')
path=[n]
while n in prev:n=prev[n];path.append(n)
path.reverse();result=[[l,round(float(xs[x]),6),round(float(ys[y]),6)] for l,y,x in path]
# Merge collinear grid steps; preserve layer transitions.
simple=[result[0]]
for j in range(1,len(result)-1):
 a,c,d=result[j-1:j+2]
 if not(a[0]==c[0]==d[0]) or abs((c[1]-a[1])*(d[2]-c[2])-(c[2]-a[2])*(d[1]-c[1]))>1e-9:simple.append(c)
simple.append(result[-1]);simple.insert(0,[simple[0][0],*startxy]);simple.append([simple[-1][0],*endxy])
(w/'manual_path.json').write_text(json.dumps(simple,indent=2)+'\n')
print('cost',cost,'nodes',len(best),'path',simple,flush=True)
# Shortcut within each layer using conservatively inflated obstacle cells.
def visible(a,c):
 if a[0]!=c[0]:return False
 count=max(2,math.ceil(math.hypot(c[1]-a[1],c[2]-a[2])/.025))
 xx=np.linspace(a[1],c[1],count);yy=np.linspace(a[2],c[2],count)
 ix=np.rint((xx-xs[0])/step).astype(int);iy=np.rint((yy-ys[0])/step).astype(int)
 return not occ[a[0],iy,ix].any()
smoothed=[simple[0]];i=0
while i<len(simple)-1:
 j=i+1
 for k in range(i+1,len(simple)):
  if simple[k][0]!=simple[i][0]:break
  if visible(simple[i],simple[k]):j=k
 smoothed.append(simple[j]);i=j
(w/'manual_path.json').write_text(json.dumps(smoothed,indent=2)+'\n');print('smoothed',smoothed)
