# 書込みと初回接続（0.22.4 public build）

対象はWeAct ESP32S3-A N16R2（16 MiB flash）と本プロジェクトのGBA用基板V1（20260928）です。ESP32-S3一般や別配線には使用できません。

## 4バイナリの書込み

1. 電源を切ってカートリッジを外します。ジャンパ・挿し替えは電源OFFで行います。USBはUART側かネイティブ側のどちらか一本だけを接続します。
2. Pythonと公式esptoolを用意します。確認に使った版は5.1.0です：`python -m pip install "esptool==5.1.0"`。シリアルモニタは閉じます。
3. `manifest.json`／`SHA256SUMS`で配布物のサイズとSHA-256を確認します。
4. `PORT`をWindowsの`COM5`やmacOSの`/dev/cu.usbmodem...`など、実機のポートへ置き換えます。

ネイティブUSBを使う場合は、BOOTを押したままRESETを一度押して離し、最後にBOOTを離します。書込みモードで現れるポートを使います。通常のUSBドライブ動作中はシリアルポートを公開しません。

配布ディレクトリで実行します：

```sh
python -m esptool --chip esp32s3 --port PORT --baud 115200 --before no-reset --after no-reset write-flash --flash-mode dio --flash-freq 40m --flash-size 16MB 0x0 firmware/bootloader.bin 0x8000 firmware/partition-table.bin 0x10000 firmware/gba-dumper-0.22.4-public.bin 0x210000 firmware/ota-data-initial.bin
```

UART側USBでも手動BOOT／RESETで書込みモードへ入り、同じコマンドを使えます。UARTの通常自動リセットを使う場合は`--before default-reset`へ変更します。接続・書込み・ハッシュ照合が失敗した場合は正常導入済みとは扱いません。

4本すべてで`Hash of data verified`を確認した後、BOOTに触れずRESETだけを押して通常起動します。ネイティブUSBの自動リセットだけでは書込みモードが残る場合があります。

この手順は2 MiB×2スロットの配布構成へそろえ、起動先をota_0へ初期化します。NVS（0x9000、0x6000 B）は書込み対象に含めず、保存済みWi-Fi設定を維持します。全消去は不要です。別レイアウトの既存FWからの設定互換性は保証しません。アプリだけを0x10000へ書くと現在の起動先によっては更新されないため、通常は4本セットを使ってください。

## USBだけでROMを取り出す

書込みが済んだらUSBを抜いて電源を切り、カートリッジを装着します。JP2はCLOSE、既存評価構成のJP1もCLOSEのままで構いません。読み出し専用USB経由ではセーブ書込みは行いません。ネイティブUSB一本でiPhoneまたはPCへ接続します。Wi-Fi設定は不要です。[USB操作](USAGE.md#usbでromをコピー)を参照。

## Webを使う初回Wi-Fi設定

保存済み設定があればそのWi-Fiへ自動接続します。設定がない、または接続できない場合は機器が`GBA-Dumper-XXXXXX`の親機になります。初回のWeb接続にはこの親機パスワードが必要です。

1. ネイティブUSBを外してUART側USB一本で接続し、115200 bps・8N1のシリアルモニタを開きます。
2. 必要なら`WEB SETUP`、続いて`WIFI APINFO`を改行付きで送信し、親機の接続名とパスワードを取得します。応答を公開ログへ添付しないでください。
3. iPhone／PCを機器のWi-Fiへ接続し、通常は `http://192.168.4.1/` を開きます。別ネットワークとの競合時は `192.168.5.1` の場合もあり、UARTの`WEB_READY`で確認します。インターネット接続がなくても機器との接続を維持します。
4. Webで2.4 GHzのWi-Fiを検索し、接続先のSSID・パスワードを設定します。成功した設定だけ保存し、次回起動でも使用します。DHCPのIPは固定ではありません。NVSのWi-Fi設定は現状暗号化していません。

パスワードは機器内のRNGで生成し、NVSへ保存します。開発者共通のSSID・パスワード・OTA認証局は配布バイナリに含みません。初回生成と消去済みNVSからの設定手順の確認状況は[検証結果](VALIDATION.md)を参照。対応版導入後は[Web更新](UPDATE.md)を利用できます。UART指令による旧OTA開始は無効です。

## 導入済み機器の通常更新

0.14系以降は原則として[Web更新](UPDATE.md)を使います。4本セットの有線書込みは初回導入・構成移行・復旧用です。Web更新画面へブートローダーやパーティション表を送らないでください。
