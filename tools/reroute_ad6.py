"""AD6-only routing experiment: other tracks are protected; import AD6 only."""
from pathlib import Path
import sys,shutil,re
import pcbnew as p
r=Path(__file__).resolve().parents[1];w=r/'tmp/ad6-reroute';w.mkdir(parents=True,exist_ok=True)
def blocks(s):
 depth=0;quoted=False;escape=False;start=None
 for i,c in enumerate(s):
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
   continue
  if c=='"':quoted=True
  elif c=='(':
   if depth==1:start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==1 and start is not None:yield start,i+1,s[start:i+1]
def target(t):return t.startswith(('(segment','(via')) and any(f'(net "{n}")' in t for n in ['/MCU_AD6','/CART_AD6'])
def without(s,predicate):
 for a,b,t in reversed(list(blocks(s))):
  if predicate(t):s=s[:a]+s[b:]
 return s
if sys.argv[1]=='prepare':
 src=(r/'hardware/gba_dumper.kicad_pcb').read_text();(w/'before.kicad_pcb').write_text(src)
 # Keep the original R7 escape and CART_AD6; reroute MCU_AD6 beyond its via.
 s=without(src,lambda t:target(t) and '(net "/MCU_AD6")' in t and '(layer "In2.Cu")' in t)
 (w/'prepared.kicad_pcb').write_text(s)
 export=without(s,lambda t:t.startswith('(zone') and any(f'(name "{n}")' in t for n in ['WEACT_UNDERSIDE_NO_COMPONENTS','GND_CONTINUOUS_IN1']))
 (w/'export.kicad_pcb').write_text(export)
 b=p.LoadBoard(str(w/'export.kicad_pcb'));assert p.ExportSpecctraDSN(b,str(w/'route.dsn'))
 s=(w/'route.dsn').read_text().replace('(type route)','(type protect)').replace('(layer In1.Cu\n      (type signal)','(layer In1.Cu\n      (type power)')
 extra=''
 for x in [12.8,82.7]:
  for layer in ['F.Cu','In1.Cu','In2.Cu','B.Cu']:extra+=f'    (keepout "J3_SLOT_MARGIN" (rect {layer} {(x-1.2)*1000} -28300 {(x+1.2)*1000} -22900))\n'
 s=s.replace('    (boundary',extra+'    (boundary',1);(w/'route.dsn').write_text(s)
 shutil.copy2(r/'tmp/weact-routing/route.rules',w/'route.rules')
 print('Prepared protected-route AD6 experiment')
elif sys.argv[1]=='import':
 b=p.LoadBoard(str(w/'prepared.kicad_pcb'));assert p.ImportSpecctraSES(b,str(w/'route.ses'))
 p.SaveBoard(str(w/'router_result.kicad_pcb'),b)
 src=(w/'before.kicad_pcb').read_text();other=[t for _,_,t in blocks(src) if t.startswith(('(segment','(via')) and not target(t)]
 s=without(src,target);new='\n'.join(t for _,_,t in blocks((w/'router_result.kicad_pcb').read_text()) if target(t))
 i=s.rfind(')');s=s[:i]+new+'\n'+s[i:]
 assert other==[t for _,_,t in blocks(s) if t.startswith(('(segment','(via')) and not target(t)]
 (w/'candidate.kicad_pcb').write_text(s)
 for ext in ['kicad_pro','kicad_dru']:shutil.copy2(r/f'hardware/gba_dumper.{ext}',w/f'candidate.{ext}')
 (w/'fp-lib-table').write_text((r/'hardware/fp-lib-table').read_text().replace('${KIPRJMOD}',str(r/'hardware')))
 print('Imported AD6 only; other track/via blocks byte-identical')
