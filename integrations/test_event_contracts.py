import unittest
from dataclasses import replace
from integrations.event_contracts import HiveEvent

TIME = "2026-11-19T19:00:00+01:00"
CASES = [
    ("camera_detection", {"label": "vespa_velutina_candidate", "confidence": 0.7}),
    ("manual_observation", {
        "label": "observer_report:vespa_velutina",
        "confidence": 0.55,
        "verification_status": "observer_report",
        "origin_event_id": "mobile-event-001",
        "prey_detected": False,
    }),
    ("acoustic_event", {"label": "buzz_candidate", "confidence": 0.4}),
    ("hive_telemetry", {"temperature_c": 22.3, "humidity_pct": 51.2}),
    ("varroa_count", {"mites": 2, "bees_examined": 100}),
]

class EventContractTests(unittest.TestCase):
    def event(self, kind, payload):
        return HiveEvent(kind, "hive-1", TIME, payload)

    def test_roundtrip_all_five(self):
        for kind, payload in CASES:
            with self.subTest(kind=kind):
                event = self.event(kind, payload)
                self.assertEqual(HiveEvent.from_json(event.to_json()), event)

    def test_rejects_untrusted_approvals(self):
        for kind, payload in CASES:
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):
                    self.event(kind, {**payload, "training_approved": True}).validate()

    def test_manual_observation_cannot_claim_camera_or_expert_status(self):
        payload = {
            "label": "observer_report:vespa_velutina",
            "confidence": 0.55,
            "verification_status": "observer_report",
        }
        with self.assertRaises(ValueError):
            self.event("manual_observation", {**payload, "verification_status": "expert_confirmed"}).validate()
        with self.assertRaises(ValueError):
            self.event("manual_observation", {**payload, "verification_status": "unverified"}).validate()

    def test_invalid_confidence(self):
        for value in [-0.1, 1.1, float("nan"), True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.event("camera_detection", {"label": "hornet", "confidence": value}).validate()

    def test_invalid_telemetry(self):
        with self.assertRaises(ValueError):
            self.event("hive_telemetry", {"temperature_c": 21, "humidity_pct": 150}).validate()

    def test_invalid_varroa(self):
        with self.assertRaises(ValueError):
            self.event("varroa_count", {"mites": -1, "bees_examined": 100}).validate()

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            self.event("varroa_count", {"mites": 0, "bees_examined": 0}).__class__(
                "varroa_count", "hive-1", "2026-11-19T19:00:00", {"mites": 0, "bees_examined": 0}
            ).validate()

    def test_reject_unknown_keys(self):
        event = self.event(*CASES[0])
        import json
        raw = json.loads(event.to_json())
        raw["training_approved"] = True
        with self.assertRaises(ValueError):
            HiveEvent.from_json(json.dumps(raw))

    def test_large_input_rejected(self):
        with self.assertRaises(ValueError):
            HiveEvent.from_json(" " * 32769)

if __name__ == "__main__":
    unittest.main()
