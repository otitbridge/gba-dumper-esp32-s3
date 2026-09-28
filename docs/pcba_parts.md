# PCBA受動部品選定 — 2026-09-27

抵抗33個とコンデンサ2個、計5種類35個を選定。全て0805、JLCPCB商品ページでBasicおよびEconomic and Standard対応を確認。片面SMTとし、J1/J2/J3およびJP1/JP2は手はんだ、TPは露出パッドとしてPCBA部品から除外する。

|Ref|数量|値・定格|メーカー型番|LCSC・根拠|
|---|---:|---|---|---|
|R1〜R24|24|330 Ω、1%、125 mW|UNI-ROYAL 0805W8F3300T5E|[C17630](https://jlcpcb.com/partdetail/C17630)|
|R25〜R28|4|100 Ω、1%、125 mW|UNI-ROYAL 0805W8F1000T5E|[C17408](https://jlcpcb.com/partdetail/0805W8F1000T5E/C17408)|
|R29〜R33|5|10 kΩ、1%、125 mW|UNI-ROYAL 0805W8F1002T5E|[C17414](https://jlcpcb.com/partdetail/0805W8F1002T5E/C17414)|
|C1|1|100 nF、50 V、X7R、10%|YAGEO CC0805KRX7R9BB104|[C49678](https://jlcpcb.com/partdetail/YAGEO-CC0805KRX7R9BB104/C49678)|
|C2|1|10 µF、25 V、X5R、10%|Samsung CL21A106KAYNNNE|[C15850](https://jlcpcb.com/partdetail/CL21A106KAYNNNE/C15850)|

抵抗は最大使用電圧150 V、温度係数±100 ppm/℃の掲載。電圧定格は許容電力の制限を解除しない。3.3 Vが抵抗両端に掛かる場合の計算は330 Ωで33 mW、100 Ωで109 mW、10 kΩで1.09 mW。特に100 Ωは125 mW定格に近い。通常の制御信号は入力負荷であり、この計算は短絡を許容する根拠ではない。GPIO保護はバス方向制御と非選択状態の確保が主対策。

## フットプリント

- 抵抗: `Resistor_SMD:R_0805_2012Metric`
- コンデンサ: `Capacitor_SMD:C_0805_2012Metric`

KiCad 10.0.5同梱の標準SMTパッドを採用。HandSolder拡大パッドではない。R1〜R33/C1/C2に割当済み。メーカー・MPN・LCSC・定格を回路図の非表示プロパティにも記録。J1/J2の既存割付は維持し、J3は後続のユーザー裁定で提示GitHubフットプリントに確定。

## C2のDCバイアスと電源適合

[メーカー製品情報](https://product.samsungsem.com/mlcc/CL21A106KAYNNN.do)で0805、2.00±0.20×1.25±0.20×1.25±0.20 mm、10 µF、25 V、X5Rを確認。

[Samsung特性図（DigiKey配布）](https://media.digikey.com/pdf/Data%20Sheets/Samsung%20PDFs/CL21A106KAYNNNE_Char.pdf)のDC Bias図を視認した。3.3 V付近では容量減少が約30%であり、公称10 µFに対して典型的に約7 µFという読み取り。曲線の概算であり、温度・公差・経時変化・測定AC条件を含む最低容量保証ではない。25 V定格だけを根拠に3.3 V時の容量低下を無視しない。

本仕様の10 µFはPoC初期の公称値なので、本品を選定する。実効10 µF以上という新規要件が生じた場合は容量・サイズを見直す。WeActのレギュレータ型番、セラミック容量追加との安定性、立上がり、対象負荷での電圧低下・発熱は未検証として残す。

## BOMと発注時の確認

- `hardware/bom/selected_parts.json`: 5品種の型番・定格・出典の生成元。
- `hardware/bom/preliminary.csv`: 全52参照部品の一覧。選定部品も実機未検証と明示。
- `hardware/bom/jlcpcb_pcba.csv`: 5行・35個、JLCPCB用Comment/Designator/Footprint/LCSC Part Number形式。

同じMPNでも別LCSC番号にExtended区分の登録があるため、上表のLCSC番号で指定する。Basic区分は確認日時点の掲載であり固定保証ではない。在庫全5品種の数量を確定したとは扱わず、注文数量と実装ロスを含め発注画面で在庫・Basic区分・Economic対応を再確認する。

WeAct版は配線・シルク・DRC・CPL作成と照合まで完了。CPLはoutput/fabrication_review/assembly/jlcpcb_cpl.csv。2026-09-28、注文画面で5品種すべてBasicとして一致確認し、ユーザーが発注完了（[order-id-redacted]、送料込み4,609円）。[注文記録](jlcpcb_order_20260928.md)を参照。実機検証済みとはしない。
