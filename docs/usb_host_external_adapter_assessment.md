# 外付けUSBホスト給電アダプターの追加調査

調査日: 2026-09-28。検討資料でありV1の採用仕様・動作確認済みBOMではない。PC通信UART0→CH343を維持。PCB、BOM、シルク、製造状態は変更しない。

## 結論

外部5VでUSB機器を給電し、ESP32-S3のNative USBをホストとして使う方法には公開事例がある。一方、WeAct ESP32S3-A N16R2＋下記市販アダプター＋USBメモリの組合せを検証した一次資料は今回の検索では確認できなかった。したがって「基板無改造で評価可能な候補」であり、「購入して挿すだけで動作保証」とはしない。

## 動作実績の範囲

1. Espressif ESP-IDF v5.5のMSCホスト公式例はESP32-S3対象を明記し、USBメモリ上の作成・読出し・書込みを実装。FATを対象とする。READMEの速度例をESP32-S3の実測値として転用しない（複数チップ向け）。[公式MSC例](https://github.com/espressif/esp-idf/blob/v5.5/examples/peripherals/usb/host/msc/README.md)
2. K7MDL2のIC-905 Band DecoderはESP32-S3でUSB-UARTとUSBホストを併用する実動プロジェクト。非給電OTG端子にはYケーブル等による5V追加が必要と説明。ただし周辺機器は無線機のCDC/VCPで、USBメモリではない。筆者が最終的に1kΩジャンパを使用した記述もあり、Yケーブル単体の型式付き実測保証とは扱わない。無線機のVBUS検知向け1kΩ接続はバス給電USBメモリへ流用しない。[作者README](https://github.com/K7MDL2/IC-905_Band_Decoder_on_ESP32-S3/blob/main/README.md)
3. touchgadgetのUSBホスト実験ではUSBブレークアウトへの別5V供給、ケーブルVBUSを切り離す接続方法と動作例を公開。対象はESP32-S2・MIDI等であり、S3＋MSCの直接実績ではない。[作者README](https://github.com/touchgadget/esp32-usb-host-demos)

## WeAct回路に対する判断

保存済み公式ESP32_S3_A_Sch.pdf（SHA-256 ad44dcae89c68d47c769958268a52bd499d6cb76730602efbe738c1fd79d63f7）のUSB2がNative USB。GPIO19=D−、GPIO20=D+。D5はUSB2 VBUS→基板+5V方向で、基板+5V→USB2へは給電できない。CC1/CC2はR4/R8の5.1kΩでGNDへ接続。USB-Cホスト用のRp・電源供給制御はない。

[公式Hardware](https://github.com/WeActStudio/WeActStudio.ESP32S3-AorB/tree/main/ESP32S3-A/Hardware) / [保存回路図](../hardware/reference/weact/README.md)

ESP-IDF v5.5のusb_phy_otg_set_mode()はHOST時にIDDIG、VBUSVALID、AVALIDを内部定数へ接続し、ホスト動作を設定する。従ってWeAct Native端子のVBUSを給電しない構成でも、外部給電した機器とD+/D−で通信する技術的根拠はある。ただしファームウェアによる固定ホスト設定はType-CのCC制御を追加するものではない。[Espressif実装](https://github.com/espressif/esp-idf/blob/v5.5/components/usb/usb_phy.c)

## 具体的な市販候補

|役割|製品|確認済み|残る確認|
|---|---|---|---|
|Type-C→A変換|StarTech USB31CAADGCP|メーカー資料でPassive、USB2.0互換、Type-Cオス→Aメス|WeActでの接続実測、内部回路図は未確認|
|VBUS遮断|PortaPow USB Power Blocker / PPUSBBP1|メーカーがD+/D−/GNDを通し5Vを遮断、USB2.0対応と明記|実物導通と電源投入時の遮断確認。メーカーも機器によって通信不可と注記|
|USBメモリへ外部5V注入|Comprehensive USB3-AMF-PT|USB-Aホスト側オス／機器側メス／電源側オス、USB1.1/2.0/3.0、最大5V 0.9A、Bulk対応|内部回路・逆流防止・電流制限特性は公開記述から確定できない。ホスト側VBUSなしで機能するか確認が必要|

メーカー資料:
- [StarTech USB31CAADGCPデータシート](https://media.startech.com/cms/pdfs/usb31caadgcp_datasheet.pdf)
- [PortaPow PPUSBBP1](https://portablepowersupplies.co.uk/product/usb-power-blocker)
- [Comprehensive USB3-AMF-PT](https://comprehensiveco.com/products/usb-3-0-power-injector-adapter-cable-with-up-to-5gbps-data-transfer.html)

価格比較・国内調達確定・購入は未実施。Comprehensiveの0.9Aは表示上の最大仕様であり、過電流遮断値や各USBメモリの利用可能電流を保証しない。インジェクターの逆流防止を推測せず、別のVBUS遮断器でWeAct側への電源経路を断つ。

## 基板無改造で評価する接続案（未検証）

```text
PC または5V電源 ── WeAct UART端子（従来どおり）

WeAct Native USB-C
  └─ USB31CAADGCP
       └─ PPUSBBP1（ここでVBUSを遮断。D+/D−/GNDのみ通す）
            └─ USB3-AMF-PTのHOST側
                 ├─ DEVICE側 ── USB-Aメモリ
                 └─ POWER側  ── 保護された安定化5V電源
```

WeActへの外部5V逆給電と、PC電源・USBメモリ電源の直接並列を遮断する。GNDは共通で、ガルバニック絶縁ではない。電源は5V固定、必要な過電流保護を備えたものとする。ハブを介さないため、機器が単一MSCならハブドライバーを不要にできる構成。

この構成はNative Type-Cの標準的な接続・電源役割交渉によるものではなく、データ線を利用してS3を固定ホストにする専用評価接続。WeAct側Rdは変わらず、C→Aアダプターを挿しても標準準拠のType-Cホストにはならない。汎用スマートフォンOTG、PDパススルー、Type-Cハブの動作へ一般化しない。[TIのCC役割説明](https://www.ti.com/product/TUSB322I)

## 回路を明確にした自作外付け案

市販インジェクターがホストVBUSを必要とする場合は、外付けケーブル／小基板を製作すれば接続を明確にできる。WeActやGBA親基板を改造する必要はない。

- Native側D−→USB-Aメモリ端子2、D+→端子3、GND→端子4。
- Native側VBUSはメモリのVBUSへ接続しない。
- 外部安定化5V→電流制限付きUSB電源スイッチ→メモリ端子1。
- メモリ電源のコンデンサと必要なESD保護、シールド・短いUSBデータ配線を用意する。
- EspressifのESP32-S3-USB-OTGにはMIC2005Aを使った500mA電流制限回路の公開例がある。これを回路参考とするが、部品・容量・ENの接続を確定した完成設計は今回作成していない。[公式給電回路説明](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-usb-otg/user_guide.html)

## 採用前の評価条件

1. 無通電でD+/D−/GND導通、VBUSの確実な遮断を確認。
2. WeAct/カートリッジへ接続する前に、外部給電でメモリ側5V・Native側への非給電を測定。PC側から外部電源コネクタへの逆供給も確認。
3. S3をUSBホストに固定し、MSC公式例で認識・ファイル書込み・読戻し・ハッシュ一致を検証。消去してよい検証用FAT32メモリを使う。
4. Cプラグ両向き、電源投入順、挿抜、突入時電圧、連続書込みを確認。基板OFF時はメモリ側も切り、データ線経由の部分給電を避ける。
5. その後GBA読出しと組み合わせ、チャンク境界でバスを非選択にしてファイル書込み。USB切断・電源断時に完了扱いにしない。

セルフパワーハブは外部電源があるだけでは成立を保証できない。上流VBUS検知で接続を拒む製品があり、Type-CハブはCC/PD条件も増える。現状では具体的な検証済みハブを採用候補に確定しない。

判断: ハード改版前に上記の外付け構成で単体PoCを行う価値はある。現行PCBへの部品追加は必須とまでは言えないが、未検証のためUSBメモリ保存対応済みとは表示しない。
