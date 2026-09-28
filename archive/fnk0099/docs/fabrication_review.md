# シルク整理・製造前CADレビュー

2026-09-27。**CAD上のDRC違反0件、未配線0件、回路図等価性問題0件。製造承認は未実施。**

## 今回完了した作業

- 可視シルク文字を高さ1.0mm以上、線幅0.15mmへ修正。既知の高さ68件・線幅52件、計120件の警告を解消した。DRC設定・除外は緩めていない。
- `NATIVE USB / DO NOT CONNECT - GBA BUS` を左側の見える空間に表示。特定コネクタを指す矢印ではなく、Native USB全般への禁止表示。実物ポートの封止・表示と併用する。
- JP1は `WR ENABLE / DEFAULT OPEN`、JP2は `POWER LINK / NORMALLY CLOSED` と表示。
- `REMOVE USB FIRST / JP1 / JP2 / CARTRIDGE` を表示し、操作前の無給電を明示。GBA ONLY / 3.3V、TP信号名を維持。
- H1/H2の参照文字を基板内側へ移動。部品位置・穴位置は変更していない。
- 非製造層の確認前注記を整理。製造シルクからUNROUTED表記を削除。
- 配線完了コミット8d5587cとの比較で、全トラック・ビア形状、パッド形状とネット、部品位置・回転が同一であることを確認した。
- PCBA対象は上面35個、BOMは5品種で一致。手はんだ部品やTP・固定穴がJLCPCB部品表へ混入していない。

## 成果物

- `hardware/gba_dumper.kicad_pcb`：シルク整理済み正本。
- `hardware/verification/routing_drc.json`：全項目0件の最新DRC。ゾーン再充填・回路図照合を含む。
- `hardware/verification/fabrication_preflight.json`：出図前CADチェック。manufacturing_approvedはfalse。
- `output/pcb/final_top.svg` / `.png`：上面の配線・シルク図。部品実装後の3D表示ではない。穴の全体確認はPCBデータ・既存配置図も参照する。
- `tools/finish_silkscreen.py` / `tools/check_fabrication_readiness.py`：整理・検査用スクリプト。

## 出図・発注までに残ること

1. ガーバー・ドリル・CPLの出力と独立照合は完了（下記）。在庫・Basic区分は発注時に再確認する。
2. エコノミーPCBA用位置決め穴はメーカー追加を基本とし、追加CAMの位置・銅箔離隔を確認する。既存M3固定穴で代用しない。捨て板・フィデューシャルの条件も注文時に確認する。
3. `open_items.md` に残る実機GPIO・起動・電源・封止保持性・カートリッジ挿抜等を確認する。ユーザー確認済みの配置やアクセスを再度未確認には戻さない。

この段階でガーバーのレビュー用出力へ進むことは可能だが、出力したことを発注承認と扱わない。ガーバー・CPLはレビュー用として生成済み。購入・注文・アップロードは行っていない。


## ガーバー・ドリル・CPL照合（2026-09-27）

正本コミット `e7eb536` のPCBからKiCad 10.0.5で出力。PCB自体の変更なし。
成果物は [出力案内](../output/fabrication_review/README.md)、機械検査結果は [verification.json](../output/fabrication_review/review/verification.json)。

- 銅箔4層、マスク2層、シルク2層、ペースト2層、外形1層の計11ファイル。裏面シルク・裏面ペーストは空で正常。
- 独立パーサーGerbonara 1.6.3で再読込し、外形中心線100×100mmを確認。上下レンダリング画像を目視確認し、固定穴、J3長穴、シルクと実装パッドの配置を確認した。
- PTH139個＝部品穴76個＋ビア63個。NPTH6個＝φ3.2mm固定穴4個＋1.6×4.6mm長穴2個。位置・径・長穴端点をPCBから抽出した期待値と一対一照合。
- Excellonの座標出力は小数3桁mm。比較許容差0.000501mmは最大0.0005mmの丸めと浮動小数誤差だけを吸収する。GerbonaraのG90ヘッダ位置警告は残るが、絶対座標と全穴形状の照合は成功。
- CPL35個はR1〜R33、C1/C2のみ。全てTop、回転0°。BOM5品種の参照番号と一致。上面ペースト開口70個をPCBパッド形状の外接矩形と照合し、各CPL中心が対応する2開口の中点になることを確認。
- Gerber・ドリル・CPLは共通原点。+X右、+Y上で、現基板のYは−100〜0mm。CPLだけの原点変更やY符号変更をしない。裏面画像は裏面から見た左右反転表示。
- 全銅箔形状の独立ネット再構成やメーカーCAM照合までを完了した意味ではない。正本の最新DRCは違反・未配線・回路図等価性問題いずれも0件。
- ZIPは基板製造データ14ファイルのみ。CPL/BOMはassemblyフォルダで別管理。manifest.jsonに正本と出力ファイルのSHA-256を保存。

CPL列名は [JLCPCB公式KiCadガイド](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad) に合わせた。製造承認は引き続き未実施。位置決め穴の追加CAM確認および実機ゲートは残る。
