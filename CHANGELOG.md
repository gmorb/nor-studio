# Changelog

## v1.2.0

### Added
- PS5-style light bar along the top edge: blue while reading/writing, a white flash on success, amber on errors.
- IBM Plex Mono (embedded) for hex, serials, MACs and the terminal, so they look the same on every OS.
- Snappier motion: buttons press down slightly, notifications and dialogs open with a quick ease-out, all respecting reduced-motion settings.
- Polish: hover effects only on mouse devices, themed dropdown arrows, fixed-width numbers, scroll areas don't drag the page, the tab title follows the active section.

### Fixed
- Switching tabs no longer makes the background flash brighter and then dim: tabs now switch instantly.
- Closing or reloading the page while the programmer is writing now asks for confirmation (a half-written NOR can stop a console booting).
- "Run list…" is locked while error codes are being read, and reading is locked while a list runs.
- Error-code rows no longer overflow the screen on phones.
- "Copied" notifications no longer flash the light bar, and at most 4 notifications stack at once.
- The health check no longer warns "WiFi MAC copies differ" on healthy dumps. The three addresses at 0x1C73C0 are a consecutive block (base, +1, +2), not copies. The check now confirms they're sequential, and editing the WiFi MAC writes base, +1 and +2 instead of the same address three times.
- Changing the model number to a different length (e.g. dropping the trailing letter of `CFI-2015 A01X`) now shows an amber warning and is repeated in the save confirmation, like serial-length changes.
- Slim model numbers with a space (e.g. `CFI-2015 A01X`) can be edited without the space being stripped.
- NOR editor shows all three firmware values (installed, minimum, factory) with a note on what they mean and how to reinstall system software in Safe Mode. They're read-only on purpose.
- Verified against two real EDM‑041 dumps: every field parses correctly and the health check passes cleanly.
- On phones, the background glow no longer stretches while scrolling (the backdrop is now a fixed full-height layer instead of a fixed background).

### Hardware guide
- NOR chip diagrams (EDM‑010/020 and EDM‑041) show the CH341A pin for every chip pin (CS, MISO, MOSI, CLK, GND, 3.3V), color-coded to match the wiring guide, with a toggle to hide them.
- New "CH341A wiring" guide: direct wiring from the programmer header to the chip (MISO→DO, MOSI→DI), alias names, chip-ID troubleshooting, and when to leave the 3.3 V wire off (powered-board method).
- EDM‑041 NOR confirmed: Winbond W25Q16JV (3.3 V, SOIC‑8) next to the southbridge, with location and pinout diagram and board photos.
- The empty tag next to "Advanced" in the NOR editor no longer shows.

## v1.1.0

### Added
- UART: decodes every error‑log field (power state, OS state, boot cause, active devices, SoC and ambient temperature, time between entries).
- UART: console detection from the ready banner, a "Detect console" serial break, and a command‑list runner (.txt).
- UART: reads up to 64 log slots, with hex slot indexes from 10 upwards.
- Database: code‑family pattern matching (e.g. `8005xxxx`, `C001xxxx`) with a "family match" badge.
- NOR: OS flags (IDU, manufacturing mode, boot message mode, ABL debug print, BIOS and MP memory tests) shown and editable in both NVS copies.
- NOR: motherboard serial, LAN MAC and Wi‑Fi MAC editing (all 3 copies), behind an Advanced section with warnings.
- NOR: health check for SLB2 firmware containers (EMC IPL A/B, USB PDC A/B), Wi‑Fi MAC copies and OS flag copies.
- Hardware Guide: EDM‑010/020 UART map in real board orientation (JL5109 = GND), plus new EDM‑03x and EDM‑04x+ (Slim) UART pinouts.

### Fixed
- Error codes stored as patterns in the database were never matched.

## v1.0.0: first release

### Added
- NOR Editor: console info (serial, motherboard serial, SKU, region, board, MACs, firmware, slot, IDU), MD5/SHA‑256, health check, Disc ↔ Digital, serial/SKU editing with a byte diff, compare two dumps.
- CH341A Programmer (WebUSB): chip detection with voltage hints, read twice and compare, automatic backup, sector‑level smart write, full verify, write‑protect detection, demo mode.
- UART (Web Serial): full error log read, decoded descriptions, clear log, terminal with auto‑checksum and history, report export, demo mode.
- Error code database: HTTPS download, offline cache, import of `errorDB.xml`, CST JSON or CSV, personal notes.
- Hardware Guide: EDM‑010/020 NOR pinout and UART pad map, in‑circuit vs chip‑off guidance, Slim tips.
- Voltage safety checks and 3.3 V‑mod warnings for the CH341A and UART adapters.

### Fixed (compared with PS5 NOR Modifier)
- Database download error: the dead plain‑HTTP source was replaced, and real errors are shown.
- Board variant change never applied (region text was appended before the search).
- Digital edition detection read the wrong offset.
- `.BIN` uppercase extension rejected.
- UART reads could hang with no timeout.
- Whole‑file find/replace narrowed to the NVS area.
