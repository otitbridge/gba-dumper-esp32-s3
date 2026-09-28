"""Read exported files with Gerbonara 1.6.3; compare with the native-PCB snapshot."""
from pathlib import Path
import json,csv,collections,hashlib,zipfile,subprocess
from gerbonara import GerberFile,ExcellonFile,LayerStack
from gerbonara.graphic_objects import Flash,Line
r=Path(__file__).resolve().parents[1];out=r/'output/fabrication_review';folder=out/'gerbers'
expected=json.loads((out/'review/expected_from_pcb.json').read_text())
assert expected['source_sha256']==hashlib.sha256((r/'hardware/gba_dumper.kicad_pcb').read_bytes()).hexdigest()
def canon(row):return tuple(round(v,5) if isinstance(v,(int,float)) else v for v in row)
parsed={}
for kind in ['PTH','NPTH']:
 g=ExcellonFile.open(folder/f'gba_dumper-{kind}.drl');actual=[]
 for o in g.objects:
  if isinstance(o,Flash):actual.append(['circle',o.x,o.y,o.aperture.diameter])
  else:
   assert isinstance(o,Line)
   a,c=sorted([(o.x1,o.y1),(o.x2,o.y2)])
   actual.append(['slot',*a,*c,o.aperture.diameter])
 # KiCad decimal-mm Excellon output quantizes coordinates to 0.001 mm.
 remaining=list(expected['drills'][kind])
 for hole in actual:
  matches=[i for i,want in enumerate(remaining) if hole[0]==want[0] and len(hole)==len(want) and all(abs(a-b)<=0.000501 for a,b in zip(hole[1:],want[1:]))]
  assert len(matches)==1,(kind,hole,matches)
  remaining.pop(matches[0])
 assert not remaining,(kind,remaining)
 parsed[kind]=len(actual)
outline=GerberFile.open(folder/'gba_dumper-Edge_Cuts.gm1')
assert len(outline.objects)==4 and all(isinstance(o,Line) for o in outline.objects)
segments={frozenset([canon((o.x1,o.y1)),canon((o.x2,o.y2))]) for o in outline.objects}
corners=[(0,0),(100,0),(100,-100),(0,-100)]
assert segments=={frozenset([corners[i],corners[(i+1)%4]]) for i in range(4)}
paste=GerberFile.open(folder/'gba_dumper-F_Paste.gtp')
boxes=[]
for obj in paste.objects:
 (x1,y1),(x2,y2)=obj.bounding_box();boxes.append([x1,y1,x2,y2]);assert obj.polarity_dark
assert collections.Counter(map(canon,boxes))==collections.Counter(map(canon,expected['top_paste_pad_bboxes']))
assert len(boxes)==70
assert not GerberFile.open(folder/'gba_dumper-B_Paste.gbp').objects
stack=LayerStack.open(folder)
assert len([k for k in stack.graphic_layers if k[1]=='copper'])==4
for key in [('top','copper'),('inner_1','copper'),('inner_2','copper'),('bottom','copper')]:assert len(stack.graphic_layers[key].objects)>0
with (out/'assembly/jlcpcb_cpl.csv').open() as f:cpl=list(csv.DictReader(f))
with (out/'assembly/jlcpcb_bom.csv').open() as f:bom=list(csv.DictReader(f))
assert len(cpl)==35 and len(bom)==5
refs=[row['Designator'] for row in cpl];assert len(set(refs))==35
assert set(refs)==set(expected['pcba_refs'])=={v for row in bom for v in row['Designator'].split(',')}
assert all(row['Layer']=='Top' and float(row['Rotation'])==0 for row in cpl)
# Compare CPL centroid with pair of exported paste apertures (non-polar 0805).
for row in cpl:
 x=float(row['Mid X'].removesuffix('mm'));y=float(row['Mid Y'].removesuffix('mm'))
 pair=[z for z in boxes if abs((z[1]+z[3])/2-y)<1e-5 and abs((z[0]+z[2])/2-x)<1.01]
 assert len(pair)==2,row
 assert abs(sum((z[0]+z[2])/2 for z in pair)/2-x)<1e-5
 assert abs(sum((z[1]+z[3])/2 for z in pair)/2-y)<1e-5
result={'parser':'Gerbonara 1.6.3','source_sha256':expected['source_sha256'],'copper_layers':4,'outline_mm':[100,100],'drill_coordinate_tolerance_mm':0.000501,'drill_objects':parsed,'npth_detail':'4 x 3.2mm round mounting holes + 2 x 1.6mm by 4.6mm slots','top_paste_apertures':70,'bottom_paste_apertures':0,'cpl_components':35,'bom_part_numbers':5,'all_coordinates_drills_centroids_matched':True,'manufacturing_approved':False,'parser_notes':['Gerbonara warns KiCad G90 appears after header; decimal-mm absolute coordinates and all hole/slot geometry were independently matched.']}
(out/'review/verification.json').write_text(json.dumps(result,indent=2)+'\n')
with zipfile.ZipFile(out/'gba_dumper_gerbers_REVIEW_ONLY.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(folder.iterdir()):z.write(path,path.name)
manifest={'status':'REVIEW_ONLY_NOT_APPROVED_FOR_MANUFACTURE','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'source_board_sha256':expected['source_sha256'],'files':{str(path.relative_to(out)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(out.rglob('*')) if path.is_file() and path.name!='manifest.json'}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PASS: 4 copper layers; 100mm outline; 139 PTH + 6 NPTH; 70 paste pads; 35 CPL centroids/rotations; BOM match. Review ZIP created.')
