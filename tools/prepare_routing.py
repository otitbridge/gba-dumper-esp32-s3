"""Prepare a working copy and a local-router DSN; never overwrite source PCB."""
from pathlib import Path
import re,pcbnew as p
r=Path(__file__).resolve().parents[1];out=r/'tmp/weact-routing';out.mkdir(parents=True,exist_ok=True)
b=p.LoadBoard(str(r/'hardware/gba_dumper.kicad_pcb'))
if len(b.GetTracks()): raise SystemExit('Source is already routed')
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for f in b.GetFootprints():
 if f.GetReference() not in ['C1','C2','R33','TP2']: continue
 pad=next(pad for pad in f.Pads() if pad.GetNetname()=='/GND')
 start=pad.GetPosition(); end=V(p.ToMM(start.x),p.ToMM(start.y)+2)
 t=p.PCB_TRACK(b);t.SetStart(start);t.SetEnd(end);t.SetWidth(p.FromMM(.5));t.SetLayer(p.F_Cu);t.SetNet(pad.GetNet());b.Add(t)
 via=p.PCB_VIA(b);via.SetPosition(end);via.SetWidth(p.FromMM(.6));via.SetDrill(p.FromMM(.3));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(pad.GetNet());b.Add(via)
p.SaveBoard(str(out/'prepared.kicad_pcb'),b)
# KiCad DSN exporter treats footprint-only keepouts as copper keepouts too.
# Omit ONLY this rule area from the export working copy; source keeps it intact.
for zone in list(b.Zones()):
 if zone.GetZoneName()=='WEACT_UNDERSIDE_NO_COMPONENTS': b.Remove(zone)
assert p.ExportSpecctraDSN(b,str(out/'route.dsn'))
s=(out/'route.dsn').read_text()
s=s.replace('(layer In1.Cu\n      (type signal)', '(layer In1.Cu\n      (type power)')
# Router-only rectangular margins around the two rounded J3 NPTH slots.
extra=''
for x in [12.8,82.7]:
 for layer in ['F.Cu','In1.Cu','In2.Cu','B.Cu']:
  extra+=f'    (keepout \"J3_SLOT_MARGIN\" (rect {layer} {(x-1.2)*1000} -28300 {(x+1.2)*1000} -22900))\n'
s=s.replace('    (boundary',extra+'    (boundary',1)
s=s.replace('(class POWER_3V3 /BOARD_3V3 /CART_3V3 /GND','(class POWER_3V3 /BOARD_3V3 /CART_3V3')
pos=s.index('  (wiring')
s=s[:pos].rstrip()[:-1]+'''    (class GROUND /GND
      (circuit (use_via "Via[0-3]_600:300_um"))
      (rule (width 800) (clearance 200)))
  )
'''+s[pos:]
s=s.replace('(type route)', '(type protect)')
(out/'route.dsn').write_text(s)
(out/'route.rules').write_text('''(rules PCB route
 (autoroute_settings
  (autoroute on) (postroute on)
  (layer_rule F.Cu (active on) (preferred_direction horizontal))
  (layer_rule In1.Cu (active off))
  (layer_rule In2.Cu (active on) (preferred_direction vertical))
  (layer_rule B.Cu (active on) (preferred_direction horizontal))))
''')
print('Prepared WeAct GND fanouts; In1 reserved for GND plane')
