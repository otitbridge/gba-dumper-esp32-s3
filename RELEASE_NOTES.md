# 0.13.0 public build — USB MSC対応開発版

- ネイティブUSBに読み取り専用「GBA-DUMPER」を追加。iPhoneの「ファイル」やPCへROMをコピーできます。
- 既存のNo-Intro容量表からROM容量を設定し、各4 KiBを2回読んで照合します。未知・競合容量のROMは公開しません。
- Web UI・Wi-Fi設定・転送・EEPROM操作を維持。USBとWeb等のカートリッジ操作を排他制御し、WebにUSB停止／有効化ボタンを追加しました。
- 保存済みWi-Fi設定は維持。初期Wi-Fi設定・私用OTA認証局を含めず、公開版のOTA開始は従来どおり無効です。
- TinyUSB（MIT）とesp_tinyusb（Apache-2.0）の表示・ライセンス原文を追加しました。

配布用バイナリと開発用バイナリは異なります。公開用そのものの実機結果、iPhone報告との区別、初期NVSなどの残件は[VALIDATION.md](VALIDATION.md)を参照してください。ソースコード・最新設計は今回も非公開です。

---

# 0.11.1 public build — 開発版

ブラウザ操作、Wi-Fi検索と永続設定、親機への自動切替、ROM容量設定、EEPROM 512 Bの退避・書込み・中断後復元を提供します。

開発用0.11.1との配布用差分：初期Wi-Fi設定なし、親機パスワードを機器RNGで初回生成してNVS保存、私用OTA認証局なし、OTA START無効。Web UIとUART書込みは維持します。

配布用ビルドの生成と既知の私用値・鍵・パスの検査は完了。配布ビルド自体の実機確認は未実施です。開発用FWの検証範囲・残件はREADMEとUSAGEを参照してください。
