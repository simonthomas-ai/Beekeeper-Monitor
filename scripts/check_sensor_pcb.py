#!/usr/bin/env python3
"""Konservative Strukturprüfung: ersetzt NICHT KiCad ERC/DRC oder Hardware-Abnahme."""
from pathlib import Path
import re

pcb = Path("hardware/sensoradapter-v01/sensoradapter-v01.kicad_pcb")
s = pcb.read_text(encoding="utf-8")
assert s.lstrip().startswith("(kicad_pcb "), "Keine KiCad-PCB-Datei"
assert s.count("(footprint ") == 2, "Erwartet genau zwei vierpolige Anschlüsse"
for name in ("3V3", "GND", "SDA", "SCL"):
    assert f'"{name}"' in s, f"Fehlendes Netz: {name}"
for n in range(1, 5):
    assert len(re.findall(rf'\(pad "{n}" ', s)) == 2, f"Pad {n} fehlt"
    assert len(re.findall(rf'\(segment .*?\(net {n}\)\)', s)) == 1, f"Segment für Netz {n} fehlt"
assert '(gr_rect ' in s and '"Edge.Cuts"' in s, "Platinenumriss fehlt"
print("Strukturprüfung bestanden. KiCad ERC/DRC, Footprint- und elektrische Prüfung stehen aus.")
