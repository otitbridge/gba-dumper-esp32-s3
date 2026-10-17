# UART書込みと初回接続

対象はWeAct ESP32S3-A N16R2（16 MiB flash）と本プロジェクト基板V1です。ESP32-S3一般や別の配線には使用できません。

1. USBを抜いてカートリッジを外します。ジャンパ・挿し替えは電源OFFで行います。UART側USBのみで接続し、2つのUSBを同時給電しません。
2. Pythonと公式esptoolを用意します。`python -m pip install esptool`。書込み前にシリアルモニタを閉じます。
3. `manifest.json`のサイズ・SHA-256と配布ファイルを確認します。
4. 配布ディレクトリで次のコマンドを実行します。`PORT`はWindowsでは`COM5`など、macOSでは`/dev/cu.usbmodem...`など、実際の機器のポートに置き換えます。

```sh
python -m esptool --chip esp32s3 --port PORT --baud 115200 write_flash --flash_mode dio --flash_freq 40m --flash_size 16MB 0x0 firmware/bootloader.bin 0x8000 firmware/partition-table.bin 0x10000 firmware/gba-dumper-0.11.1-public.bin 0x210000 firmware/ota-data-initial.bin
```

これは本プロジェクトの2 MiB×2スロット構成へそろえる書込みです。起動先情報も初期化してota_0から起動させます。0x9000のNVSは書込み対象に含めません。別の既存FWから移行する際には、以前の保存データとの互換性を保証しません。全消去コマンドは通常手順に含めません。CH343経路の通常書込みは開発機でエラーが発生したことがあり、通信・照合が失敗した場合は公開版を正常導入済みと扱わず、Issuesへ報告してください。

5. 通常再起動します。保存済みWi-Fiがなければ機器が`GBA-Dumper-XXXXXX`の親機になります。
6. 初回のパスワードはUARTの115200 bps・8N1のシリアルモニタから取得します。必要なら`WEB SETUP`、続いて`WIFI APINFO`を改行付きで送信します。応答に接続名とパスワードが含まれるため、スクリーンショットや公開ログには残さないでください。
7. iPhone／PCで機器のWi-Fiへ接続し、通常は `http://192.168.4.1/` を開きます。インターネット接続がなくても機器との接続を維持します。同一サブネット競合時は`192.168.5.1`へ切り替わる場合があるため、UARTの`WEB_READY`で確認します。
8. Webで2.4 GHzのWi-Fiを検索し、接続先のSSID・パスワードを設定します。成功した設定だけ保存され、次回起動時に使われます。接続できない場合は親機へ戻ります。

既存の機器では保存済みWi-Fiへ自動接続するため、UARTの`WEB_READY`に表示されたURLを開きます。DHCPのIPアドレスは固定ではありません。NVS内のWi-Fi設定は現状暗号化していません。

初回にシリアルモニタを開くと自動起動が抑止される場合があります。その場合も`WEB SETUP`で親機を開始できます。UART接続に失敗する場合は基板のBOOT／RESETとWeAct公式手順を確認してください。UARTではセーブを直接操作する指令を送らず、初期設定完了後にモニタを閉じてWebを使います。
