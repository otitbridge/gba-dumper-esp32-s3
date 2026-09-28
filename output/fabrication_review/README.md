# 製造前レビュー用出力

2026-09-28 / KiCad 10.0.5 / WeAct ESP32S3-A N16R2 / PCB正本コミット d64897f。
**REVIEW ONLY — 製造承認前。実機ゲートとメーカー追加CAM確認が残る。**

- [ガーバー・ドリルZIP](gba_dumper_gerbers_REVIEW_ONLY.zip)：11層＋PTH/NPTHドリル。100×100mm、4層。
- [CPL](assembly/jlcpcb_cpl.csv)：上面35個、R1〜R33とC1/C2。
- [BOM](assembly/jlcpcb_bom.csv)：5品種。手はんだ・機構部品を含まない。
- [上面画像](review/gerber_top.png) / [裏面画像](review/gerber_bottom.png)：Gerbonaraによる実出力の再描画。SVGも同じフォルダ。
- [照合結果](review/verification.json) / [SHA-256一覧](manifest.json)。

全データはPCB絶対原点を共有し、Y座標は−100〜0mm。CPLだけを移動・反転しない。
メッキ穴142個、非メッキ穴6個（固定穴4・長穴2）、上面ペースト開口70個を照合済み。
JLCPCB側プレビューでは部品の重なり・向き、追加位置決め穴と銅箔離隔を別途確認する。

## 再生成

プロジェクトルートで以下を実行（kicad-cliはKiCad 10.0.5、prepareはpcbnew対応Python、verifyはGerbonara 1.6.3を使用）。

```sh
kicad-cli pcb export gerbers --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts --subtract-soldermask --disable-aperture-macros -o output/fabrication_review/gerbers hardware/gba_dumper.kicad_pcb
kicad-cli pcb export drill --format excellon --drill-origin absolute --excellon-units mm --excellon-zeros-format decimal --excellon-oval-format alternate --excellon-separate-th -o output/fabrication_review/gerbers hardware/gba_dumper.kicad_pcb
kicad-cli pcb export pos --side front --format csv --units mm --smd-only --exclude-fp-th --exclude-dnp -o output/fabrication_review/review/kicad_positions.csv hardware/gba_dumper.kicad_pcb
python3 tools/prepare_fabrication_review.py
python3 tools/verify_fabrication_exports.py
```

画像はGerbonara LayerStack.open(gerbers)のto_pretty_svg(side='top'/'bottom')から作成。画像更新後にverifyを再実行しmanifestを更新する。検査スクリプトは現在の部品・形状に限定した照合であり、設計変更時には検査条件も見直す。

## 注文条件・検査記録

表面仕上げは鉛含有HASL、4層・1.6 mm・外層1 oz/内層0.5 oz・緑マスク・白シルク。表面仕上げは注文画面で指定する。PCBAは上面の抵抗・コンデンサ35個のみで、J1/J2/J3/JP1/JP2は手はんだ。旧FNK版の見積額をWeAct版へ流用しない。

DRCは[記録](review/drc.json)のとおり違反・未配線・回路図等価性問題すべて0。実Gerberのシルクを白、背景を暗緑色として[QR確認画像](review/gerber_silk_qr.png)を生成し、予定URLへの復号一致を確認（[記録](review/qr_decode.json)）。画像上の細いQR横線はSVGラスタライズの境界表現で、矩形の座標は接している。実物印刷は未確認。

画像の再生成はtools/render_fabrication_review.py（Gerbonara 1.6.3）でSVGを生成後、sharpでPNG化。画像・文書更新後にverify_fabrication_exports.pyを再実行してmanifestを更新する。

### Gerber jobの扱い

KiCadが生成した.gbrjobは監査用としてgerbersフォルダに残すが、アップロードZIPから除外した。自動メタデータには外形線幅を含む100.1 mm、Finish=None、内層銅厚0.035 mmという既定値が含まれるため。実際の外形中心線は100×100 mm。注文は製造ルール文書の1.6 mm・外層1 oz/内層0.5 oz・鉛含有HASLを指定し、メーカー標準積層を確認する。PCBの積層メタデータはメーカー確定積層を意味しない。
