# Hardware guide

> ⚠️ Confirm every point with a multimeter before connecting anything. Wrong voltage or a swapped wire can permanently damage the console. Use at your own risk.

## Quick answer: in‑circuit or chip‑off?

| Method | When it works | Notes |
|---|---|---|
| **UART pads** | Reading and clearing error codes only | UART goes to the southbridge. It **cannot** read or write the NOR. |
| **SOIC‑8 clip, in‑circuit** | Often, on EDM‑010/020 | The clip back‑powers the 3.3 V standby rail that also feeds the southbridge. Hold `/SSB_RESET` low if reads are unstable. |
| **Lift pin 8 (VCC)** | When in‑circuit reads are unstable | Isolates the chip from the rest of the rail |
| **Chip‑off** (SOP8 adapter) | Always | The most reliable method; reflow it back in the same orientation |

Always read **twice** and compare. NOR Studio does this for you.

---

## Rebuilding from a donor NOR

> **If the rebuilt NOR still gives 3 beeps on plug-in:** check the health check for "Identity block starts with … instead of 0x30". A backup read from a dying chip can have a corrupted byte at 0x1C4000. Restore identity now keeps 0x30, but rebuilds made before this fix may carry the bad byte. Also remember the error log is stored on the NOR: after writing a donor dump, the codes you read are the donor's until you clear the log.

Repair technicians report that a known-good donor dump from the **same board type** (same EDM revision and components) can bring back a console whose own NOR is lost or corrupted. Restoring the console's own identity afterwards keeps WiFi, controllers and the disc drive pairing happy.

- Always try the console's **own** dump first if you have one that reads cleanly twice and passes the health check.
- The LAN MAC at `0x1C4020` has **two check bytes at `0x1C403E`** that can't be recalculated. Changing the MAC without them makes the console beep 3 times. Copy the whole `0x1C4000–0x1C403F` block (board ID + LAN MAC + check) from the original dump as one unit.
- In NOR Studio: open the donor dump → Edit → **Restore identity from original dump** → choose the console's original dump → Apply → review the diff → Save.

## Wiring a CH341A straight to the chip

For soldered wires, a chip-off on a breakout, or when the clip won't fit. Every PS5 board covered here uses the same Winbond W25Q16JV, so the mapping is the same.

| CH341A label | Flash pin | Why |
|---|---|---|
| CS | **1** /CS | Chip select |
| MISO | **2** DO / SO | Data from the chip *out* to the programmer *in* |
| MOSI | **5** DI / SI | Data from the programmer *out* to the chip *in* |
| CLK | **6** CLK | Also printed SCK / SCLK |
| GND | **4** GND | Connect first |
| VCC 3.3 V | **8** VCC | **Only when the board is unplugged**; leave it off on a powered board |

**Why the names don't match:** SPI is named from the programmer's side. MISO ("master in, slave out") goes to the chip's output DO; MOSI ("master out, slave in") goes to the chip's input DI. Don't cross them like UART's TX→RX. Aliases: DO = SO = IO1 = Q · DI = SI = IO0 = D · CS = CE# = SS · CLK = SCK = SCLK. If your programmer prints DO/DI instead of MISO/MOSI, wire it one way and check the chip ID. If it reads `FF FF FF` or `00 00 00`, swap those two wires.

**/WP (pin 3) and /HOLD (pin 7):** pulled up on the board, so leave them alone in-circuit. On a chip-off, tie both to VCC.

### Two ways to power the chip

- **Recommended: board unplugged, programmer powers the chip.** Connect all six wires. If reads are unstable, ground JL5110 (/SSB_RESET) on EDM-010/020, or lift pin 8, or remove the chip. This is the only method for EDM-03x/04x.
- **Advanced: board powered in standby, programmer doesn't.** Connect CS, MISO, MOSI, CLK and GND only. **Never connect the programmer's 3.3 V wire here**: two supplies on one rail can damage the programmer, the chip or the board. In standby the southbridge also drives the SPI lines, so it **must be held in reset** (JL5110 to GND on EDM-010/020) or reads garble and writes can corrupt the NOR. Not for EDM-03x/04x until a reset point is known.

**Check with the app:** `EF 40 15` = correct. `FF FF FF` = check MISO→2 and CS→1. `00 00 00` = no power or GND, or MOSI/MISO swapped. Changing or odd IDs = loose wire or clock; shorten wires and re-solder CLK→6.

**Not sure which wire?** When the ID fails, press **Find the bad connection** in the Programmer tab. With a multimeter, it checks GND and VCC, then switches CS, CLK and MOSI high and low for you to measure on the chip's legs, and shows MISO live while you briefly bridge pin 2 to pin 4. It finishes by naming the connection that failed.

## EDM‑010 / EDM‑020 (CFI‑10xx / 11xx)

Source: Sony board service manuals for the CFI‑1000/1100 series (schematic sheets "SFlash 2MB" and "MISC", printed wiring boards side A and side B).

### NOR chip: IC5001

- **Part:** Winbond **W25Q16JVSNIM**: 16 Mbit (2 MB), **3.3 V**, SOIC‑8. JEDEC ID `EF 40 15`.
- **Location:** top side (Side A), immediately right of the southbridge **IC5006**.
- **Supply:** `3.3V_SS_PG1` (the southbridge's standby rail).

| Pin | Name | Connection |
|---|---|---|
| 1 | /CS | `/S50_SSB_SF_CS`, 4.7 kΩ pull‑up (R5074) |
| 2 | DO (MISO) | 47 Ω (R5058) → `S50_SSB_SF_SIO1` |
| 3 | /WP | 4.7 kΩ pull‑up to 3.3 V (R5077) |
| 4 | GND | GND |
| 5 | DI (MOSI) | 47 Ω (R5060) → `S50_SSB_SF_SIO0` |
| 6 | CLK | `S50G_SSB_SF_SCLK` |
| 7 | /HOLD | 4.7 kΩ pull‑up to 3.3 V (R5078) |
| 8 | VCC | `3.3V_SS_PG1` |

This is a 3.3 V chip, so no 1.8 V adapter is needed. The CH341A must still have the **3.3 V mod**.

**On the board (EDM-010 photos):** IC5001 is marked `25Q16JVNIM` and sits right of the southbridge, which is marked `SIE CXD90061GG` on this board, with a column of 4 small parts between them. With the chip's text upright, the dot (pin 1) is at the lower left: pins 1–4 along the bottom, 5–8 along the top from right to left. That's the same orientation as EDM-041.

<p>
  <img src="boards/edm-010-nor-and-southbridge.jpg" alt="EDM-010: southbridge CXD90061GG with the Winbond 25Q16JVNIM NOR (IC5001) to its right" width="49%">
  <img src="boards/edm-010-nor-closeup.jpg" alt="EDM-010 NOR close-up: Winbond 25Q16JVNIM, pin 1 dot at lower left" width="49%">
</p>

> **Southbridge versions:** EDM-010 uses `CXD90061GG`, EDM-041 uses `CXD90069GG` (both seen on users' boards). When replacing a southbridge, fit the same part number as the original: the NOR has to match the southbridge that's fitted.

### UART / service test pads: JL5101–JL5110

Bottom side of the board, just below a metal shield can. A small black ribbon connector sits on the left and a white 3‑pin connector on the right.

As seen on the board (this is the service manual drawing rotated 180°):

```
          [ metal shield can ]
         JL5106   JL5101   JL5109      ← 3.3V FC · 3.3V STBY · GND
JL5102   JL5108   JL5110   JL5105      ← n/c · FC TX · /SSB_RESET · PS5 TX
         JL5107   JL5103   JL5104      ← FC RX · strap · PS5 RX
```

The right‑hand column is **GND / TX / RX** from top to bottom. That matches the reference photo in [Console Service Tool](https://github.com/amoamare/Console-Service-Tool/blob/master/Resources/UARTLocations/PlayStation5/EDM_010_020_UART.png).

| Pad | Net | Use |
|---|---|---|
| JL5109 | GND (no net in schematic; confirm continuity) | → adapter **GND** |
| JL5105 | `SSB_UART0_TX` | → adapter **RX** |
| JL5104 | `SSB_UART0_RX` | → adapter **TX** |
| JL5101 | `3.3V_SS_PG1` | Measure only: ≈3.3 V in standby. Sits right next to GND, so do **not** bridge it. |
| JL5110 | `/SSB_RESET` | Hold to GND while programming the NOR in‑circuit |
| JL5103 | `SSB_BOOT_STRAP_1` | Leave alone |
| JL5106–JL5108 | SSD flash controller UART | Not the error log |

### Wiring checklist

**UART**
1. Adapter at 3.3 V. Wire TX→RX, RX→TX and GND only.
2. AC in, console in standby → NOR Studio **UART** tab → Read error codes.

**Programmer (in‑circuit)**
1. AC unplugged. Wait a minute for the rails to discharge.
2. Clip on IC5001, pin 1 to pin 1. 3.3 V‑modded CH341A.
3. If the ID or the reads are unstable, connect JL5110 to GND for the duration.
4. **Programmer** tab → expect `EF 40 15` → Read (read twice) → Save backup → Edit → Write. Write asks whether to read first (recommended) or write without reading.

---

## EDM‑03x (EDM‑030 / 031 / 033)

UART pads sit in a cluster near the board edge, below a black connector, with fuse **F5402** printed to the right. From the [Console Service Tool reference photo](https://github.com/amoamare/Console-Service-Tool/blob/master/Resources/UARTLocations/PlayStation5/EDM_03x_UART.png):

```
 GND   ·   TX   ·        ← top row: 1st = GND, 3rd = PS5 TX → adapter RX
  ·    ·   RX   ·        ← second row: 3rd = PS5 RX → adapter TX
```

No EDM‑03x schematic is included here. Confirm TX (≈3.3 V idle in standby) and GND (continuity) with a meter. For the NOR, read the chip marking next to the southbridge and follow the same voltage rules as below.

## EDM‑04x (Slim: EDM‑040 / 041 / 044)

### UART pads (EDM‑040 / 041 / 044 and later)

A cluster of 10 round pads near the curved board edge by the fan cut‑out. A metal screw bracket and the two WiFi antenna cables (blue and white) are just above and to the right, and a long ribbon connector runs below. From a community reference photo:

```
        ·    ·              ← top row (2 pads)
  TX   RX    ·    ·         ← middle row: 1st = PS5 TX → adapter RX, 2nd = PS5 RX → adapter TX
  ·    ·    GND   ·         ← bottom row: 3rd = GND
```

No official schematic or boardview is included here. Pinouts from launch boards **do not** carry over. Confirm each pad with a meter before soldering.

### NOR chip (confirmed on EDM‑041)

- **Part:** Winbond **W25Q16JV**, top marking `25Q16JVNIM`: 2 MB, **3.3 V**, SOIC‑8, JEDEC ID `EF 40 15`. It's the same chip as EDM‑010/020.
- **Location:** right of the southbridge (`SIE CXD90069GG`), with a column of 8 small resistors between them.
- **Pin 1:** the dot. With the text upright it's the lower‑left pin. Pins 1–4 run along the bottom (CS, DO, WP, GND) and 5–8 along the top from right to left (DI, CLK, HOLD, VCC).
- Use a 3.3 V‑modded CH341A with no 1.8 V adapter. The reset point isn't mapped for EDM‑04x yet, so if in‑circuit reads are unstable, lift pin 8 or remove the chip and use an SOP8 adapter.

<p>
  <img src="boards/edm-041-nor-and-southbridge.jpg" alt="EDM-041: southbridge CXD90069GG with the Winbond 25Q16JVNIM NOR to its right" width="49%">
  <img src="boards/edm-041-nor-closeup.jpg" alt="EDM-041 NOR close-up: Winbond 25Q16JVNIM, pin 1 dot at lower left" width="49%">
</p>

- The UART protocol is the same (115200 baud, `errlog` commands).
- Find TX with a meter: in standby it idles at ≈3.3 V. Confirm GND with continuity.
- Find the NOR near the southbridge and read its marking. `W25Q…JV/V` means 3.3 V; `25U…`, `W25Q…W` and `GD25LQ…` mean 1.8 V and need a 1.8 V adapter.
- Community pad maps exist on repair forums. Use them as a starting point and verify them.
- Slim dumps are 2 MB. NOR Studio reads and edits serial/SKU, but disables Disc ↔ Digital switching for them. Two real EDM‑041 dumps, one disc (`CFI-2015 A01X`) and one digital (`CFI-2015 B01X`), both carry the same edition flag `22 01 01 01` at 0x1C7010. On Slims only the model number's A/B letter differs.
- Real EDM‑041 dumps verified field by field: serial, motherboard serial, SKU, board, LAN MAC, wireless MAC block (base, +1, +2), Kiban ID, firmware, OS flags, EAP magics and the SLB2 containers all parse correctly. Note that the +0x3000 backup area is empty (FF) on these Slim dumps.


## 3 beeps as soon as it's plugged in

The southbridge checks the NOR before anything else powers up. When it doesn't like what it finds, it beeps three times and stops. Work through these in order:

1. **Connect UART and plug in.** If `$$ [MANU] UART CMD READY` appears, the southbridge is running and reading the NOR, so the problem is the NOR's contents. No banner at all points to a missing or dead NOR, or the southbridge.
2. **Read the codes, then clear the log.** Clear log, unplug for 10 seconds, plug back in without pressing power. A full log can cause the beeps on its own.
3. **Written a donor dump? Those codes aren't yours.** The error log is stored on the NOR, so the donor's history comes with it. NOR Studio tags those entries "In loaded dump" when the same dump is open in the NOR Editor.
4. **Check the dump in the NOR Editor.** The health check verifies the identity block checksum: the 16-bit little-endian words from 0x1C4000 to 0x1C41FF must add up to zero. If it fails, the console beeps 3 times. When one corrupted byte is the cause (like 0x00 instead of 0x30 at 0x1C4000 on a backup from a failing chip), the app fixes it in one click.
5. **Rebuild with Restore identity**, not by editing fields one at a time. The LAN MAC sits inside the checksummed block. Make sure the donor is set for the same HDMI chip as your board (0x1C4062: `01` Realtek RTD2175P, `FF` Panasonic MN864739); NOR Studio warns you if it isn't.
6. **Read the chip back in-circuit and Compare** with the file you wrote, to rule out soldering and the write.
7. **Beeps only when you press power?** Different fault: check the power/eject button board's flex cable first.

**The case this came from (EDM-041 Slim):** the NOR chip died. A new chip with the console's own backup still beeped, and so did a donor dump with the console's identity restored. Writing the donor unmodified booted, which proved the board was fine; every UART code had come with the donor dump. The console's own backup had `00` at 0x1C4000 instead of `30`, corrupted by the dying chip, which broke the identity block checksum. Donor dump + own identity + `30` booted on the console's own serial and MACs.

### Finding and vetting a donor dump

NOR Studio doesn't host dumps: every dump contains Sony's firmware and another console's serial, MACs and keys. Repair forums share them in their firmware threads (for example BadCaps and TronicsFix). Before using one:

- Same board family: Slim for Slim (EDM-04x), launch for launch (EDM-010/020), EDM-03x for EDM-03x.
- Open it in the NOR Editor: no failed checks, including the identity block checksum.
- Same HDMI chip as your board: Console information shows it (Realtek RTD2175P or Panasonic MN864739).
- Read its error log in the health check. APU, power or thermal faults mean that console was faulty. The data can still be fine, but a clean log is safer.
- Keep an untouched copy, so you can tell a bad board from a bad rebuild.
- Put your own identity back with **Restore identity** before you use the console. A donor written as-is shares its serial and MACs with another console, and anything tied to that serial (a PSN ban, for example) applies to both.


## HDMI chip swap (Realtek → Panasonic)

Slim boards ship with one of two HDMI chips, and the NOR says which one to expect: 0x1C4062 = `01` Realtek RTD2175P, `FF` Panasonic MN864739. Converter boards such as [BGA Tech's Realtek → Panasonic mod](https://github.com/BgaTech-Brazil/Realtek-Panasonic) replace a dead Realtek chip with a Panasonic one, so the NOR must be switched too.

BGA Tech's method uses a base file: a known-good Panasonic NOR for the board family, with the console's serial and motherboard serial copied in. NOR Studio's Restore identity does the same and also copies the MAC addresses, model and Kiban ID, so converted consoles don't share the base file's MACs.

1. Read and save the console's original NOR.
2. Get the Panasonic base file for your board family from the converter's maker.
3. Open the base file in the NOR Editor. Console information should show **HDMI chip: Panasonic MN864739**, and the health check should pass.
4. **Restore identity** from the original dump, everything ticked. The "Different HDMI chip" note is expected: the base file's Panasonic setting stays.
5. Save, write and verify. Fit the converter, connect UART, clear the log (it came with the base file), and test.

The firmware version comes from the base file and may be older than the console's system software: update once it boots.
