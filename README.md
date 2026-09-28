# GBA専用ダンパー V1 — WeAct ESP32S3-A N16R2

**状態：4層配線・AD6短縮・シルク最終整理・最終DRCまで完了。WeAct版ガーバー・ドリル・CPL出力と照合まで完了。JLCPCBへ5枚発注済み（2026-09-28）。実機未検証。**

正本ブランチは `main`（WeAct版）。識別子 `WEACT_ESP32S3_A_N16R2_GBA_V1_20260928`。WeAct本体の部品取り外し・パターンカットなし。N16R8やESP32S3-Bには適用しない。

- [最終シルク確認PNG](output/pcb/final_review/front_silk.png) / [出力前レビュー](docs/fabrication_review.md)
- [回路図SVG](output/schematic/gba_dumper.svg) / [PNG](output/schematic/gba_dumper.png) / [KiCad回路図](hardware/gba_dumper.kicad_sch)
- [配線概要PNG](output/pcb/routed/routing_overview.png) / [GND面](output/pcb/routed/ground_plane.png) / [配線記録](docs/routing.md) / [配線長比較](docs/routing_comparison.md)
- [配線前配置図PNG](output/pcb/placement.png) / [SVG](output/pcb/placement.svg) / [PCB](hardware/gba_dumper.kicad_pcb)
- [全体BOM](hardware/bom/preliminary.csv) / [調達表](hardware/bom/assembly_parts.csv) / [PCBA BOM](hardware/bom/jlcpcb_pcba.csv)
- [ピンマップ](docs/pinmap.md) / [ファームウェア定義](firmware/main/pinmap.hpp)
- [設計仕様](docs/design_spec.md) / [移行レビュー](docs/weact_migration_review.md)
- [ソケット・機械条件](docs/weact_footprint.md) / [配置条件](docs/pcb_placement.md) / [製造ルール](docs/manufacturing_rules.md)
- [未完了事項](docs/open_items.md) / [立上げ手順](docs/bringup.md)

UART0 TX43/RX44→CH343。GPIO35/36はSAVEデータ兼上位アドレス、GPIO37は/WR。GPIO19/20/48はGBAバスに接続しない。Native USBは本V1では使わずPCはUART端子へ接続。JP1初期OPEN、JP2通常CLOSE。カートリッジ・ジャンパ・子基板の挿抜はUSBを抜いてから。

基板のランド表面仕上げは**鉛含有HASL（通常のHASL）**を指定。注文番号 **[order-id-redacted]**、送料・SMT実装込み **4,609円**でユーザーが注文完了。[注文記録・費用内訳](docs/jlcpcb_order_20260928.md)を参照。

R1〜R33・C1/C2の35個を上面PCBA（5品種、既選定Basic）。J1/J2/J3/JP1/JP2は手はんだ。ソケットは秋月110073の40極品2本から22極を各1本切り出す。WeAct付属ヘッダとの嵌合は到着後確認。ファームウェア成果物はピン定義のみで、ドライバ・ホストは未実装。

旧FNK0099設計は過去コミット `6403600` に保持。[旧製造データ・検査履歴](archive/fnk0099/README.md)はWeAct版に使用禁止。WeAct用Gerber・ドリル・CPLは[製造レビュー出力](output/fabrication_review/README.md)を参照。

## 再生成と確認

KiCad 10.0.5のCLIと、pcbnewを含むKiCad同梱Pythonを使う。`KICAD_PYTHON`と`KICAD_CLI`は各環境の実行パスに設定する。

```sh
python3 tools/generate_design.py
"$KICAD_CLI" sch export netlist --format kicadxml -o hardware/verification/gba_dumper.xml hardware/gba_dumper.kicad_sch
"$KICAD_CLI" sch erc -o hardware/verification/erc.rpt hardware/gba_dumper.kicad_sch
"$KICAD_PYTHON" tools/generate_placement.py
"$KICAD_PYTHON" tools/configure_manufacturing.py
"$KICAD_PYTHON" tools/sync_pcb_metadata.py
"$KICAD_CLI" pcb drc --schematic-parity --format json -o hardware/verification/placement_drc.json hardware/gba_dumper.kicad_pcb
python3 tests/hardware/check_design.py
"$KICAD_PYTHON" tests/hardware/check_placement.py
python3 tests/hardware/check_manufacturing.py
c++ -std=c++17 -Wall -Wextra -pedantic -fsyntax-only tests/pinmap/compile.cpp
```

生成元に変更を反映してから再生成する。配置スクリプトは配線済み基板への上書きを拒否する。配線前の描画手順はtools/export_review.sh。現在の配線画像はtools/export_routing.shで出力する。WeAct向けの配線スクリプトをtoolsへ追加。旧座標に依存するFNK版と製造出力スクリプトはarchiveへ保存。配線済みPCBに対して上記のgenerate_placement.pyは実行せず、配線の再生成は配線前コミットef14faeを別作業コピーに展開して行う。

現行配線の検査はKiCad同梱Pythonでtests/hardware/check_routing.pyとtests/hardware/check_route_lengths.py。前工程の確認記録はdocs/weact_migration_review.md。部品位置・銅箔は維持し、シルク文字のみ更新済み。tests/hardware/check_silkscreen.pyで変更範囲を検証する。

## ライセンス

自作ハードウェア・設計文書はCERN-OHL-P-2.0、ソフトウェアはMIT。[適用範囲と本文](LICENSE.md) / [第三者資料の表示](THIRD_PARTY_NOTICES.md)。実機未検証で、現時点では動作するダンパーファームウェアを提供していません。

## 公開履歴と参照資料

この公開版は新しいGit履歴で開始します。文書中の過去コミットIDは非公開の開発履歴を指し、この公開リポジトリでは参照できません。旧設計の内容はarchive/fnk0099を参照してください。WeAct公式参考PDFは同梱せず、hardware/reference/weact/sources.jsonの公式リポジトリから取得してください。設計・製造ファイルは発注時の内容を維持しています。
