"""Render native PCB track geometry for AD6, with identical board scale/orientation.
KiCad Python creates SVG; rasterize with sharp using the command in the output README.
"""
from pathlib import Path
import html,json,math
import pcbnew as p
r=Path(__file__).resolve().parents[1];out=r/'output/pcb/ad6_comparison';out.mkdir(parents=True,exist_ok=True)
report=json.loads((r/'hardware/verification/ad6_reroute/comparison_before.json').read_text())
colors={p.F_Cu:'#d62728',p.In2_Cu:'#c47500',p.B_Cu:'#1565c0'}
nets={'/MCU_AD6','/CART_AD6'}
def pt(v):return (p.ToMM(v.x),p.ToMM(v.y))
def line(a,b,color,width,extra=''):return f'<line x1="{a[0]:.5f}" y1="{a[1]:.5f}" x2="{b[0]:.5f}" y2="{b[1]:.5f}" stroke="{color}" stroke-width="{width}" {extra}/>'
def label(s,x,y,size=1.65,anchor='start',color='#14213d'):
 return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-family="Arial,sans-serif">{html.escape(s)}</text>'
def render(key,path,title):
 b=p.LoadBoard(str(path));parts=[]
 parts.append('<rect x="-5" y="-15" width="110" height="136" fill="white"/>')
 parts.append(label(title,0,-10,3.0))
 d=report[key]['signal_paths']['AD6'];length=d['path_mm']
 parts.append(label(f'AD6 main path: {length:.2f} mm | top view | 100 x 100 mm',0,-6,1.8))
 parts.append('<rect x="0" y="0" width="100" height="100" fill="#fbfcfe" stroke="#334155" stroke-width="0.3"/>')
 # Background tracks/pads provide exact PCB context without obscuring AD6.
 for t in b.GetTracks():
  if not isinstance(t,p.PCB_VIA):parts.append(line(pt(t.GetStart()),pt(t.GetEnd()),'#dce1e8',max(.08,p.ToMM(t.GetWidth())*.55)))
 for f in b.GetFootprints():
  for pad in f.Pads():
   x,y=pt(pad.GetPosition());size=pt(pad.GetSize())
   parts.append(f'<ellipse cx="{x}" cy="{y}" rx="{size[0]/2}" ry="{size[1]/2}" fill="#eef1f6" stroke="#c3cad4" stroke-width="0.10"/>')
 # Minimal component outlines are read from actual footprint bounds.
 fps={f.GetReference():f for f in b.GetFootprints()}
 for ref in ['J1','J2','J3']:
  f=fps[ref];bb=f.GetBoundingBox(False,False)
  x,y,w,h=[p.ToMM(v) for v in [bb.GetLeft(),bb.GetTop(),bb.GetWidth(),bb.GetHeight()]]
  parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#a6aebc" stroke-width="0.16"/>')
  parts.append(label(ref,x,y-1,1.9))
 for t in b.GetTracks():
  if t.GetNetname() in nets and not isinstance(t,p.PCB_VIA):
   parts.append(line(pt(t.GetStart()),pt(t.GetEnd()),colors[t.GetLayer()],.55,'stroke-linecap="round"'))
 via_count=0
 for t in b.GetTracks():
  if t.GetNetname() in nets and isinstance(t,p.PCB_VIA):
   x,y=pt(t.GetPosition());via_count+=1
   parts.append(f'<circle cx="{x}" cy="{y}" r="0.58" fill="white" stroke="#14213d" stroke-width=".22"/>')
 # Relevant pads and visible R7 bridge (component body is excluded from length).
 starts=d['segments'][0]['from'];end=['J3','12']
 endpoints=[tuple(starts),('R7','1'),('R7','2'),tuple(end)]
 for ref,n in endpoints:
  x,y=pt(fps[ref].FindPadByNumber(n).GetPosition())
  parts.append(f'<circle cx="{x}" cy="{y}" r="0.70" fill="#ffe082" stroke="#14213d" stroke-width=".20"/>')
 a=pt(fps['R7'].FindPadByNumber('1').GetPosition());c=pt(fps['R7'].FindPadByNumber('2').GetPosition())
 parts.append(line(a,c,'#14213d',.35,'stroke-dasharray=".5 .4"'))
 source=pt(fps[starts[0]].FindPadByNumber(starts[1]).GetPosition());cart=pt(fps['J3'].FindPadByNumber('12').GetPosition())
 parts.append(line(source,(65,84),'#14213d',.15));parts.append(label(f'GPIO10 / {starts[0]}-{starts[1]}',65.5,84.4,1.8))
 parts.append(line(a,(28,60),'#14213d',.15));parts.append(label('R7 / 330 ohm',17,59.4,1.8))
 parts.append(line(cart,(42,18),'#14213d',.15));parts.append(label('GBA AD6 / J3-12',42,16.5,1.8,'middle'))
 parts.append(label(f'MCU -> R7: {d["segments"][0]["track_path_mm"]:.2f} mm',0,105,1.8))
 parts.append(label(f'R7 -> cartridge: {d["segments"][1]["track_path_mm"]:.2f} mm | vias: {via_count}',0,108,1.8))
 for x,(layer,text) in zip([0,30,62],[(p.F_Cu,'F.Cu (top)'),(p.In2_Cu,'In2.Cu (inner)'),(p.B_Cu,'B.Cu (bottom)')]):
  parts.append(line((x,112),(x+5,112),colors[layer],.55));parts.append(label(text,x+6,112.6,1.6))
 parts.append(label('Colored: full AD6 nets. Circles: vias. Dashed: R7 body.',0,116,1.45))
 parts.append(label('Lengths exclude pad interiors, resistor body and via barrels.',0,119,1.45))
 return ''.join(parts)
before=render('fnk0099',r/'archive/fnk0099/gba_dumper.kicad_pcb','BEFORE / FNK0099 N16R8')
after=render('weact',r/'hardware/verification/ad6_reroute/before.kicad_pcb','AFTER / WeAct ESP32S3-A N16R2')
for name,body in [('before_fnk0099',before),('after_weact',after)]:
 (out/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="1360" viewBox="-5 -15 110 136">{body}</svg>\n')
(out/'comparison.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="1360" viewBox="-5 -15 220 136">{before}<g transform="translate(110 0)">{after}</g></svg>\n')
(out/'README.md').write_text('''# AD6経路比較

変更前はarchive/fnk0099/gba_dumper.kicad_pcb、変更後はhardware/gba_dumper.kicad_pcb。上面視・同一縮尺。基板輪郭は100 mm角。全配線を薄灰色、AD6のMCU側とカートリッジ側を層別の色で強調。丸枠はビア、黄色丸は接続パッド、R7両端の破線は抵抗本体。

- before_fnk0099.png: 変更前
- after_weact.png: 変更後
- comparison.png: 左右比較

図の強調はAD6ネット全体（小さな枝も含む）。表示長は比較資料と同じ最短の主経路で、パッド内部・抵抗内部・ビア垂直長は除く。FNKは65.33 mm、WeActは83.23 mm。WeActの全トラック合計は83.32 mmで、主経路との差は約0.09 mm。層間の移動は丸枠で追える。実際のKiCadトラック座標から描画し、線の視認性を上げるため描画幅のみ強調している。基板や配線は変更していない。

再生成: KiCad同梱Pythonでtools/render_ad6_comparison.pyを実行し、SVGをNode sharpでPNGへラスタライズする。
''')
print(out)
