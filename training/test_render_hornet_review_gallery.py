import unittest
from render_hornet_review_gallery import render

class ReviewGalleryTests(unittest.TestCase):
    def test_unreviewed_only_and_escape_metadata(self):
        rows = [
            {"training_approved": "NO", "large_review_url": "https://static.inaturalist.org/photos/123/large.jpg", "source_url": "https://www.inaturalist.org/observations/42", "api_taxon": "<script>alert(1)</script>", "observation_id": "42", "photo_id": "123", "api_photo_license": "cc0", "api_attribution": "A & B"},
            {"training_approved": "YES", "api_taxon": "must not appear"},
        ]
        page = render(rows)
        self.assertIn("Candidate count: 1", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script>", page)
        self.assertNotIn("must not appear", page)
        self.assertIn("UNREVIEWED", page)
        self.assertIn("https://static.inaturalist.org/photos/123/large.jpg", page)

    def test_manual_review_export_never_approves_training(self):
        page = render([{"training_approved": "NO", "observation_id": "12", "photo_id": "34"}])
        self.assertIn('data-key="12:34"', page)
        self.assertIn('value="CONFIRMED"', page)
        self.assertIn('value="WRONG_SPECIES"', page)
        self.assertIn('value="UNCERTAIN"', page)
        self.assertIn('"training_approved"', page)
        self.assertIn('note,"NO"', page)
        self.assertIn("vespa-velutina-manual-review.csv", page)

    def test_rejects_external_image_and_source(self):
        page = render([{"training_approved": "NO", "large_review_url": "https://evil.example/pic.jpg", "source_url": "javascript:alert(1)"}])
        self.assertNotIn("evil.example", page)
        self.assertNotIn("javascript:", page)
        self.assertIn("Image URL unavailable", page)

if __name__ == "__main__":
    unittest.main()
