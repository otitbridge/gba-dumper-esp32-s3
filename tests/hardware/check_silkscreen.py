"""Verify this milestone changes only silkscreen text, not copper or geometry."""
from pathlib import Path
import sys,json,hashlib
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'tools'))
sys.argv=['check','noop'];from reroute_ad6 import blocks,without
import pcbnew as p
before=r/'hardware/verification/silkscreen/before.kicad_pcb';after=r/'hardware/gba_dumper.kicad_pcb'
def silk(t):return '(layer "F.SilkS")' in t or '(layer "B.SilkS")' in t
qr_path=r/'hardware/verification/silkscreen/qr.json'
qr=json.loads(qr_path.read_text()) if qr_path.exists() else None
qr_ids={v['uuid'] for v in qr['rectangles']} if qr else set()
def fixed(path):
 out=[]
 for _,_,t in blocks(path.read_text()):
  if t.startswith('(gr_rect') and any(f'(uuid "{u}")' in t for u in qr_ids):continue
  if t.startswith('(gr_text') and silk(t):continue
  if t.startswith('(footprint'):
   t=without(t,lambda c:c.startswith(('(property','(fp_text')) and silk(c))
  # Whitespace around removed fields is not meaningful.
  out.append(' '.join(t.split()))
 return sorted(out)
assert fixed(before)==fixed(after),'Non-silkscreen board content changed'
b=p.LoadBoard(str(after));texts=[]
for d in b.GetDrawings():
 if isinstance(d,p.PCB_TEXT) and d.GetLayer() in [p.F_SilkS,p.B_SilkS]:texts.append(d)
for f in b.GetFootprints():
 texts.extend(d for d in f.GetFields() if d.IsVisible() and d.GetLayer() in [p.F_SilkS,p.B_SilkS])
for t in texts:
 assert min(t.GetTextSize().x,t.GetTextSize().y)>=p.FromMM(1)
 assert t.GetTextThickness()>=p.FromMM(.15)
 assert 'UNROUTED' not in t.GetText() and 'FNK0099' not in t.GetText()
required={'GBA DUMPER / WEACT ESP32S3-A','S3-WROOM-1-N16R2 / REMOVE USB FIRST','PC','CARTRIDGE','GBA ONLY / 3.3V','WR ENABLE','DEFAULT OPEN','POWER LINK','DEFAULT CLOSED'}
assert not {'NATIVE USB: UNUSED','PC: USB-UART','PC : USB-UART','WEACT ESP32S3-A / N16R2','REMOVE USB FIRST','GBA DUMPER / WEACT','JP1 / JP2 / CARTRIDGE'} & {t.GetText() for t in texts}
assert required<={t.GetText() for t in texts}
print('PASS: only silk text changed; all copper, pads, components, holes and other geometry unchanged; text >=1mm/0.15mm; required labels present')

if qr:
 drawings={d.m_Uuid.AsString():d for d in b.GetDrawings()}
 for item in qr['rectangles']:
  d=drawings[item['uuid']]
  assert d.GetLayer()==p.F_SilkS and d.GetShape()==p.SHAPE_T_RECT and d.IsSolidFill() and d.GetWidth()==0
  assert [d.GetStart().x,d.GetStart().y]==item['start'] and [d.GetEnd().x,d.GetEnd().y]==item['end']
 assert qr['quiet_zone_modules']==4 and qr['module_mm']>=.3
 print('PASS: QR-only silk rectangles match recorded geometry; no copper changes')
