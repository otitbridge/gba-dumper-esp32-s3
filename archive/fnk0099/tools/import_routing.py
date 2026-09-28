"""Import local SES into prepared copy and add an In1.Cu GND plane."""
from pathlib import Path
import pcbnew as p,shutil
r=Path(__file__).resolve().parents[1];work=r/'tmp/routing'
b=p.LoadBoard(str(work/'prepared.kicad_pcb'))
assert p.ImportSpecctraSES(b,str(work/'route.ses'))
assert not [t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.In1_Cu]
z=p.ZONE(b);z.SetLayer(p.In1_Cu);z.SetNet(b.FindNet('/GND'));z.SetZoneName('GND_CONTINUOUS_IN1')
z.SetLocalClearance(p.FromMM(.35));z.SetMinThickness(p.FromMM(.25));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetThermalReliefGap(p.FromMM(.3));z.SetThermalReliefSpokeWidth(p.FromMM(.5))
poly=z.Outline();poly.NewOutline()
for x,y in [(0.5,0.5),(99.5,0.5),(99.5,99.5),(0.5,99.5)]:poly.Append(p.FromMM(x),p.FromMM(y))
b.Add(z)
p.SaveBoard(str(work/'routed.kicad_pcb'),b)
for ext in ['kicad_pro','kicad_dru']: shutil.copyfile(r/f'hardware/gba_dumper.{ext}',work/f'routed.{ext}')
print('Imported routing; added GND plane; source board preserved until validation')
