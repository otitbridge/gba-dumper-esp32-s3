# AD6経路比較

変更前はarchive/fnk0099/gba_dumper.kicad_pcb、変更後はAD6再配線前のhardware/verification/ad6_reroute/before.kicad_pcb。上面視・同一縮尺。基板輪郭は100 mm角。全配線を薄灰色、AD6のMCU側とカートリッジ側を層別の色で強調。丸枠はビア、黄色丸は接続パッド、R7両端の破線は抵抗本体。

- before_fnk0099.png: 変更前
- after_weact.png: 変更後
- comparison.png: 左右比較

図の強調はAD6ネット全体（小さな枝も含む）。表示長は比較資料と同じ最短の主経路で、パッド内部・抵抗内部・ビア垂直長は除く。FNKは65.33 mm、WeActは83.23 mm。WeActの全トラック合計は83.32 mmで、主経路との差は約0.09 mm。層間の移動は丸枠で追える。実際のKiCadトラック座標から描画し、線の視認性を上げるため描画幅のみ強調している。基板や配線は変更していない。

再生成: KiCad同梱Pythonでtools/render_ad6_comparison.pyを実行し、SVGをNode sharpでPNGへラスタライズする。
