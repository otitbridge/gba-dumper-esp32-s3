"""Generate the logical design and BOM from explicit part selections."""
from pathlib import Path
import json, csv, uuid
ROOT=Path(__file__).resolve().parents[1]
def write(p,s): (ROOT/p).write_text(s)
_uid_counter=0
def uid():
 global _uid_counter
 _uid_counter+=1
 return str(uuid.uuid5(uuid.NAMESPACE_URL,f'WEACT_ESP32S3_A_N16R2_GBA_V1_20260928/{_uid_counter}'))
def q(s): return json.dumps(str(s),ensure_ascii=False)
AD=[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,21]
AH=[1,35,36,38,39,40,41,42]
left=['3V3','3V3','EN',4,5,6,7,15,16,17,18,8,3,46,9,10,11,12,13,14,'5V','GND']
right=['GND',43,44,1,2,42,41,40,39,38,37,36,35,0,45,48,47,21,20,19,'GND','GND']
rows=[]
for i,g in enumerate(AD): rows.append(dict(signal=f'AD{i}',gpio=g,cart_pin=i+6,resistor=f'R{i+1}',ohms=330))
for i,g in enumerate(AH): rows.append(dict(signal=f'A{i+16}_D{i}',gpio=g,cart_pin=i+22,resistor=f'R{i+17}',ohms=330))
for i,(s,g,p) in enumerate([('nCS',47,5),('nRD',2,4),('nWR',37,3),('nCS2',3,30)]): rows.append(dict(signal=s,gpio=g,cart_pin=p,resistor=f'R{i+25}',ohms=100))
for r in rows:
 for j,arr in [('J1',left),('J2',right)]:
  if r['gpio'] in arr: r.update(socket=j,socket_pin=arr.index(r['gpio'])+1)
write('hardware/pinmap.json',json.dumps({'id':'WEACT_ESP32S3_A_N16R2_GBA_V1_20260928','signals':rows},indent=2)+'\n')
bygpio={r['gpio']:r for r in rows}
cart={r['cart_pin']:r['signal'] for r in rows}; cart.update({1:'3V3',2:'PHI',31:'nREQ',32:'GND'})
pintext='# GPIO・ソケット配線正本\n\n識別子: `WEACT_ESP32S3_A_N16R2_GBA_V1_20260928`。実機未検証。\n\nJ1/J2は部品面、アンテナ上・USB下で左/右、上から1–22。\n\n|GBA端子|信号|GPIO|ソケット|直列抵抗|\n|---:|---|---:|---|---|\n'
for p in range(1,33):
 r=next((r for r in rows if r['cart_pin']==p),None)
 pintext+=f'|{p}|{cart[p]}|{r["gpio"] if r else "—"}|{r["socket"]+"-"+str(r["socket_pin"]) if r else {1:"J1-1 → JP2",32:"J2-22 (共通GND)"}.get(p,"TPのみ" if p==31 else "R33 → GND + TP")}|{r["resistor"]+" / "+str(r["ohms"])+" Ω" if r else "—"}|\n'
pintext+='\n|位置|J1|J2|\n|---:|---|---|\n'
for i,(a,b) in enumerate(zip(left,right),1): pintext+=f'|{i}|{a if isinstance(a,str) else "GPIO"+str(a)}|{b if isinstance(b,str) else "GPIO"+str(b)}|\n'
pintext+='\nGPIO0/19/20/43/44/45/46/48、EN、5Vは親基板でNC。UART0はWeAct上のCH343に接続されたまま。/WRはR27→JP1→CART_nWR、R31はJP1よりカートリッジ側。/CS2プルアップはJP2装着時のみ給電される。\n'
write('docs/pinmap.md',pintext)
write('firmware/main/pinmap.hpp','''#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
namespace gba_pins {
inline constexpr char ID[] = "WEACT_ESP32S3_A_N16R2_GBA_V1_20260928";
inline constexpr std::array<int,16> AD = {'''+','.join(map(str,AD))+'''};
inline constexpr std::array<int,8> AH = {'''+','.join(map(str,AH))+'''};
inline constexpr int NCS=47, NRD=2, NWR=37, NCS2=3;
inline constexpr int UART_TX=43, UART_RX=44;
inline constexpr std::array<int,4> CTRL={NCS,NRD,NWR,NCS2};
constexpr std::uint64_t bit(int gpio) { return std::uint64_t{1} << gpio; }
template<std::size_t N> constexpr std::uint64_t mask(const std::array<int,N>& pins) {
    std::uint64_t v=0; for(int p:pins) v |= bit(p); return v;
}
constexpr unsigned popcount(std::uint64_t v) {
    unsigned n=0; while(v) { n += unsigned(v&1U); v >>= 1U; } return n;
}
inline constexpr auto AD_MASK=mask(AD), AH_MASK=mask(AH), CTRL_MASK=mask(CTRL);
inline constexpr auto ALL_MASK=AD_MASK|AH_MASK|CTRL_MASK;
inline constexpr auto FORBIDDEN_MASK=bit(0)|bit(19)|bit(20)|bit(48)|bit(43)|bit(44)|bit(45)|bit(46);
static_assert(popcount(AD_MASK)==16 && popcount(AH_MASK)==8 && popcount(CTRL_MASK)==4);
static_assert(popcount(ALL_MASK)==28,"Duplicate GPIO assignment");
static_assert((ALL_MASK & FORBIDDEN_MASK)==0,"Reserved GPIO used");
static_assert((AD_MASK >> 32U)==0,"AD must stay in bank 0");
static_assert(((AD_MASK|AH_MASK)&(bit(2)|bit(3)|bit(37)))==0);
}
''')
# Native KiCad schematic with embedded, passive connector models. External board electronics are not modeled.
parts=json.loads((ROOT/'hardware/bom/selected_parts.json').read_text())
manual_parts=json.loads((ROOT/'hardware/bom/manual_parts.json').read_text())
selected={ref:part for part in parts+manual_parts for ref in part['refs']}
rootid=uid(); lib=[]; body=[]; expected={}; bom=[]
def font(size=1): return f'(effects (font (size {size} {size})))'
def symbol_def(name,pins,shape):
 s=f'(symbol "GBA:{name}" (pin_names (offset 0.8)) (in_bom yes) (on_board yes) (property "Reference" "X" (at 0 0 0) {font()}) (property "Value" "{name}" (at 0 -3 0) {font()}) (symbol "{name}_0_1" {shape}) (symbol "{name}_1_1" '
 for n,label,x,y,angle,length in pins:
  s+=f'(pin passive line (at {x} {y} {angle}) (length {length}) (name {q(label)} {font(0.9)}) (number "{n}" {font(0.9)}))'
 lib.append(s+'))')
 return pins
def rectangle(x1,y1,x2,y2): return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type default)) (fill (type background)))'
# Pins extend to the left; y in symbol coordinates is inverted when placed.
sockets={}
for name,arr in [('WEACT_LEFT',left),('WEACT_RIGHT',right),('GBA_SLOT',[cart[i] for i in range(1,33)])]:
 pins=[(i+1,str(a) if isinstance(a,str) else f'GPIO{a}',-5.08,-i*5.08,0,5.08) for i,a in enumerate(arr)]
 sockets[name]=symbol_def(name,pins,rectangle(0,3,23,-(len(arr)-1)*5.08-3))
res=symbol_def('R',[(1,'~',-5.08,0,0,3.08),(2,'~',5.08,0,180,3.08)],rectangle(-2,1,2,-1))
cap=symbol_def('C',[(1,'~',-5.08,0,0,4.58),(2,'~',5.08,0,180,4.58)],'(polyline (pts (xy -0.5 -2) (xy -0.5 2)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.5 -2) (xy 0.5 2)) (stroke (width 0.254) (type default)) (fill (type none)))')
jump=symbol_def('JUMPER',[(1,'~',-5.08,0,0,3.08),(2,'~',5.08,0,180,3.08)],rectangle(-2,1.5,2,-1.5))
tp=symbol_def('TP',[(1,'~',0,0,90,2.54)],'(circle (center 0 3.54) (radius 1) (stroke (width 0.254) (type default)) (fill (type none)))')
def label(net,x,y,angle=0):
 body.append(f'(label {q(net)} (at {x} {y} {angle}) {font(0.95)[:-1]} (justify left bottom)) (uuid "{uid()}"))')
def place(name,pins,ref,value,x,y,nets,footprint=''):
 part=selected.get(ref)
 if part: footprint=part['footprint']
 x=round(round(x/1.27)*1.27,4); y=round(round(y/1.27)*1.27,4)
 ident=uid()
 tx=x+10 if name=='TP' else x
 props=f'(property "Reference" "{ref}" (at {tx} {y-3} 0) {font(1.1)}) (property "Value" {q(value)} (at {tx} {y-5} 0) {font(1)}) (property "Footprint" {q(footprint)} (at {x} {y} 0) (effects (font (size 1 1)) (hide yes)))'
 if part:
  for key,val in [('Manufacturer',part['manufacturer']),('MPN',part['mpn']),('LCSC',part['lcsc']),('Assembly',part['classification']),('Rating',part['rating']),('Supplier',part.get('supplier','JLCPCB')),('Supplier Code',part.get('supplier_code',part['lcsc']))]:
   props+=f'(property {q(key)} {q(val)} (at {x} {y} 0) (effects (font (size 1 1)) (hide yes)))'
 body.append(f'(symbol (lib_id "GBA:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{ident}") {props} '+''.join(f'(pin "{p[0]}" (uuid "{uid()}"))' for p in pins)+f'(instances (project "gba_dumper" (path "/{rootid}" (reference "{ref}") (unit 1)))))')
 bom.append([ref,value,footprint,part.get('status','SELECTED_NOT_BENCH_VERIFIED') if part else 'FOOTPRINT_APPROVED_BY_USER' if ref=='J3' else 'PCB_FEATURE_NO_PURCHASE' if ref.startswith('TP') else 'UNVERIFIED',part['mpn'] if part else '',part['lcsc'] if part else '',part['rating'] if part else '',part['source'] if part else '',part.get('supplier','JLCPCB') if part else '',part.get('supplier_code',part['lcsc']) if part else ''])
 for p,net in zip(pins,nets):
  n,_,px,py,_,_=p; px+=x; py=y-py
  if net is None:
   body.append(f'(no_connect (at {px} {py}) (uuid "{uid()}"))'); continue
  # Short lead + label at its far end, never text-only connectivity.
  dx=-7.62 if p[2]<=0 else 7.62
  ex=round(px+dx,4)
  body.append(f'(wire (pts (xy {px} {py}) (xy {ex} {py})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
  label(net,ex,py,180 if dx<0 else 0)
  expected.setdefault(net,[]).append([ref,str(n)])
def note(t,x,y,size=1.5): body.append(f'(text {q(t)} (at {x} {y} 0) {font(size)[:-1]} (justify left bottom)) (uuid "{uid()}"))')
note('WEACT N16R2 GBA DIRECT V1 / LOGICAL SCHEMATIC / NOT FOR FABRICATION',20,19,2.5)
note('WEACT_ESP32S3_A_N16R2_GBA_V1_20260928 | Unmodified ESP32S3-A N16R2 ONLY | GPIO19/20/48 NOT ON GBA BUS',20,26)
note('SOCKET VIEW: component side, antenna UP, USB DOWN; top pin = 1. All footprints require physical verification.',20,33)
for name,arr,ref,x in [('WEACT_LEFT',left,'J1',58),('WEACT_RIGHT',right,'J2',132)]:
 nets=[]
 for a in arr:
  nets.append('BOARD_3V3' if a=='3V3' else 'GND' if a=='GND' else 'MCU_'+bygpio[a]['signal'] if a in bygpio else None)
 place(name,sockets[name],ref,name,x,50,nets,footprint="GBA_Mechanical:PinSocket_1x22_P2.54mm_D1.02mm")
place('GBA_SLOT',sockets['GBA_SLOT'],'J3','GBA_32_LOGICAL_PINS',490,50,['GND' if cart[p]=='GND' else 'CART_'+cart[p] for p in range(1,33)],footprint='Gekkio_Connector_PCBEdge:GameBoy_Cartridge_AGB_1x32_P1.50mm_Socket_Horizontal')
for i,r in enumerate(rows):
 x=230 if i<16 else 365; y=50+(i if i<16 else i-16)*10.16
 place('R',res,r['resistor'],str(r['ohms']),x,y,['MCU_'+r['signal'],'WR_LINK' if r['signal']=='nWR' else 'CART_'+r['signal']])
note('R1-R33, C1-C2: 0805 / JLCPCB Basic selected / electrical validation pending',188,218)
place('JUMPER',jump,'JP1','WR ENABLE / DEFAULT OPEN',365,188,['WR_LINK','CART_nWR'])
for i,s in enumerate(['nCS','nRD','nWR','nCS2']): place('R',res,f'R{29+i}','10k',80+i*110,246,['CART_3V3','CART_'+s])
note('CONTROL PULLUPS: cartridge side; R31 after JP1. GPIO3 strap HIGH requires JP2 installed and common power.',20,262)
place('JUMPER',jump,'JP2','POWER LINK / DEFAULT CLOSED',80,280,['BOARD_3V3','CART_3V3'])
place('C',cap,'C1','100nF',200,280,['CART_3V3','GND'])
place('C',cap,'C2','10uF',310,280,['CART_3V3','GND'])
place('R',res,'R33','10k / PHI pulldown',440,280,['CART_PHI','GND'])
note('GBA ONLY / 3.3V | JP1/JP2 and cartridge: REMOVE USB FIRST | PC: UART connector only; native USB not used',20,303)
note('Power source: WeAct J1-1/2. Regulator capability unverified. No external supply in parallel. No 5V cartridge connection.',20,311)
for i,s in enumerate(['3V3','GND','nCS','nRD','nWR','nCS2','AD0','AD15','A16_D0','A23_D7','PHI','nREQ']):
 place('TP',tp,f'TP{i+1}',s,40+(i%6)*85,335+(i//6)*25,['GND' if s=='GND' else 'CART_'+s],footprint='GBA_Mechanical:TestPoint_Pad_D2.0mm')
note('/REQ: test point ONLY; no GPIO, no ground short. PHI: R33 to GND. USB-UART through on-board CH343 only.',20,380)
note('ERC scope: passive carrier interconnect only. WeAct power/strap circuits, boot behavior and signal integrity need bench tests.',20,388)
write('hardware/gba_dumper.kicad_sch',f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{rootid}") (paper "A2") (lib_symbols '+''.join(lib)+')'+''.join(body)+f'(sheet_instances (path "/" (page "1"))))\n')
write('hardware/lib/GBA.kicad_sym','(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor") '+''.join(s.replace('"GBA:','"') for s in lib)+')\n')
write('hardware/sym-lib-table','(sym_lib_table (version 7) (lib (name "GBA")(type "KiCad")(uri "${KIPRJMOD}/lib/GBA.kicad_sym")(options "")(descr "Logical passive carrier symbols; no footprints")))\n')
# Preserve KiCad board rules and settings once placement exists.
if not (ROOT/'hardware/gba_dumper.kicad_pro').exists():
 write('hardware/gba_dumper.kicad_pro',json.dumps({'meta':{'filename':'gba_dumper.kicad_pro','version':1}},indent=2)+'\n')
write('hardware/verification/expected_nets.json',json.dumps(expected,indent=2)+'\n')
with (ROOT/'hardware/bom/preliminary.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n"); w.writerow(['Reference','Value','Footprint','Status','MPN','LCSC Part Number','Rating','Source','Supplier','Supplier Code']); w.writerows(bom)
print(f'Generated {len(rows)} GPIO assignments, {len(bom)} components, {len(expected)} nets')

with (ROOT/'hardware/bom/jlcpcb_pcba.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n")
 w.writerow(['Comment','Designator','Footprint','LCSC Part Number'])
 for part in parts:
  w.writerow([part['value'],','.join(part['refs']),part['footprint'].split(':')[1],part['lcsc']])

with (ROOT/'hardware/bom/akizuki_jumpers.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n")
 w.writerow(['Usage','MPN','Akizuki Code','Quantity per board','Pack Quantity','Source'])
 for part in manual_parts:
  if not (set(part['refs']) & {'JP1','JP2'} or part['mpn']=='2228GG'): continue
  w.writerow([','.join(part['refs']) or part['usage'],part['mpn'],part['supplier_code'],part['quantity'],part['pack_quantity'],part['source']])

# Procurement includes accessories; board features remain in the logical BOM only.
with (ROOT/'hardware/bom/assembly_parts.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n")
 w.writerow(['Usage','MPN','Supplier','Supplier Code','Quantity per board','Pack Quantity','Source','Status'])
 for p in manual_parts+json.loads((ROOT/'hardware/bom/accessories.json').read_text()):
  w.writerow([p.get('usage') or ','.join(p.get('refs',[])),p['mpn'],p['supplier'],p['supplier_code'],p['quantity'],p['pack_quantity'],p['source'],p.get('status','SELECTED_NOT_BENCH_VERIFIED')])
