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
4. **Programmer** tab → expect `EF 40 15` → Read (read twice) → Save backup → Edit → Write.

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

- The UART protocol is the same (115200 baud, `errlog` commands).
- Find TX with a meter: in standby it idles at ≈3.3 V. Confirm GND with continuity.
- Find the NOR near the southbridge and read its marking. `W25Q…JV/V` means 3.3 V; `25U…`, `W25Q…W` and `GD25LQ…` mean 1.8 V and need a 1.8 V adapter.
- Community pad maps exist on repair forums. Use them as a starting point and verify them.
- Slim dumps are 2 MB. NOR Studio reads and edits serial/SKU, but disables Disc ↔ Digital switching for them.
