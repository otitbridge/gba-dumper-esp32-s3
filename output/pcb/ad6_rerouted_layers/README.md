# AD6再配線後の4層配線図

2026-09-28。正式PCBからKiCad CLIで各銅箔層とEdge.Cutsを出図。全層を部品面から透視した向き・同一縮尺で表示し、裏面も反転していない。In1.CuはGND面。銅箔・パッド・ビア・穴を表示し、シルクは省略。

- four_layers.png: 4層一覧、上段F.Cu／In1.Cu、下段In2.Cu／B.Cu
- F.Cu.png、In1.Cu.png、In2.Cu.png、B.Cu.png: 各層2000×2000 px
- 同名SVG: ベクトル原図
- source.json: 出図元PCBとSHA-256

AD6主経路73.69 mmの再配線後。PCB自体は変更していない。閲覧用資料であり製造出力ではない。

再生成: 各層について `kicad-cli pcb export svg --layers <layer>,Edge.Cuts --mode-single --page-size-mode 2 --exclude-drawing-sheet -o output/pcb/ad6_rerouted_layers/<layer>.svg hardware/gba_dumper.kicad_pcb`、続いてsharpが使えるNodeで `tools/render_routing_layers.js` を実行。
