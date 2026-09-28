# J3スロットの確定フットプリント

2026-09-27、ユーザー裁定により提示GitHubフットプリントを確定採用。原本を変更せずプロジェクト内ライブラリに保存し、J3へ割当済み。採用根拠はユーザー裁定であり、新規実測の完了を意味しない。

- 著者・配布元: Gekkio / [gekkio-kicad-libs](https://github.com/Gekkio/gekkio-kicad-libs)
- [取得URL](https://raw.githubusercontent.com/Gekkio/gekkio-kicad-libs/main/Gekkio_Connector_PCBEdge.pretty/GameBoy_Cartridge_AGB_1x32_P1.50mm_Socket_Horizontal.kicad_mod)
- ライセンス: CC BY 4.0。原文はhardware/lib/licenses/Gekkio-CC-BY-4.0.txt。原本は無保証で提供される。
- KiCad形式: version 20260206、generator_version 10.0。
- SHA-256: `4a1884ea326590eea102b43216ce3d89ce4204e4d52d5eff547ab522a2feaf7b`
- 取得時のmainから保存。コミットIDは未取得。内容の同定には上記ハッシュを用いる。

## ファイルから確認できる寸法（mm）

|項目|内容|
|---|---|
|信号パッド|1〜32、各番号1個、スルーホール|
|X方向配置|1.5刻み。1番(0,0)、31番(45,0)|
|通常の偶数端子|2〜30番はY=-1.5|
|32番端子|**(46.5,-3)**。通常の偶数列と異なる|
|信号穴|直径1.0|
|銅箔パッド|1番1.4×1.4の矩形、2〜32番直径1.6の円|
|固定用NPTH|中心(-15.2,-1.4)、(54.7,-1.4)、穴1.6×4.6の長穴|
|Courtyard外接寸法|72.9×22.1（X=-16.7〜56.2、Y=-20.5〜1.6）|

上記外接寸法にはカートリッジの挿入・取り外し空間やWeActを含まない。100mm角への全体配置成立は別途確認する。

## 原本の特徴と裁定記録

ファイル名はAGBだがdescrは「Game Boy cartridge slot, Super Game Boy and Super Game Boy 2」。この説明文と32番端子のY=-3mm配置を含め、ユーザー裁定で原本のまま採用する。これらを理由とするフットプリント採用・割付の保留は解除した。

購入するスロットの型番または購入先は調達記録として別途記載する。組立時には採用形状に合う部品であることと接点の導通を受入検査する。汎用1×32一直線コネクタと交換可能とは扱わない。

3Dモデル参照は${KICAD10_3DMODEL_DIR}/Gekkio_Connector_PCBEdge.3dshapes/...wrl。モデル本体は未取得なので表示できると保証しない。今回のフットプリント確定は基板全体のGate3完了・製造承認とは別である。

調達先追記（2026-09-27）：ユーザーから https://ja.aliexpress.com/item/1005005472303111.html を指定。商品番号を調達識別子としてBOMへ反映。商品ページ本文は取得できず、メーカー型番や注文バリエーションは推測していない。フットプリント確定の裁定は維持する。
