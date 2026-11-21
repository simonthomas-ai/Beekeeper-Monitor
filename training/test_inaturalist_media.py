"""Regression tests for iNaturalist image quality selection."""
import unittest

from inaturalist_media import original_image_url, is_original_image_url, normalize_if_inaturalist


class INaturalistMediaTests(unittest.TestCase):
    def test_square_thumbnail_upgraded_to_original(self):
        self.assertEqual(
            original_image_url("https://inaturalist-open-data.s3.amazonaws.com/photos/763034625/square.jpg", 763034625),
            "https://inaturalist-open-data.s3.amazonaws.com/photos/763034625/original.jpg",
        )

    def test_all_known_variants_upgraded(self):
        for variant in ("thumb", "small", "medium", "large", "square"):
            with self.subTest(variant=variant):
                url = f"https://static.inaturalist.org/photos/12/{variant}.jpeg"
                self.assertEqual(original_image_url(url), "https://static.inaturalist.org/photos/12/original.jpeg")

    def test_original_is_idempotent_and_keeps_extension(self):
        url = "https://inaturalist-open-data.s3.amazonaws.com/photos/99/original.png"
        self.assertEqual(original_image_url(url, "99"), url)
        self.assertTrue(is_original_image_url(url, 99))

    def test_reject_photo_id_mismatch(self):
        with self.assertRaises(ValueError):
            original_image_url("https://static.inaturalist.org/photos/10/square.jpg", 11)

    def test_reject_untrusted_hosts_and_unsafe_urls(self):
        for url in (
            "http://static.inaturalist.org/photos/1/square.jpg",
            "https://user:pass@static.inaturalist.org/photos/1/square.jpg",
            "https://example.org/photos/1/square.jpg",
            "https://static.inaturalist.org/photos/1/not-a-size.jpg",
            "https://static.inaturalist.org/photos/1/square.jpg#fragment",
        ):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    original_image_url(url)

    def test_non_inaturalist_https_source_is_not_rewritten(self):
        url = "https://media.example.org/insect/photo.jpg"
        self.assertEqual(normalize_if_inaturalist(url, 2), url)


if __name__ == "__main__":
    unittest.main()
