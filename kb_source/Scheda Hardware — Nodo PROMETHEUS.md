# Scheda Hardware — Nodo PROMETHEUS

**Ruolo nel cluster:** Windows + RTX 2060, esecuzione Ollama (modelli `gemma7b_max`, `gemma:7b-instruct`, `gemma2:2b`)
**Hostname:** PROMETHEUS
**IP:** 192.168.8.129
**Ultimo aggiornamento scheda:** 21/08/2026

---

## CPU

| Campo | Valore |
|---|---|
| Modello | Intel Core i9 9900K |
| Code Name | Coffee Lake |
| Core / Thread | 8 / 16 |
| Package | Socket 1151 LGA |
| Tecnologia | 14nm |
| Specifica | Intel Core i9-9900K CPU @ 3.60GHz |
| Family / Model / Stepping | 6 / E / D (Ext. Family 6, Ext. Model 9E, Revision R0) |
| Istruzioni | MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, Intel64, NX, AES, AVX, AVX2, FMA3 |
| Virtualizzazione | Non supportata |
| Hyperthreading | Supportato, Abilitato |
| Velocità stock | 3600 MHz |
| Bus Speed | 99.8 MHz |
| Fan Speed | 915 RPM |
| Temperatura media | 36 °C |

**Cache**
| Livello | Dimensione |
|---|---|
| L1 Data | 8 x 32 KB |
| L1 Instructions | 8 x 32 KB |
| L2 Unified | 8 x 256 KB |
| L3 Unified | 16384 KB |

**Dettaglio core (snapshot)**
| Core | Clock | Moltiplicatore | Bus | Temp | Thread (APIC ID) |
|---|---|---|---|---|---|
| Core 0 | 4390.3 MHz | x44.0 | 99.8 MHz | 37 °C | 0, 1 |
| Core 1 | 798.2 MHz | x8.0 | 99.8 MHz | 38 °C | 2, 3 |
| Core 2 | 1895.8 MHz | x19.0 | 99.8 MHz | 36 °C | 4, 5 |
| Core 3 | 798.2 MHz | x8.0 | 99.8 MHz | 36 °C | 6, 7 |
| Core 4 | 997.8 MHz | x10.0 | 99.8 MHz | 35 °C | 8, 9 |
| Core 5 | 798.2 MHz | x8.0 | 99.8 MHz | 35 °C | 10, 11 |
| Core 6 | 798.2 MHz | x8.0 | 99.8 MHz | 38 °C | 12, 13 |
| Core 7 | 798.2 MHz | x8.0 | 99.8 MHz | 34 °C | 14, 15 |

---

## RAM

| Campo | Valore |
|---|---|
| Slot totali / usati / liberi | 4 / 2 / 2 |
| Tipo | DDR4 |
| Dimensione totale | 32768 MB (32 GB) |
| Canali | Dual |
| Frequenza DRAM | 1329.8 MHz |
| Timing (CL-tRCD-tRP-tRAS) | 19-19-19-43 |
| Command Rate | 2T |

**Utilizzo memoria**
| Campo | Valore |
|---|---|
| Uso memoria | 35% |
| Fisica totale / disponibile | 32 GB / 21 GB |
| Virtuale totale / disponibile | 46 GB / 34 GB |
| Moduli SPD | 2 (Slot #1, Slot #2) |

---

## Scheda Madre

| Campo | Valore |
|---|---|
| Produttore | Gigabyte Technology Co. Ltd. |
| Modello | H310M H (U3E1) |
| Versione | x.x |
| Chipset | Intel Coffee Lake, revisione 0D |
| Southbridge | Intel H370, revisione 10 |
| Temperatura sistema | 34 °C |

**BIOS**
| Campo | Valore |
|---|---|
| Brand | American Megatrends Inc. |
| Versione | F14 |
| Data | 07/07/2020 |

**Tensioni**
| Rail | Valore |
|---|---|
| CPU CORE | 0.708 V |
| MEMORY CONTROLLER | 2.028 V |
| VIN2 | 2.028 V |
| VIN3 | 2.052 V |
| VIN5 | 1.080 V |
| VIN6 | 1.224 V |
| VIN7 | 1.704 V |

**Slot PCI-E**
| Slot | Tipo | Uso | Lanes | Designazione | Caratteristiche |
|---|---|---|---|---|---|
| 0 | PCI-E | In uso | x16 | J6B2 | 3.3V, Shared, PME |
| 1 | PCI-E | In uso | x1 | J6B1 | 3.3V, Shared, PME |
| 2 | PCI-E | In uso | x1 | J6D1 | 3.3V, Shared, PME |
| 3 | PCI-E | In uso | x1 | J7B1 | 3.3V, Shared, PME |
| 4 | PCI-E | In uso | x1 | J8B4 | 3.3V, Shared, PME |

---

## GPU

**Monitor collegato**
| Campo | Valore |
|---|---|
| Nome | HP 22es su NVIDIA GeForce RTX 2060 |
| Risoluzione corrente | 1920x1080 |
| Risoluzione di lavoro | 1920x1040 |
| Frequenza | 60 Hz |
| Stato | Abilitato, Primario |
| Device | \\.\DISPLAY1\Monitor0 |

**NVIDIA GeForce RTX 2060**
| Campo | Valore |
|---|---|
| Produttore | NVIDIA |
| Device ID | 10DE-1F08 |
| Revisione | A2 |
| Subvendor | HP (103C) |
| Bus | PCI Express x16 |
| Tecnologia | 12nm |
| Memoria fisica / virtuale | 2047 MB / 2048 MB |
| Driver | 32.0.16.1074 |
| BIOS GPU | 90.06.33.00.9b |
| Temperatura | 38 °C |
| Clock GPU / Shader / Memoria (idle) | 300 MHz / 405 MHz / 405 MHz |
| Voltaggio | 0.719 V |
| Perf Level 0 (boost) | GPU 435 MHz, Shader 810 MHz |

---

## Storage

**TEAM T253X1960G (SSD)**

| Campo | Valore |
|---|---|
| Capacità | 894 GB (960.197.124.096 bytes) |
| Interfaccia | SATA-III 6.0Gb/s |
| Serial Number | TPBG2010080010400399 |
| Firmware | T0707B0 |
| Tipo device | Fisso |
| ATA Standard | ACS2 |
| LBA | 48-bit |
| Feature | S.M.A.R.T., APM, NCQ, TRIM, SSD |
| RAID | Nessuno |
| Power On Count | 764 |
| Power On Time | 109,6 giorni |
| Stato S.M.A.R.T. | **Good** |

**Attributi S.M.A.R.T. principali**
| ID | Attributo | Raw Value | Stato |
|---|---|---|---|
| 01 | Read Error Rate | 0 | Good |
| 05 | Reallocated Sectors Count | 0 | Good |
| 09 | Power-On Hours | 109d 14h | Good |
| 0C | Device Power Cycle Count | 764 | Good |
| A0 | Uncorrectable Sector Count R/W | 0 | Good |
| A1 | Spare Block validi | 100% | Good |
| A3 | Initial Invalid Block | 74 | Good |
| A4 | Total Erase Count | 53.317 | Good |
| A5 | Maximum Erase Count | 333 | Good |
| A6 | Minimum Erase Count | 2 | Good |
| A7 | Average Erase Count | 38 | Good |
| AF | Program Fail Count | 0 | Good |
| B0 | Erase Fail Count | 0 | Good |
| B1 | Wear Leveling Count | 0 | Good |
| B2 | Unexpected Power Loss | 0 | Good |
| C0 | Power-off Retract Count | 39 | Good |
| C4 | Reallocation Event Count | 0 | Good |
| C5 | Current Pending Sector Count | 0 | Good |
| C6 | Uncorrectable Sector Count | 0 | Good |
| C7 | UltraDMA CRC Error Count | 0 | Good |
| E8 | Endurance Remaining | 100% | Good |
| F1 | Total LBAs Written | 261.863 | Good |
| F2 | Total LBAs Read | 259.717 | Good |

---

## Periferiche

| Dispositivo | Tipo | Vendor | Connessione |
|---|---|---|---|
| Tastiera HID (x4) | Keyboard | Baldor Electric Company | USB |
| HID-compliant Optical Wheel Mouse | Mouse | Logitech | USB |
| HID-Compliant Mouse | Mouse | — | XP-Pen Tablet |
| Mouse compatibile HID | Mouse | — | XP-Pen Tablet |

---

## Rete

| Campo | Valore |
|---|---|
| Adattatore | Realtek Gaming GbE Family Controller #2 |
| Tipo | Ethernet |
| IP Address | 192.168.8.129 |
| Subnet mask | 255.255.255.0 |
| Gateway | 192.168.8.1 |
| DNS preferito | 1.1.1.1 |
| DNS alternativo | 8.8.8.8 |
| DHCP | Disabilitato (IP statico) |
| IP Esterno | 151.82.222.242 |
| NetBIOS over TCP/IP | Abilitato via DHCP |
| NetBIOS Node Type | Hybrid |

**Identità di rete**
| Campo | Valore |
|---|---|
| NetBIOS Name | PROMETHEUS |
| DNS Name | prometheus |
| Membership | Workgroup |
| Workgroup | WORKGROUP |
| Remote Desktop | Disabilitato |

**Condivisione**
| Campo | Valore |
|---|---|
| File and Printer Sharing | Abilitato |
| Simple File Sharing | Abilitato |
| Administrative Shares | Abilitato |
| Modello sicurezza account locali | Classico |
| Network Discovery (profilo privato) | Abilitato |
| Network Discovery (profilo pubblico) | Disabilitato |

**Adattatori aggiuntivi**
| Adattatore | Connessione | IP | Subnet | DHCP |
|---|---|---|---|---|
| Hyper-V Virtual Ethernet Adapter | vEthernet (Default Switch) | 172.28.144.1 | 255.255.240.0 | No |
| Norton VPN Wintun Adapter | Norton VPN | — | — | No |

---

## Note operative

- Nodo Windows dedicato all'inferenza AI locale (Ollama), raggiungibile dagli altri nodi del cluster tramite porta 11434.
- SSD in buone condizioni di salute (0 errori critici, endurance al 100%), nessun intervento richiesto al momento.
- Temperature CPU/GPU nella norma in idle (~34-38°C).
- RAM al 35% di utilizzo con margine disponibile (21 GB liberi).

---

*Prossime sezioni da aggiungere: hardware di **atlas** e **themis**.*
