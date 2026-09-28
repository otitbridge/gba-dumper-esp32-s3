# 現行WeAct版の参照資料

2026-09-28: WeActStudio公式ESP32S3-A回路図・外形図を取得、回路・ピン配列と機械寸法を確認。原本とSHA-256はhardware/reference/weact、照合結果はweact_footprint.md。Espressif WROOM-1データシートv1.8のTable1-1（N16R2 Quad SPI PSRAM）と3-1を再確認。秋月110073の切断可能構造、寸法、推奨穴径を再確認。下記S1/S2と旧S3のGPIO35〜37 NC方針はFNK0099版の履歴でありWeActへ適用しない。

# 参照資料・確認状況

基準日2026-09-27。ユーザー提示のS番号を維持する。再取得・再確認済みと、提供仕様から継承した根拠を区別する。

|ID|資料|今回の扱い|
|---|---|---|
|S1|[Freenove Preface](https://docs.freenove.com/projects/fnk0099/en/latest/fnk0099/codes/Python/Preface.html)|2026-09-27閲覧。ボードとCH343の背景確認。35〜37再利用記述は設計に採用しない|
|S2|[公式ピンアウト](https://raw.githubusercontent.com/Freenove/Freenove_ESP32_S3_WROOM_Board_Lite/main/ESP32S3_Lite_Pinout.png)、[公式リポジトリ](https://github.com/Freenove/Freenove_ESP32_S3_WROOM_Board_Lite)|2026-09-27画像を取得しJ1/J2全端子を視認照合。リポジトリmainツリーのパス検索では回路図を特定できず。現物寸法・取り外し部品番号は未確認|
|S3|[Espressif WROOM-1/1U datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)|提供資料のv1.8、印刷p12 Table3-1注bという根拠を継承。今回PDFの版を再確認していない。35〜37をNCとするユーザー指定を厳守|
|S4|[ESP-IDF GPIO](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html)|実装時に採用ESP-IDF版へ固定して再確認。今回ドライバ未実装|
|S5|[GBATEK GBA-only mirror](https://rust-console.github.io/gbatek-gbaonly/)|提示仕様のGBA論理番号・バス要求を継承。今回はプロトコル詳細を新規確定していない|
|S6|[gba-cartridge](https://github.com/jojolebarjos/gba-cartridge)|バス実装参考として継承。今回コードの転用なし|
|S7|[sanni/cartreader GBA.ino](https://github.com/sanni/cartreader/blob/master/Cart_Reader/GBA.ino)|提示blob SHA 6990b7c7b9d02da5d35fb39be63d971dfa922ccfはコミットではない。実装採用コミット・ライセンスは未確認、転用なし|
|S8|[ESP-IDF UART](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/uart.html)|実装時に採用版と照合。今回未実装|

本回路図の値・GPIO配置・検証条件の直接の正本はユーザー提示仕様。閲覧していない資料を今回検証済みとはしない。

## S9 — ユーザー指定J3候補

Gekkio/gekkio-kicad-libsのAGB 32極ソケットフットプリントを2026-09-27に取得。原本・CC BY 4.0本文を同梱。出典URL、SHA-256、寸法、不整合は[slot_footprint.md](slot_footprint.md)へ記録。実物適合は未検証。

## S10 — PCBA部品とC2特性

2026-09-27にJLCPCB公式のC17630/C17408/C17414/C49678/C15850の商品ページで仕様とBasic区分を確認。Samsung公式製品ページおよび同社特性図を確認。各URLと確認範囲は[pcba_parts.md](pcba_parts.md)へ記録。

## S11 — JP1/JP2の秋月選定

2026-09-27、秋月電子108593/103890商品ページおよび添付メーカー図面を照合。ヘッダ・キャップの定格3A、寸法、推奨穴径、価格と販売単位を[jumper_parts.md](jumper_parts.md)へ記録。

## TP・組立部材（2026-09-27取得・確認）

- KiCad 10.0.5同梱TestPoint_Pad_D2.0mm：F.Cu/F.Maskのみ、φ2mm。https://www.kicad.org/libraries/license/ （標準ライブラリのライセンス）
- https://akizukidenshi.com/catalog/g/g110073/ ：Ronmeeソケット型番と分割使用。嵌合は同日のユーザー回答で確認。
- https://ja.aliexpress.com/item/1005005472303111.html ：ユーザー指定のJ3調達先。ページ本文は取得不可、MPN未確認。
- https://www.sanwa.co.jp/product/syohin?code=TK-CAP6BK ：PE製Type-Cメス用キャップ、寸法・数量。
- https://www.nitto.com/jp/ja/products/construction/protection002/ ：No.21赤色絶縁テープ19mm。
- https://akizukidenshi.com/catalog/g/g101861/ ：樹脂スペーサー14mm×4、ネジ7mm×8のセット。
- https://akizukidenshi.com/goodsaffix/OS-SCREW-3PL-1_oldvsnew_20250321.pdf ：新旧寸法図。現行供給品は販売ページ上Bタイプ。
