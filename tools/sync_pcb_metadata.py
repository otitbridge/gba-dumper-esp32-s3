"""Synchronize PCB metadata with the schematic without changing geometry or nets."""
from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew as p
r=Path(__file__).resolve().parents[1];path=r/'hardware/gba_dumper.kicad_pcb'
b=p.LoadBoard(str(path));comps={c.attrib['ref']:c for c in ET.parse(r/'hardware/verification/gba_dumper.xml').findall('.//components/comp')}
for fp in b.GetFootprints():
 ref=fp.GetReference()
 if ref.startswith('H'):
  fp.SetAttributes(fp.GetAttributes()|p.FP_BOARD_ONLY);continue
 if ref.startswith('TP'):fp.SetAttributes(fp.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM)
 current={f.GetName() for f in fp.GetFields()}
 for field in comps[ref].findall('fields/field'):
  name=field.attrib['name']
  if name in ['Footprint','Datasheet','Description'] or name in current:continue
  item=p.PCB_FIELD(fp,p.FIELD_T_USER,name);item.SetText(field.text or '');item.SetVisible(False);item.SetPosition(fp.GetPosition());fp.Add(item)
p.SaveBoard(str(path),b)
