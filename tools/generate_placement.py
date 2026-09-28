#!/usr/bin/env python3
"""KiCad 10 pcbnew: regenerate an UNROUTED placement from the exported netlist.
Run with KiCad's bundled Python. Refuses to overwrite a routed board.
"""
from pathlib import Path
import json, re, xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/gba_dumper.kicad_pcb'
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
if OUT.exists() and len(p.LoadBoard(str(OUT)).GetTracks()):
 raise SystemExit('Refusing to overwrite routing; edit the existing board instead.')
mm=p.FromMM
vec=lambda x,y:p.VECTOR2I(mm(x),mm(y))
b=p.BOARD(); b.SetCopperLayerCount(4)
b.GetDesignSettings().SetBoardThickness(mm(1.6))
b.GetDesignSettings().m_SolderMaskMinWidth=mm(.1)
xml=ET.parse(ROOT/'hardware/verification/gba_dumper.xml')
root_uuid=re.search(r'\(uuid "([^"]+)"', (ROOT/'hardware/gba_dumper.kicad_sch').read_text())[1]
net_by_pad={}
for node in xml.findall('.//nets/net'):
 net=p.NETINFO_ITEM(b,node.attrib['name']); b.Add(net)
 for pad in node.findall('node'): net_by_pad[(pad.attrib['ref'],pad.attrib['pin'])]=net
coords={'J1':(57,44.5,0),'J2':(84.94,44.5,0),'J3':(28,27,0),'C1':(22,33,0),'C2':(28,33,0),'JP1':(32,72,0),'JP2':(13,38,0),'R33':(37,33,0)}
for i in range(16): coords[f'R{i+1}']=(46,47+i*3,0)
for i in range(8): coords[f'R{i+17}']=(94,49+i*4,0)
for i in range(4):
 coords[f'R{i+25}']=(20,62+i*4,0)
 coords[f'R{i+29}']=(20,80+i*4,0)
for i,xy in enumerate([(7,34),(7,48),(7,59),(7,65),(7,71),(7,77),(38,47),(38,92),(94,38),(94,83),(37,39),(43,39)],1): coords[f'TP{i}']=(*xy,0)
placements=[]
for c in xml.findall('.//components/comp'):
 ref=c.attrib['ref']; lib,name=c.findtext('footprint').split(':')
 base=ROOT/'hardware/lib'/f'{lib}.pretty' if lib in {'GBA_Mechanical','Gekkio_Connector_PCBEdge'} else LIB/f'{lib}.pretty'
 fp=p.FootprintLoad(str(base),name)
 if fp is None: raise RuntimeError(f'Missing footprint {lib}:{name}')
 fp.SetFPID(p.LIB_ID(lib,name)); fp.SetReference(ref); fp.SetValue(c.findtext('value'))
 fp.SetPath(p.KIID_PATH('/'+root_uuid+'/'+c.findtext('tstamps')))
 b.Add(fp); x,y,angle=coords[ref]; fp.SetPosition(vec(x,y)); fp.SetOrientationDegrees(angle)
 fp.Value().SetVisible(False)
 fp.Reference().SetTextSize(vec(1,1)); fp.Reference().SetTextThickness(mm(.15))
 # Short references outside solder lands, not on component bodies.
 if ref.startswith('R'): fp.Reference().SetPosition(vec(x-3.6,y)); fp.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
 if ref.startswith('TP'): fp.Reference().SetPosition(vec(x,y-2))
 for pad in fp.Pads():
  net=net_by_pad.get((ref,pad.GetNumber()))
  if net: pad.SetNet(net)
 placements.append({'reference':ref,'x_mm':x,'y_mm':y,'rotation_deg':angle,'footprint':c.findtext('footprint')})
def line(x1,y1,x2,y2,layer=p.Edge_Cuts):
 s=p.PCB_SHAPE(); s.SetShape(p.SHAPE_T_SEGMENT); s.SetStart(vec(x1,y1)); s.SetEnd(vec(x2,y2)); s.SetLayer(layer); s.SetWidth(mm(.1)); b.Add(s)
def box(x1,y1,x2,y2,layer):
 for a in [(x1,y1,x2,y1),(x2,y1,x2,y2),(x2,y2,x1,y2),(x1,y2,x1,y1)]: line(*a,layer)
def text(value,x,y,size=1,layer=p.F_SilkS):
 t=p.PCB_TEXT(b); t.SetText(value); t.SetPosition(vec(x,y)); t.SetTextSize(vec(max(1,size),max(1,size))); t.SetTextThickness(mm(.15)); t.SetLayer(layer); b.Add(t)
def keepout(name,x1,y1,x2,y2,copper=True,footprints=True):
 z=p.ZONE(b); z.SetIsRuleArea(True); z.SetZoneName(name)
 layers=p.LSET()
 for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]: layers.AddLayer(layer)
 z.SetLayerSet(layers); z.SetDoNotAllowTracks(copper); z.SetDoNotAllowVias(copper); z.SetDoNotAllowPads(copper and not name.startswith('H')); z.SetDoNotAllowZoneFills(copper); z.SetDoNotAllowFootprints(footprints)
 poly=z.Outline(); poly.NewOutline()
 for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]: poly.Append(mm(x),mm(y))
 b.Add(z)
box(0,0,100,100,p.Edge_Cuts)
# Mechanical-only holes: deliberately no schematic electrical component.
for i,(x,y) in enumerate([(5,5),(95,5),(5,95),(95,95)],1):
 fp=p.FootprintLoad(str(LIB/'MountingHole.pretty'),'MountingHole_3.2mm_M3')
 fp.SetFPID(p.LIB_ID('MountingHole','MountingHole_3.2mm_M3')); fp.SetReference(f'H{i}'); fp.SetValue('M3 / 14mm foot'); b.Add(fp); fp.SetPosition(vec(x,y)); fp.Value().SetVisible(False)
 fp.Reference().SetPosition(vec(x,9.8 if y==5 else 90.2))
 fp.SetAttributes(fp.GetAttributes() | p.FP_EXCLUDE_FROM_BOM | p.FP_EXCLUDE_FROM_POS_FILES)
 # NPTH pad allowed; tracks/vias/zones barred. Copper-pad clearance checked separately.
 keepout(f'H{i}_SCREW_CLEARANCE',x-4,y-4,x+4,y+4,True,False)
 circle=p.PCB_SHAPE(); circle.SetShape(p.SHAPE_T_CIRCLE); circle.SetCenter(vec(x,y)); circle.SetEnd(vec(x+1.6,y)); circle.SetLayer(p.Dwgs_User); circle.SetWidth(mm(.15)); b.Add(circle)
# Official WeAct dimensions; longitudinal pad-to-outline offset read from drawing, pending as-built check.
keepout('WEACT_ANTENNA_ALL_COPPER_KEEP_OUT',59.97,32.595,81.97,39.635,True,True)
keepout('WEACT_UNDERSIDE_NO_COMPONENTS',59,39.635,82.94,100,False,True)
box(55.349,39.635,86.591,102.391,p.Dwgs_User)
box(61.9615,33.595,79.9785,39.635,p.Dwgs_User)
text('WEACT N16R2 / 22 PINS',71,56,1,p.Dwgs_User)
text('ANTENNA / RF DISABLED',71,36,.9,p.Dwgs_User)
text('USB UART / CABLE EXIT BELOW PCB',71,98,.8,p.Dwgs_User)
text('CARTRIDGE ACCESS / VERIFY',51,12,1,p.Dwgs_User)
text('GBA ONLY / 3.3V',49,3.5,1.3)
text('V1 PLACEMENT / UNROUTED',27,54,.9)
text('WR ENABLE',31,68,1)
text('DEFAULT OPEN',32,65.5,1)
text('POWER LINK',20,43,1)
text('NORMALLY CLOSED',21,45.5,1)
text('REMOVE USB FIRST',24,56,.8)
text('UART TO PC / USB UNUSED',71,90,1,p.Dwgs_User)

for c in xml.findall('.//components/comp'):
 ref=c.attrib['ref']
 if ref.startswith('TP'):
  x,y,_=coords[ref]; text(c.findtext('value'),x,y+2,.8)
p.SaveBoard(str(OUT),b)
(ROOT/'hardware/verification/placement.json').write_text(json.dumps({'board_mm':[100,100],'copper_layers':4,'routed':False,'components':placements,'mounting_holes_mm':[[5,5],[95,5],[5,95],[95,95]],'mechanical_envelope':'OFFICIAL_WEACT_PDF_DIMENSIONS_USB_SIDE_ORIGIN_PENDING_AS_BUILT_CHECK'},indent=2)+'\n')
print(f'Saved {OUT}: {len(placements)} schematic footprints + 4 mechanical holes, 4 layers, no routing')
