# PC通信仕様 — 要求のみ、未確定・未実装

UART0→CH343、115200bps 8N1、RTS/CTSなし。HELLO/GET_INFO/READ_HEADER/READ_ROM/READ_SAVE/WRITE_SAVE/ABORTを候補とする。

各フレームに版・種別・連番・絶対バイトoffset・長さ・CRC。チャンクACK/再送、同期前ブートログ破棄、バイナリ開始後非フレームログ禁止。CRC検査後のみファイルへ反映し、未完了は.partial。奇数ROMアドレス、不正長、範囲外、timeoutはエラー。WRITE_SAVEは成功済みIDを認識し再送で二重実行しない。

同期語、CRC多項式・初期値、エンディアン、フィールド幅、ACK/timeout/再送回数、切断検出と冪等性保持期間は実装前に固定する。本ファイルを完成したwire protocolと扱わない。
