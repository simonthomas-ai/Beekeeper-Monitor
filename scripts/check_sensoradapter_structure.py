#!/usr/bin/env python3
"""Independent, conservative structure checks; NOT a replacement for KiCad DRC."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1] / "hardware" / "sensoradapter-v01"
pcb = (root / "sensoradapter-v01.kicad_pcb").read_text()
table = (root / "fp-lib-table").read_text()
foot = root / "Connector_PinHeader_2.54mm.pretty" / "PinHeader_1x04_P2.54mm_Vertical.kicad_mod"
assert foot.is_file(), "Project footprint file missing"
library = foot.read_text()
nickname = "Connector_PinHeader_2.54mm"
part = "PinHeader_1x04_P2.54mm_Vertical"
assert f'(name "{nickname}")' in table, "Library nickname missing from fp-lib-table"
assert "${KIPRJMOD}/Connector_PinHeader_2.54mm.pretty" in table, "Library path is not project-relative"
assert f'(footprint "{part}"' in library, "Footprint definition mismatch"
assert pcb.count(f'(footprint "{nickname}:{part}"') == 2, "Expected exactly two matching connector footprints"
for pad in range(1, 5):
    pattern = rf'\\(pad "{pad}" thru_hole '
    assert len(re.findall(pattern, library)) == 1, f"Library pad {pad} missing or duplicated"
    assert len(re.findall(pattern, pcb)) == 2, f"PCB pad {pad} missing or duplicated"
for number, name in enumerate(("3V3", "GND", "SDA", "SCL"), 1):
    assert f'(net {number} "{name}")' in pcb, f"Missing net {name}"
    assert pcb.count(f'(net {number} ') >= 3, f"Net {name} lacks expected pad/track references"
assert '(layer "Edge.Cuts")' in pcb, "Board outline missing"
print("PASS: footprint library, two connectors, 8 pads, 4 nets, outline")
print("NOTE: KiCad DRC and electrical/fabrication checks remain mandatory")
