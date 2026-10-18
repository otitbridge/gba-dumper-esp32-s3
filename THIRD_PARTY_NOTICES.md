# Third-party notices for the binary distribution

The application and bootloader contain ESP-IDF v5.5.4 and its bundled components. Original copyright notices and applicable terms are reproduced in LICENSES. The project MIT grant does not replace these terms.

| Component | Source | Included notice |
|---|---|---|
| ESP-IDF / Espressif Wi-Fi, PHY and coexistence libraries | https://github.com/espressif/esp-idf/tree/v5.5.4 | ESP-IDF-Apache-2.0.txt, Espressif-WiFi.txt, Espressif-PHY.txt, Espressif-Coexistence.txt |
| FreeRTOS kernel | ESP-IDF components/freertos/FreeRTOS-Kernel | FreeRTOS-MIT.txt |
| Mbed TLS | ESP-IDF components/mbedtls/mbedtls | mbedTLS-Apache-2.0.txt |
| lwIP | ESP-IDF components/lwip/lwip | lwIP-BSD.txt |
| cJSON | ESP-IDF components/json/cJSON | cJSON-MIT.txt |
| HTTP Parser | ESP-IDF components/http_parser | HTTP-Parser-MIT.txt |
| wpa_supplicant / hostapd | ESP-IDF components/wpa_supplicant | wpa-supplicant-BSD.txt |
| Newlib C library | ESP-IDF / Xtensa toolchain | Newlib-notices.txt |
| GCC runtime / libstdc++ | Espressif Xtensa GCC 14.2.0 | GCC-GPL-3.0.txt, GCC-Runtime-Exception.txt |
| TinyUSB 0.21.0~2 (MIT) | https://github.com/hathach/tinyusb | TinyUSB-MIT.txt |
| esp_tinyusb 2.0.0 (Apache-2.0) | https://components.espressif.com/components/espressif/esp_tinyusb/versions/2.0.0 | esp_tinyusb-Apache-2.0.txt |
| No-Intro game-code and ROM-size metadata | https://datomatic.no-intro.org/ | No-Intro.txt |

The No-Intro catalog derives from the official Nintendo Game Boy Advance DAT version 20260929-130236. Its Data Usage License (2026-09-11) is available at https://datomatic.no-intro.org/terms.html . Game codes and ROM sizes are embedded; no game ROM, SAVE image, cartridge header, Libretro metadata or Dhole database is included.

No external hardware footprints, vendor reference PDFs, build-tool executables or source packages are bundled in this distribution. Historical design files retain their original notices in the corresponding historical commits.

## Public CA certificate data for HTTPS

The ESP-IDF certificate bundle uses Mozilla CA data converted by curl (source date 2025-02-25), under MPL 2.0. The exact, unmodified PEM input is included as `LICENSES/Mozilla-CA-source.pem`; the license text is `LICENSES/Mozilla-MPL-2.0.txt`. The corresponding bundle generator is available in ESP-IDF v5.5.4 `components/mbedtls/esp_crt_bundle`. These files contain public CA certificates, not developer credentials or enrollment keys.

Sources: https://curl.se/docs/caextract.html and https://github.com/espressif/esp-idf/blob/v5.5.4/components/mbedtls/esp_crt_bundle/cacrt_all.pem . This third-party certificate data is provided under its own terms; it does not replace the existing notices for the project and other components.
