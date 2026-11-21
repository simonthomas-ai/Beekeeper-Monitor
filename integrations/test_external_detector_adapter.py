"""Tests for vendor-neutral third-party detector metadata mapping."""
import unittest

from integrations.external_detector_adapter import adapt_detection


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "taxon": "vespa_velutina",
            "confidence": 0.83,
            "timestamp": "2026-11-21T17:00:00Z",
            "event_id": "detector-123",
        }

    def convert(self, record=None):
        return adapt_detection(self.record if record is None else record,
                               device_id="station_01", source="external_camera")

    def test_valid_candidate_remains_unverified(self):
        event = self.convert()
        self.assertEqual(event.payload["verification_status"], "unverified")
        self.assertEqual(event.payload["label"], "vespa_velutina")
        self.assertEqual(event.kind, "camera_detection")

    def test_every_supported_taxon(self):
        for taxon in ("vespa_velutina", "vespa_crabro", "apis_mellifera",
                      "bombus_spp", "other_vespidae", "syrphidae", "other_insect"):
            with self.subTest(taxon=taxon):
                self.convert({**self.record, "taxon": taxon})

    def test_rejects_unknown_species(self):
        with self.assertRaises(ValueError):
            self.convert({**self.record, "taxon": "unknown"})

    def test_rejects_media_and_gps(self):
        for extra in ("image", "audio", "latitude", "longitude", "gps", "raw"):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.convert({**self.record, extra: "secret"})

    def test_rejects_invalid_confidence(self):
        for value in (-0.1, 1.01, "0.8", True, float("nan")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.convert({**self.record, "confidence": value})

    def test_rejects_unbounded_identifier(self):
        with self.assertRaises(ValueError):
            self.convert({**self.record, "event_id": "x" * 129})

    def test_rejects_naive_timestamp(self):
        with self.assertRaises(ValueError):
            self.convert({**self.record, "timestamp": "2026-11-21T17:00:00"})

    def test_rejects_extra_status_claim(self):
        with self.assertRaises(ValueError):
            self.convert({**self.record, "verification_status": "confirmed"})


if __name__ == "__main__":
    unittest.main()
