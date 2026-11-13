# Internet Download Manager (IDM) Clone Mechanics Sheet

Decompiled from target: `C:\Program Files (x86)\Internet Download Manager\IDMan.exe` (SHA256: `a705c0154fafc7cd509decf165cb6f6c050b6521b40adb6f730dd827c86051c7`).

## 1. Network & Connection Limits
- **Default Maximum Connection Number**: 8 (source: `function 0x4ef8e1` / `.rdata 0x6f3278`).
- **Connection Count Choices**: `1, 2, 4, 8, 16, 24, 32` (source: `function 0x4ef8e1`).
- **Connection Speed Tiers**:
  - High speed: Direct connection (Ethernet/Cable) / Wi-Fi / Mobile 4G / other (source: `.rdata 0x6f3470`, referenced in `function 0x4ef8d2`).
  - Medium speed: ADSL / DSL / Mobile 3G / Wi-Fi / Bluetooth 3.0 / other (source: `.rdata 0x6f34c0`, referenced in `function 0x4ef8c3`).
  - Low speed: Dial Up modem / ISDN / Bluetooth / Mobile Edge / IrDA (source: `.rdata 0x6f3508`, referenced in `function 0x4ef8b4`).

## 2. Speed Limiter
- **Limiter Enabled Key**: `bUseSpeedLimiter` (source: `function 0x5b9eb0` / `0x5b9f30`).
- **Limiter Speed Value**: `psnSpeedLimit` (source: `function 0x5b9eb0` / `0x5b9f30`).
- **Speed Limiter UI string**: `Speed Limiter` (source: `.rdata 0x6f6aa4`, referenced in `function 0x4ef1fd`).
- **Default Speed Limit**: 50 KB/s (estimated).

## 3. Categories & Extensions
From `FUN_004c9380` (`function 0x4c9380`) in `CIDMFoldersTree`:
- **Compressed** (ID 7): `zip rar r0* r1* arj gz sit sitx sea ace bz2 7z` (source: `function 0x4c9380`)
- **Documents** (ID 5): `doc pdf ppt pps docx pptx` (source: `function 0x4c9380`)
- **Music** (ID 2): `mp3 wav wma mpa ram ra aac aif m4a tsa` (source: `function 0x4c9380`)
- **Programs** (ID 1): `exe msi` (source: `function 0x4c9380`)
- **Video** (ID 3): `avi mpg mpe mpeg asf wmv mov qt rm mp4 flv m4v webm ogv ogg mkv ts tsv` (source: `function 0x4c9380`)

## 4. Queues
- **Main download queue**: (source: `.rdata 0x6f7480`, referenced in `function 0x4eefe1`).
- **Synchronization queue**: (source: `function 0x4ec7f0`).

## 5. Transfer Mechanics
- **Chunk Buffer Size**: 32 KB (32768 bytes) per read loop (estimated).
- **Speed Calculation Interval**: 500 ms rolling average update (estimated).
- **Resume Support**: Checks HTTP `Accept-Ranges: bytes` header (source: `.rdata 0x6f6e38`, referenced in `function 0x4ef0ef`).
