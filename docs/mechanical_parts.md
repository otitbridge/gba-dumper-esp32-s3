# TP・固定部材・ソケット

WeAct版、2026-09-28。TP1〜12は直径2 mmの露出銅箔パッド。F.Cu＋F.Mask、ペーストなし、穴なし。無部品でPCBA対象外。TP信号はpinmap.mdと回路図で確認。

H1〜4はφ3.2 mm NPTH丸穴。秋月101861のM3樹脂ねじ7 mm＋スペーサ14 mmセット1組（脚4個・ねじ8本、4本余り）を維持。固定穴周囲8 mm角はトラック・ビア・銅箔ゾーン禁止。機械寸法はpcb_placement.md参照。組立後の安定性と固定強度は未確認。

J1/J2は各22極へ変更し、秋月110073を2本購入。weact_footprint.md参照。JP1/JP2のヘッダとキャップはjumper_parts.mdの選定を維持。

GPIO19/20をGBAから外したため、以前のNative USB封止キャップTK-CAP6BKと赤テープNo.21は必須調達品から除外。V1はUART側USBを使用し、二つのUSBから同時給電しない。
