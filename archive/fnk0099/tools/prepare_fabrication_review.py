"""Build JLCPCB CPL and independent-check inputs from the native PCB (KiCad Python)."""
from pathlib import Path
import csv,json,hashlib,shutil
import pcbnew as p
r=Path(__file__).resolve().parents[1];out=r/'output/fabrication_review';b=p.LoadBoard(str(r/'hardware/gba_dumper.kicad_pcb'))
parts=json.loads((r/'hardware/bom/selected_parts.json').read_text()); selected={ref for part in parts for ref in part['refs']}
with (out/'review/kicad_positions.csv').open() as f: raw=list(csv.DictReader(f))
rows=[row for row in raw if row['Ref'] in selected]
assert len(rows)==35 and {row['Ref'] for row in rows}==selected
fp={f.GetReference():f for f in b.GetFootprints()}
for row in rows:
 f=fp[row['Ref']];assert abs(float(row['PosX'])-p.ToMM(f.GetPosition().x))<1e-6
 assert abs(float(row['PosY'])+p.ToMM(f.GetPosition().y))<1e-6
 assert float(row['Rot'])==f.GetOrientationDegrees() and row['Side']=='top'
with (out/'assembly/jlcpcb_cpl.csv').open('w') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
 for row in rows:w.writerow([row['Ref'],row['PosX']+'mm',row['PosY']+'mm','Top',row['Rot']])
shutil.copyfile(r/'hardware/bom/jlcpcb_pcba.csv',out/'assembly/jlcpcb_bom.csv')
drills={'PTH':[],'NPTH':[]};paste=[]
for f in b.GetFootprints():
 for pad in f.Pads():
  x,y=p.ToMM(pad.GetPosition().x),-p.ToMM(pad.GetPosition().y)
  dx,dy=p.ToMM(pad.GetDrillSize().x),p.ToMM(pad.GetDrillSize().y)
  if dx:
   kind='NPTH' if pad.GetAttribute()==p.PAD_ATTRIB_NPTH else 'PTH'
   # Current board oval holes are vertical with zero footprint rotation.
   if dx==dy:record=['circle',x,y,dx]
   else:
    assert f.GetOrientationDegrees()==0 and dy>dx
    d=(dy-dx)/2;record=['slot',x,y-d,x,y+d,dx]
   drills[kind].append(record)
  if f.GetReference() in selected:
   assert pad.IsOnLayer(p.F_Paste)
   size=pad.GetSize();sx,sy=p.ToMM(size.x),p.ToMM(size.y)
   paste.append([x-sx/2,y-sy/2,x+sx/2,y+sy/2])
for via in b.GetTracks():
 if isinstance(via,p.PCB_VIA):drills['PTH'].append(['circle',p.ToMM(via.GetPosition().x),-p.ToMM(via.GetPosition().y),p.ToMM(via.GetDrillValue())])
expected={'source_sha256':hashlib.sha256((r/'hardware/gba_dumper.kicad_pcb').read_bytes()).hexdigest(),'outline_centerline_mm':[0,-100,100,0],'drills':drills,'top_paste_pad_bboxes':paste,'pcba_refs':sorted(selected),'coordinate_convention':'PCB origin (0,0); Gerber/drill/CPL +X right, +Y up; current board spans Y -100..0 mm'}
(out/'review/expected_from_pcb.json').write_text(json.dumps(expected,indent=2)+'\n')
print('CPL35/BOM5; PCB coordinate/rotation match; expected drill counts', {k:len(v) for k,v in drills.items()})
