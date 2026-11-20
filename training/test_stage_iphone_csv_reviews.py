import csv
import tempfile
import unittest
from pathlib import Path
from training.stage_iphone_csv_reviews import FIELDS, stage_csv

class CsvGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "review.csv"
        self.row = dict.fromkeys(FIELDS, "")
        self.row.update(photo_id="123",observation_id="99",species_candidate="Vespa velutina",source_url="https://www.inaturalist.org/observations/99",image_url="https://static.inaturalist.org/photos/123/medium.jpg",claimed_license="CC0",license_rechecked="YES",species_verified="YES",image_quality_checked="YES",bounding_box_checked="YES",decision="REVIEWED")
    def tearDown(self):
        self.tmp.cleanup()
    def write(self, rows):
        with self.path.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
    def test_reviewed_never_approves(self):
        self.write([self.row])
        result=stage_csv(self.path)
        self.assertFalse(result["training_eligible"])
        self.assertFalse(result["records"][0]["training_eligible"])
        self.assertIn("independent_expert_signoff",result["records"][0]["expert_checks_required"])
    def test_duplicate_rejected(self):
        self.write([self.row,self.row])
        with self.assertRaises(ValueError):
            stage_csv(self.path)
    def test_external_image_rejected(self):
        self.row["image_url"]="https://example.com/a.jpg"
        self.write([self.row])
        with self.assertRaises(ValueError):
            stage_csv(self.path)
    def test_invalid_decision_rejected(self):
        self.row["decision"]="APPROVED"
        self.write([self.row])
        with self.assertRaises(ValueError):
            stage_csv(self.path)
if __name__=="__main__":
    unittest.main()
