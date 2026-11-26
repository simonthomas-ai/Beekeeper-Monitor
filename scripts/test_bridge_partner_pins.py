"""Prevent accidental drift between the two BeeKeeper3000 CI checkout pins."""

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github/workflows/gesamttest.yml",
    ROOT / ".github/workflows/cross-repo-integration.yml",
)
PIN = re.compile(r"^\s*ref:\s*([0-9a-f]{40})\s*(?:#.*)?$", re.MULTILINE)

EXPECTED_PARTNER_SHA = "3d6ba57ee0ab937cbce7b254d33496819c7a0868"

def partner_pins(text):
    # Require the immutable SHA directly after the named partner checkout.
    matches = re.findall(
        r"repository:\s*simonthomas-ai/BeeKeeper3000\s*\n"
        r"(?:(?!\n\s*-\s*name:).)*?\n\s*ref:\s*([^\s#]+)",
        text,
        flags=re.DOTALL,
    )
    return matches


class BridgePartnerPinTests(unittest.TestCase):
    def test_same_immutable_partner_revision(self):
        pins = []
        for path in WORKFLOWS:
            with self.subTest(workflow=path.name):
                found = partner_pins(path.read_text(encoding="utf-8"))
                self.assertGreaterEqual(len(found), 1, "Expected at least one partner checkout")
                for pin in found:
                    self.assertRegex(pin, r"^[0-9a-f]{40}$")
                    self.assertEqual(pin, EXPECTED_PARTNER_SHA, "Every integration job must use the reviewed BeeKeeper3000 commit")
                pins.extend(found)
        self.assertTrue(pins, "No BeeKeeper3000 partner pins found")
        self.assertEqual(set(pins), {EXPECTED_PARTNER_SHA}, "Bridge partner revisions drifted")


if __name__ == "__main__":
    unittest.main()
