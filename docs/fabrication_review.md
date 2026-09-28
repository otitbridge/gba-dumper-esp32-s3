# WeAct N16R2 — 製造データ出力・照合レビュー

2026-09-28。ユーザー指示により鉛含有HASLの文書変更をd64897fでコミット後、WeAct版ガーバー・ドリル・CPLを作成し照合完了。**出力時点では実機未検証・製造承認なし。その後ユーザーが発注完了（下記）。**

## シルク

- R32手前にGBA DUMPER / WEACT ESP32S3-AとS3-WROOM-1-N16R2 / REMOVE USB FIRSTの2行を配置（X=28、Y=96.5/98.3 mm）。旧WEACT ESP32S3-A / N16R2と独立したREMOVE USB FIRSTは削除。
- PC: USB-UARTはユーザー指示により削除。ユーザー指示によりNATIVE USB: UNUSEDは削除し、J1/J2間のUSB側のJ1寄り（X=64、Y=98 mm）へPCを追加。PCは子基板装着時に隠れる可能性がある位置。子基板の下へ隠れる位置を避けた説明表示であり、端子位置を指す矢印ではない。WeActはGPIO19/20非使用のため旧FNKの「GBA BUS接続禁止」は追加しない。
- 中央のJP1 / JP2 / CARTRIDGE表示を削除。各ジャンパの用途表示の上にCARTRIDGEを配置。WR ENABLE / DEFAULT OPEN、POWER LINK / DEFAULT CLOSED、GBA ONLY / 3.3V、全TP信号名と部品番号は維持。
- 可視シルク文字の高さ・幅は1.0 mm以上、線幅0.15 mm以上。パッド・穴との干渉はDRC、表示の重なりと配置は確認画像で点検。部品位置から見た可視性の確認であり、到着実物の組立試験ではない。

[シルク確認PNG](../output/pcb/final_review/front_silk.png) / [SVG](../output/pcb/final_review/front_silk.svg)。上面視、濃紺がシルク、灰色がソルダーマスク開口。閲覧用に色のみ変更し、基板のシルク形状はKiCadから直接出力。

## 最終検証

- 基準コミット2289d84のPCBをhardware/verification/silkscreen/before.kicad_pcbに保存。シルク文字以外の内容が不変であることを機械比較。全銅箔、ビア、GND面、部品配置、パッド、穴、禁止域を維持。
- ゾーン再充填・保存と回路図等価性を含むDRC: 違反0、未配線0、等価性問題0。ルール緩和・違反除外なし。結果はhardware/verification/routing_drc.json。
- ピンマップ/BOM/ERC記録、配置、製造ルール、配線、シルク変更範囲、配線長とファイルハッシュ、C++17ピン定義を照合。
- AD6主経路73.69 mm、総トラック長2901.62 mm、貫通ビア62個を維持。
- hardware/verification/silkscreen/summary.jsonに対象PCBハッシュを保存。final_layout.jsonは今回作成した最終文字配置の検査用スナップショットであり、ユーザーの追加承認や実機検証を意味しない。

## 次工程

WeAct用Gerber・ドリル・CPL出力と照合は完了。[出力一式と検査結果](../output/fabrication_review/README.md)を参照。次は発注前の実機ゲートとJLCPCB側CAM・実装プレビューの確認。Gate1〜3の未完了事項（到着品、嵌合、起動GPIO、電源等）は[未完了事項](open_items.md)に維持し、DRC合格を発注承認へ読み替えない。

旧FNK版レビューは[履歴](../archive/fnk0099/docs/fabrication_review.md)へ分離。

ジャンパ表示は用途を上段、初期状態を下段に統一。JP1はWR ENABLE / DEFAULT OPEN、JP2はPOWER LINK / DEFAULT CLOSED。各表示はCARTRIDGEを最上段に加えた3行構成で、中心と行間2.5 mmを揃えた。

## リポジトリURLとQR

予定URL https://github.com/otitbridge/gba-dumper-esp32-s3 をQRへ格納。リポジトリは未作成で、リンク先の存在確認ではなく符号の復号一致を確認した。左中央に追加し、表示URLはhttps://を省略してQR左側で4行に折り返す（改行はURLの一部ではない）。

QRは33×33セル、誤り訂正M、セル0.32 mm、周囲4セルの余白を含め13.12 mm角、中心X=29.5 / Y=53.3 mm。白シルクを背景とし、基板色を暗いモジュールに利用する反転シルク。通常の濃紺シルク確認図ではQRの明暗が逆に見える。実基板では白シルクに対して十分に暗いソルダーマスク色を用いる前提。

KiCadの描画を明暗反転したqr_decode_preview.pngからmacOS Visionで完全なURLを復号し一致。結果はhardware/verification/silkscreen/qr_decode.json。画面上の読取り確認であり、実物のシルク印刷・実装後の読取りは未検証。DRC0、銅箔・配置不変。

再生成はKiCad同梱Pythonでtools/add_repository_qr.py（同梱kicad_qrcodeを使用）。既存QRを置換するためのUUID・形状記録はqr.json。白背景の塗りつぶしはF.Silkscreenのみで、銅箔・マスク・ペーストは追加しない。

2026-09-28、ユーザーが「シルクは以上で確定」と承認。URL・QRを含む現行シルクを確定し、コミットする。この時点ではGerber・ドリル・CPL出力は未着手だったが、その後のユーザー指示で作成・照合を実施した。シルク確定は実機検証完了や発注承認を意味しない。

## 表面仕上げの注文指定

2026-09-28のユーザー指定により、裸基板のランド表面仕上げは鉛含有HASL（通常のHASL）とする。鉛フリーHASLではない。注文条件はmanufacturing_rules.mdを正本とし、WeAct版の見積額は別途確認する。HASL指定の変更自体は文書のみ。今回作成したガーバーには表面仕上げの選択は符号化されないため、注文画面で鉛含有HASLを指定する。

## 製造出力照合結果

11層のGerberとPTH/NPTHドリルをZIPへ格納。Gerbonara 1.6.3で再読込みし、100×100 mm外形、4銅層、PTH142個、NPTH6個（丸穴4・長穴2）、上面ペースト70開口をPCBと照合。CPL35部品の座標・回転とBOM5品種が一致。最終DRCは違反0・未配線0・回路図等価性問題0。PCB・配線・確定シルクは変更していない。

実Gerberから上下面PNG/SVGを生成し、上面シルク画像のQRをmacOS Visionで復号、予定URLと一致。実物の印刷品質検証ではない。ZIP、BOM、CPL、検査記録のSHA-256はmanifest.jsonへ記録。

### Gerber jobの扱い

KiCadが生成した.gbrjobは監査用としてgerbersフォルダに残すが、アップロードZIPから除外した。自動メタデータには外形線幅を含む100.1 mm、Finish=None、内層銅厚0.035 mmという既定値が含まれるため。実際の外形中心線は100×100 mm。注文は製造ルール文書の1.6 mm・外層1 oz/内層0.5 oz・鉛含有HASLを指定し、メーカー標準積層を確認する。PCBの積層メタデータはメーカー確定積層を意味しない。

## 2026-09-28 発注実績

ユーザーから注文完了の報告を受領。注文番号 **[order-id-redacted]**、総額 **4,609円**（5枚・SMT実装・OCS Express送料込み）。[注文記録](jlcpcb_order_20260928.md)に条件・内訳・確認範囲を保存。出力時点のmanifestとREVIEW_ONLYファイルは履歴として維持し、実機未確認項目を検証済みに変更しない。
