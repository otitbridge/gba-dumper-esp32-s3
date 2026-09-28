"""Local CAD preflight only; never grants manufacturing approval."""
from pathlib import Path
import json,csv,pcbnew as p
r=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(r/'hardware/gba_dumper.kicad_pcb'))
drc=json.loads((r/'hardware/verification/routing_drc.json').read_text())
assert not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity']
parts=json.loads((r/'hardware/bom/selected_parts.json').read_text()); refs={ref for row in parts for ref in row['refs']}
assert len(refs)==35
fp={f.GetReference():f for f in b.GetFootprints()}
assert all(fp[ref].GetLayer()==p.F_Cu for ref in refs)
with (r/'hardware/bom/jlcpcb_pcba.csv').open() as f: bom=list(csv.DictReader(f))
assert {ref for row in bom for ref in row['Designator'].split(',')}==refs
assert len(bom)==5 and not refs & {'J1','J2','J3','JP1','JP2'}
for f in b.GetFootprints():
 for field in f.GetFields():
  if field.GetLayer() in [p.F_SilkS,p.B_SilkS] and field.IsVisible():
   assert field.GetTextSize().y>=p.FromMM(1) and field.GetTextThickness()>=p.FromMM(.15)
texts={d.GetText() for d in b.GetDrawings() if isinstance(d,p.PCB_TEXT) and d.GetLayer()==p.F_SilkS}
assert {'NATIVE USB','DO NOT CONNECT - GBA BUS','REMOVE USB FIRST','DEFAULT OPEN','NORMALLY CLOSED','GBA ONLY / 3.3V'}<=texts
result={'cad_drc_violations':0,'unconnected':0,'schematic_parity_issues':0,'pcba_parts':35,'pcba_part_numbers':5,'pcba_side':'Top','manufacturing_approved':False,'outstanding':['Gate 1-3 remaining physical/electrical checks','Native USB cap retention and cartridge handling checks','Economic PCBA tooling holes / rails / fiducial CAM review','Gerber / drill / CPL export and independent output inspection']}
(r/'hardware/verification/fabrication_preflight.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: CAD DRC/parity clean; 35 top-side PCBA placements / 5 BOM rows; silk dimensions and operating labels. Manufacturing approval remains false.')
