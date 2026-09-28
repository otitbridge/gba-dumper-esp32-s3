"""Add an inverse-silkscreen QR: white silk background and dark-board modules."""
from pathlib import Path
import sys,json
import pcbnew as p
sys.path.insert(0,'/Applications/KiCad/KiCad.app/Contents/SharedSupport/scripting/plugins')
from kicad_qrcode import QRCode,ErrorCorrectLevel
r=Path(__file__).resolve().parents[1];path=r/'hardware/gba_dumper.kicad_pcb'
url='https://github.com/otitbridge/gba-dumper-esp32-s3'
# Idempotent replacement of this generated artwork.
sys.path.insert(0,str(r/'tools'));sys.argv=['qr','noop']
from reroute_ad6 import without
meta=r/'hardware/verification/silkscreen/qr.json'
ids=[v['uuid'] for v in json.loads(meta.read_text())['rectangles']] if meta.exists() else []
path.write_text(without(path.read_text(),lambda t:any(f'(uuid "{u}")' in t for u in ids) or t.startswith('(gr_text "github.com/otitbridge/gba-dumper-esp32-s3"') or t.startswith('(gr_text "github.com/\\n')) )
q=QRCode.getMinimumQRCode(url,ErrorCorrectLevel.M);n=q.getModuleCount();border=4;pitch=.32;size=(n+8)*pitch;x0=29.5-size/2;y0=53.3-size/2
b=p.LoadBoard(str(path));items=[]
for row in range(n+8):
 col=0
 while col<n+8:
  def white(c):return not (border<=row<n+border and border<=c<n+border and q.isDark(row-border,c-border))
  if not white(col):col+=1;continue
  start=col
  while col<n+8 and white(col):col+=1
  t=p.PCB_SHAPE(b);t.SetShape(p.SHAPE_T_RECT);t.SetStart(p.VECTOR2I(p.FromMM(x0+start*pitch),p.FromMM(y0+row*pitch)));t.SetEnd(p.VECTOR2I(p.FromMM(x0+col*pitch),p.FromMM(y0+(row+1)*pitch)));t.SetLayer(p.F_SilkS);t.SetWidth(0);t.SetFilled(True);b.Add(t)
  items.append({'uuid':t.m_Uuid.AsString(),'start':[t.GetStart().x,t.GetStart().y],'end':[t.GetEnd().x,t.GetEnd().y]})
t=p.PCB_TEXT(b);t.SetText('github.com/\notitbridge/\ngba-dumper-\nesp32-s3');t.SetPosition(p.VECTOR2I(p.FromMM(16),p.FromMM(53.3)));t.SetTextSize(p.VECTOR2I(p.FromMM(1),p.FromMM(1)));t.SetTextThickness(p.FromMM(.15));t.SetLayer(p.F_SilkS);b.Add(t)
p.SaveBoard(str(path),b)
(r/'hardware/verification/silkscreen/qr.json').write_text(json.dumps({'url':url,'error_correction':'M','modules':n,'module_mm':pitch,'quiet_zone_modules':border,'size_mm':size,'center_mm':[29.5,53.3],'inverse_silk':True,'rectangles':items},indent=2)+'\n')
print('QR',n,size,len(items))
