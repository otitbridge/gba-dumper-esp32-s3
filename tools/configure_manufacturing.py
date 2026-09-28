#!/usr/bin/env python3
"""Apply V1 JLCPCB design rules. Run with KiCad bundled Python."""
from pathlib import Path
import json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'hardware/gba_dumper.kicad_pro'
x=json.loads(project.read_text()); ds=x['board']['design_settings']
ds['rules'].update(min_clearance=.2,min_track_width=.2,min_copper_edge_clearance=.5,min_hole_clearance=.35,min_hole_to_hole=.45,min_through_hole_diameter=.3,min_via_diameter=.6,min_via_annular_width=.15,min_silk_clearance=.15,min_text_height=1.0,min_text_thickness=.15,solder_mask_to_copper_clearance=.1)
ds['defaults'].update(silk_line_width=.15,silk_text_size_h=1.0,silk_text_size_v=1.0,silk_text_thickness=.15)
ds['defaults']['zones'].update(min_clearance=.2,min_thickness=.25,thermal_relief_gap=.3,thermal_relief_spoke_width=.3)
ds['track_widths']=[0,.2,.25,.3,.5,.8,1.0]
ds['via_dimensions']=[{'diameter':.6,'drill':.3},{'diameter':.8,'drill':.4}]
# No violation is excluded to make the initial placement appear fabrication-ready.
base=x['net_settings']['classes'][0].copy();base.update(name='Default',clearance=.2,track_width=.25,via_diameter=.6,via_drill=.3,priority=2147483647)
signal=base.copy();signal.update(name='GBA_SIGNAL',priority=1)
power=base.copy();power.update(name='POWER_3V3',track_width=.8,priority=0)
x['net_settings']['classes']=[base,signal,power]
patterns=[]
for name in ['BOARD_3V3','CART_3V3','GND']: patterns.append({'netclass':'POWER_3V3','pattern':'/'+name})
for name in ['MCU_*','CART_AD*','CART_A*_D*','CART_n*','CART_PHI','WR_LINK']: patterns.append({'netclass':'GBA_SIGNAL','pattern':'/'+name})
x['net_settings']['netclass_patterns']=patterns
project.write_text(json.dumps(x,indent=2)+'\n')
boardpath=ROOT/'hardware/gba_dumper.kicad_pcb'
b=p.LoadBoard(str(boardpath)); settings=b.GetDesignSettings()
settings.m_SolderMaskExpansion=0
settings.m_SolderMaskMinWidth=p.FromMM(.1)
settings.m_SolderMaskToCopperClearance=p.FromMM(.1)
settings.m_SolderPasteMargin=0;settings.m_SolderPasteMarginRatio=0
p.SaveBoard(str(boardpath),b)
print('Applied JLCPCB V1 rules, routing presets, netclasses and 1:1 solder mask openings')
