"""Independent checks against the WeAct official ESP32S3-A header table and approved migration."""
from pathlib import Path
import json, re, xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[2]
rows=json.loads((root/'hardware/pinmap.json').read_text())['signals']
gpios=[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,21,1,35,36,38,39,40,41,42,47,2,37,3]
pads=[('J1',p) for p in [4,5,6,7,12,15,16,17,18,19,20,8,9,10,11]]+[('J2',18)]+[('J2',p) for p in [4,13,12,10,9,8,7,6,17,5,11]]+[('J1',13)]
assert [r['gpio'] for r in rows]==gpios
assert [(r['socket'],r['socket_pin']) for r in rows]==pads
assert [r['cart_pin'] for r in rows]==list(range(6,30))+[5,4,3,30]
assert len(set(gpios))==28
assert not set(gpios)&{0,19,20,43,44,45,46,48}
header=(root/'firmware/main/pinmap.hpp').read_text()
for name,want in [('AD',gpios[:16]),('AH',gpios[16:24])]:
 actual=list(map(int,re.search(r'\b'+name+r'\s*=\s*\{([^}]+)',header)[1].split(',')))
 assert actual==want
for name,want in [('NCS',47),('NRD',2),('NWR',37),('NCS2',3),('UART_TX',43),('UART_RX',44)]:
 assert int(re.search(r'\b'+name+r'\s*=\s*(\d+)',header)[1])==want
xml=ET.parse(root/'hardware/verification/gba_dumper.xml')
nets={n.attrib['name'].lstrip('/'): {(p.attrib['ref'],p.attrib['pin']) for p in n.findall('node')} for n in xml.findall('.//nets/net')}
expected={k:set(map(tuple,v)) for k,v in json.loads((root/'hardware/verification/expected_nets.json').read_text()).items()}
for net,nodes in expected.items(): assert nets[net]==nodes,(net,nets[net],nodes)
# Independently enforce the entire signal chain, not just the generated expectation file.
for i,r in enumerate(rows):
 ref=f'R{i+1}'; s=r['signal']; cartpin=str(r['cart_pin'])
 assert nets['MCU_'+s]=={(r['socket'],str(r['socket_pin'])),(ref,'1')}
 cartnodes=nets['CART_'+s]
 assert ('J3',cartpin) in cartnodes
 assert (('JP1','2') if s=='nWR' else (ref,'2')) in cartnodes
 assert nets['WR_LINK']=={('R27','2'),('JP1','1')}
for ref,s in zip(range(29,33),['nCS','nRD','nWR','nCS2']):
 assert (f'R{ref}','1') in nets['CART_3V3'] and (f'R{ref}','2') in nets['CART_'+s]
assert nets['BOARD_3V3']=={('J1','1'),('J1','2'),('JP2','1')}
assert nets['CART_3V3']=={('JP2','2'),('J3','1'),('C1','1'),('C2','1'),('TP1','1')}|{(f'R{i}','1') for i in range(29,33)}
assert nets['CART_nREQ']=={('J3','31'),('TP12','1')}
assert nets['CART_PHI']=={('J3','2'),('R33','1'),('TP11','1')}
assert nets['GND']=={('J1','22'),('J2','1'),('J2','21'),('J2','22'),('J3','32'),('C1','2'),('C2','2'),('R33','2'),('TP2','1')}
connected=set().union(*expected.values())
for pad in [('J1','3'),('J1','14'),('J1','21')]+[('J2',str(p)) for p in [2,3,14,15,16,19,20]]:
 assert pad not in connected
 unexpected=[n for n,v in nets.items() if pad in v and not n.startswith('unconnected-')]
 assert not unexpected,(pad,unexpected)
components={c.attrib['ref']:c for c in xml.findall('.//components/comp')}
assert len(components)==52
for i in range(1,34): assert components[f'R{i}'].findtext('value')==('330' if i<=24 else '100' if i<=28 else '10k' if i<=32 else '10k / PHI pulldown')
assert 'Errors 0  Warnings 0' in (root/'hardware/verification/erc.rpt').read_text()
print('PASS: 28 GPIO; independent 32-pin/socket mapping; C++ arrays; 62 logical nets; series paths; JP1/JP2; NC; BOM; ERC')
# Selected PCBA parts must agree with the exported schematic and the supplier BOM.
import csv
parts=json.loads((root/'hardware/bom/selected_parts.json').read_text())
assert len(parts)==5
refs=[ref for p in parts for ref in p['refs']]
assert len(refs)==35 and len(set(refs))==35
assert set(refs)=={f'R{i}' for i in range(1,34)}|{'C1','C2'}
assert [p['lcsc'] for p in parts]==['C17630','C17408','C17414','C49678','C15850']
for p in parts:
 assert p['classification']=='Basic' and p['package']=='0805'
 for ref in p['refs']:
  comp=components[ref]
  assert comp.findtext('footprint')==p['footprint']
  fields={f.attrib['name']:f.text for f in comp.findall('fields/field')}
  assert fields['LCSC']==p['lcsc'] and fields['MPN']==p['mpn']
with (root/'hardware/bom/jlcpcb_pcba.csv').open() as f: supplier=list(csv.DictReader(f))
assert len(supplier)==5
for row,p in zip(supplier,parts):
 assert row['Designator'].split(',')==p['refs']
 assert row['LCSC Part Number']==p['lcsc']
 assert row['Footprint']==p['footprint'].split(':')[1]
print('PASS: PCBA BOM 5 Basic part numbers / 35 placements; schematic MPN/LCSC and footprints match')
for ref in ['JP1','JP2']:
 comp=components[ref]
 assert comp.findtext('footprint')=='GBA_Mechanical:PinHeader_1x02_P2.54mm_D1.02mm'
 fields={f.attrib['name']:f.text for f in comp.findall('fields/field')}
 assert fields['MPN']=='PH-1X2SG' and fields['Supplier Code']=='108593'
fp=(root/'hardware/lib/GBA_Mechanical.pretty/PinHeader_1x02_P2.54mm_D1.02mm.kicad_mod').read_text()
assert re.findall(r'\(drill ([^)]+)\)',fp)==['1.02','1.02']
assert re.findall(r'\(pad "(\d+)"',fp)==['1','2']
assert '(at 0 2.54)' in fp
manual=json.loads((root/'hardware/bom/manual_parts.json').read_text())
assert [(p['mpn'],p['quantity']) for p in manual if p['mpn'] in {'PH-1X2SG','2228GG'}]==[('PH-1X2SG',2),('2228GG',2)]
assert not any('JP' in row['Designator'] for row in supplier)
print('PASS: JP1/JP2 PH-1X2SG; two 1.02mm holes at 2.54mm pitch; 2 caps; excluded from PCBA')
for ref in ['J1','J2']:
 fields={f.attrib['name']:f.text for f in components[ref].findall('fields/field')}
 assert fields['MPN']=='FH2.54-40U1GF8.5-0.5' and fields['Supplier Code']=='110073'
assert components['J3'].findtext('footprint')=='Gekkio_Connector_PCBEdge:GameBoy_Cartridge_AGB_1x32_P1.50mm_Socket_Horizontal'
for i in range(1,13):
 assert components[f'TP{i}'].findtext('footprint')=='GBA_Mechanical:TestPoint_Pad_D2.0mm'
tp=(root/'hardware/lib/GBA_Mechanical.pretty/TestPoint_Pad_D2.0mm.kicad_mod').read_text()
assert '(size 2 2)' in tp and '(layers "F.Cu" "F.Mask")' in tp
assert 'F.Paste' not in tp and '(drill' not in tp
assert all(c.findtext('footprint') for c in components.values())
with (root/'hardware/bom/assembly_parts.csv').open() as f: assembly=list(csv.DictReader(f))
assert next(p for p in assembly if p['MPN']=='FH2.54-40U1GF8.5-0.5')['Quantity per board']=='2'
assert next(p for p in assembly if p['Usage']=='J3')['Supplier Code']=='1005005472303111'
print('PASS: all 52 footprints assigned; TP pads without paste/drill; socket strip quantity; J3 procurement identity')
