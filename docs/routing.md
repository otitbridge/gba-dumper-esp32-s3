# WeAct N16R2 4層配線 — シルク最終整理前

この文書は配線工程の記録。現在はシルク整理・最終DRCも完了し、[出力前レビュー](fabrication_review.md)で停止。以下のシルク未更新の記述は配線工程当時の履歴。

2026-09-28。ユーザー承認済み配置を維持して配線。DRC違反0、未配線0、回路図等価性問題0。**シルクの最終整理・追加と製造出力には進まず、この工程で停止。実機未検証、発注不可。**

|層|役割|トラック数|延長 mm|
|---|---|---:|---:|
|F.Cu|部品面の信号・電源・GND引出し|228|849.60|
|In1.Cu|連続GND面、トラック禁止|0|0|
|In2.Cu|主な信号・電源経路|297|1705.30|
|B.Cu|補助経路|45|346.72|

総トラック長2901.62 mm、貫通ビア62個。信号最小幅0.20 mm、電源/GND最小幅0.50 mmを確認。GND充填領域は1個、面積8936.57 mm²。禁止領域と非GND穴の離隔を反映し、接続検査で未配線なし。面の連続性は確認したが、実機の信号品質を保証するものではない。

## 検証と比較

- 全52回路図部品の位置・回転、全パッドのネット、固定穴を確認。部品フィールド・シルク・図形も配線前と一致。hardware/verification/routing/approved_layout.jsonへ照合用情報を保存。
- ERC、ピンマップ/BOM、C++17定義、配置、製造ルール、配線の検査が合格。ゾーン再充填・保存と回路図等価性を含む最新DRCはhardware/verification/routing_drc.json。
- [FNK0099比較](routing_comparison.md): 総延長−3.83%、最長主経路+0.18%。AD6は個別再配線後、FNK比+8.35 mm（+12.79%）。[AD6のみの再配線記録](ad6_reroute.md)を参照。
- [配線概要PNG](../output/pcb/routed/routing_overview.png) / [SVG](../output/pcb/routed/routing_overview.svg)。赤F.Cu・橙In2.Cu・青B.Cuを上面から表示。
- [GND面PNG](../output/pcb/routed/ground_plane.png) / [SVG](../output/pcb/routed/ground_plane.svg)。In1.Cuは別図で表示し、概要図で他の配線を塗りつぶさない。

## 手順と再現資料

ローカルFreerouting 2.4.1とTemurin JRE 25を既存環境から使用。GUI・API/MCPサーバー・利用状況送信を無効化し、外部配線APIを使わない。JAR SHA-256は251101c3eeac22d7e7dfcf6796603279e5d1000283eb82d8f093780f7afc6aa9。

prepare_routing.pyはWeActの配置からGND引出しを作り、DSN/層ルールを準備する。KiCadのDSN変換が部品禁止領域を銅箔禁止に解釈するため、出力用コピーのみWEACT_UNDERSIDE_NO_COMPONENTSを除去。正式PCBには残す。アンテナ・固定穴の銅箔禁止域とJ3長穴の追加余裕を維持。旧FNKのA16固定経路は持ち込まない。

run_router.shでローカル配線、import_routing.pyでSESとIn1 GND面を取り込み。finish_routing.pyは最小線幅未満だったAD0の2セグメント（0.1874 mm）を0.20 mmへ修正。正式PCBをKiCad DRCで再充填・保存・検査し、違反0を確認。DRC除外や製造ルールの緩和は行っていない。

DSN・ルール・SES・実行ログはhardware/verification/routing/。SESは幅修正・面追加前の中間結果。正本はhardware/gba_dumper.kicad_pcb。配線前の検査記録とplacement画像は履歴として残し、現行結果と区別する。

## 次工程に残すもの

シルクのV1 PLACEMENT / UNROUTEDは意図的に配線前のまま残している。次工程で恒久表記・ボード識別・端子用途表示等と合わせて更新する。DRCが0件でも文言の最終整理完了を意味しない。ガーバー・ドリル・CPL、製造承認、到着品の寸法・嵌合・GPIO起動・電源試験は未完了。

参照: [Freerouting 2.4.1](https://github.com/freerouting/freerouting/releases/tag/v2.4.1)、[同版CLI仕様](https://github.com/freerouting/freerouting/blob/v2.4.1/docs/command_line_arguments.md)。閲覧用出図はtools/export_routing.sh。
