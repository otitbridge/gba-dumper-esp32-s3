"""Compare track centreline sums and shortest signal paths on two native PCBs.
Run using KiCad Python. No PCB writes. Zones, pad interiors, component bodies,
jumper shunts and via barrel lengths are excluded from centreline lengths.
"""
from pathlib import Path
import collections,csv,hashlib,heapq,json,math
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
LAYERS=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
POWER={'/BOARD_3V3','/CART_3V3','/GND'}
def xy(v):return (v.x,v.y)
def distance(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])
def snapshot(path):
 b=p.LoadBoard(str(path));nets=collections.defaultdict(float);layers=collections.defaultdict(float);counts=collections.Counter();vias=collections.Counter()
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA): vias[t.GetNetname()]+=1;counts['through_vias']+=1
  else:
   length=p.ToMM(t.GetLength());nets[t.GetNetname()]+=length
   layers[b.GetLayerName(t.GetLayer())]+=length;counts[b.GetLayerName(t.GetLayer())]+=1
 zones=[z for z in b.Zones() if not z.GetIsRuleArea()]
 return b,{'source':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'track_total_mm':sum(nets.values()),'signal_track_mm':sum(v for n,v in nets.items() if n not in POWER),'power_track_mm':sum(nets[n] for n in POWER if n!='/GND'),'ground_track_mm':nets['/GND'],'layer_track_mm':dict(layers),'net_track_mm':dict(nets),'net_vias':dict(vias),'counts':dict(counts),'ground_zones':[{'layer':b.GetLayerName(z.GetLayer()),'net':z.GetNetname(),'area_mm2':z.GetFilledArea()/1e12,'islands':z.GetFilledPolysList(z.GetLayer()).OutlineCount()} for z in zones]}
def graph(b,net):
 tracks=[t for t in b.GetTracks() if t.GetNetname()==net and not isinstance(t,p.PCB_VIA)]
 vias=[t for t in b.GetTracks() if t.GetNetname()==net and isinstance(t,p.PCB_VIA)]
 pads=[(f.GetReference(),pad) for f in b.GetFootprints() for pad in f.Pads() if pad.GetNetname()==net]
 points={l:set() for l in LAYERS};g=collections.defaultdict(list)
 def edge(a,c,w):g[a].append((c,w));g[c].append((a,w))
 for t in tracks:
  assert not isinstance(t,p.PCB_ARC),'Arc paths need explicit arc splitting'
  points[t.GetLayer()].update([xy(t.GetStart()),xy(t.GetEnd())])
 for via in vias:
  for l in LAYERS:
   if via.IsOnLayer(l):points[l].add(xy(via.GetPosition()))
 for ref,pad in pads:
  for l in LAYERS:
   if pad.IsOnLayer(l):points[l].add(xy(pad.GetPosition()))
 # Split centreline segments at every same-layer junction (including T branches).
 for t in tracks:
  a,c=xy(t.GetStart()),xy(t.GetEnd());dx=c[0]-a[0];dy=c[1]-a[1];den=dx*dx+dy*dy
  if not den:continue
  cuts=[];l=t.GetLayer()
  for q in points[l]:
   u=((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den
   if -1e-9<=u<=1+1e-9 and abs((q[0]-a[0])*dy-(q[1]-a[1])*dx)/math.sqrt(den)<=10:
    cuts.append((u,q))
  cuts.sort()
  for (_,v),(_,w) in zip(cuts,cuts[1:]):edge((l,*v),(l,*w),distance(v,w)/1e6)
 # Conductive pad interiors are zero-length connectors, not fictitious traces.
 for ref,pad in pads:
  node=('pad',ref,pad.GetNumber())
  for l in LAYERS:
   if pad.IsOnLayer(l):
    for q in points[l]:
     if pad.HitTest(p.VECTOR2I(*q)):edge(node,(l,*q),0)
 for via in vias:
  q=xy(via.GetPosition());active=[l for l in LAYERS if via.IsOnLayer(l)]
  for l in active[1:]:edge((active[0],*q),(l,*q),0)
 return g

def shortest(g,start,end):
 queue=[(0,0,start)];counter=0;best={start:0}
 while queue:
  d,_,v=heapq.heappop(queue)
  if v==end:return d
  if d>best[v]:continue
  for w,length in g[v]:
   nd=d+length
   if nd<best.get(w,math.inf):
    best[w]=nd;counter+=1;heapq.heappush(queue,(nd,counter,w))
 raise AssertionError(f'No centreline path {start} -> {end}')
def paths(b,rows):
 out={};cache={}
 def route(net,start,end):
  if net not in cache:cache[net]=graph(b,net)
  return shortest(cache[net],('pad',*start),('pad',*end))
 for row in rows:
  s=row['signal'];ref=row['resistor'];net='/MCU_'+s
  src=next((f.GetReference(),pad.GetNumber()) for f in b.GetFootprints() if f.GetReference() in ['J1','J2'] for pad in f.Pads() if pad.GetNetname()==net)
  segments=[(net,src,(ref,'1'))]
  if s=='nWR':segments += [('/WR_LINK',(ref,'2'),('JP1','1')),('/CART_nWR',('JP1','2'),('J3',str(row['cart_pin'])))]
  else:segments += [('/CART_'+s,(ref,'2'),('J3',str(row['cart_pin'])))]
  parts=[{'net':n,'from':a,'to':c,'track_path_mm':route(n,a,c)} for n,a,c in segments]
  out[s]={'path_mm':sum(x['track_path_mm'] for x in parts),'segments':parts}
 return out

def main():
 old_b,old=snapshot(ROOT/'archive/fnk0099/gba_dumper.kicad_pcb');new_b,new=snapshot(ROOT/'hardware/gba_dumper.kicad_pcb')
 rows=json.loads((ROOT/'hardware/pinmap.json').read_text())['signals']
 old['signal_paths']=paths(old_b,rows);new['signal_paths']=paths(new_b,rows)
 signals=[]
 for row in rows:
  s=row['signal'];a=old['signal_paths'][s]['path_mm'];c=new['signal_paths'][s]['path_mm']
  nets=['/MCU_'+s,'/CART_'+s]+(['/WR_LINK'] if s=='nWR' else [])
  sums=[sum(data['net_track_mm'].get(n,0) for n in nets) for data in [old,new]]
  assert a<=sums[0]+.001 and c<=sums[1]+.001
  signals.append({'signal':s,'fnk_path_mm':a,'weact_path_mm':c,'path_delta_mm':c-a,'path_delta_percent':100*(c/a-1),'fnk_net_sum_mm':sums[0],'weact_net_sum_mm':sums[1],'fnk_vias':sum(old['net_vias'].get(n,0) for n in nets),'weact_vias':sum(new['net_vias'].get(n,0) for n in nets)})
 result={'method':'KiCad track centreline length; branched-net sums and shortest pad-connected paths reported separately. Excludes pad interiors, components, shunts, via barrels and copper zones. Parent PCB only, not daughterboard traces. No delay/equal-length guarantee.','fnk0099':old,'weact':new,'signals':signals}
 out=ROOT/'hardware/verification';(out/'routing_comparison.json').write_text(json.dumps(result,indent=2)+'\n')
 with (out/'routing_comparison.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(signals[0]),lineterminator="\n");w.writeheader();w.writerows([{k:round(v,3) if isinstance(v,float) else v for k,v in row.items()} for row in signals])
 with (out/'routing_nets.csv').open('w') as f:
  w=csv.writer(f,lineterminator="\n");w.writerow(['net','FNK0099_track_mm','WeAct_track_mm','delta_mm','FNK0099_vias','WeAct_vias'])
  for n in sorted(set(old['net_track_mm'])|set(new['net_track_mm'])):
   a=old['net_track_mm'].get(n,0);c=new['net_track_mm'].get(n,0)
   w.writerow([n,round(a,3),round(c,3),round(c-a,3),old['net_vias'].get(n,0),new['net_vias'].get(n,0)])
 for key in ['track_total_mm','signal_track_mm','power_track_mm','ground_track_mm']:
  print(key,round(old[key],3),round(new[key],3),round(100*(new[key]/old[key]-1),2))
 print('Vias:',old['counts']['through_vias'],new['counts']['through_vias'])
 print('Max path changes:',[(s['signal'],round(s['path_delta_mm'],2),round(s['path_delta_percent'],2)) for s in sorted(signals,key=lambda x:abs(x['path_delta_percent']),reverse=True)[:6]])
 print('Max paths:',max(s['fnk_path_mm'] for s in signals),max(s['weact_path_mm'] for s in signals))
if __name__=='__main__':main()
