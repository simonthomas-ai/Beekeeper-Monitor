"""Regression tests for iNaturalist image quality selection."""
import unittest
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

try:
    from training.inaturalist_media import ALLOWED_HOSTS, original_image_url, is_original_image_url, normalize_if_inaturalist
except ModuleNotFoundError:
    from inaturalist_media import ALLOWED_HOSTS, original_image_url, is_original_image_url, normalize_if_inaturalist


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

    def test_published_review_galleries_use_original_or_hash_bound_local_images(self):
        root = Path(__file__).resolve().parents[1]
        gallery_names = ("all.html", "velutina.html", "crabro.html", "apis.html", "bombus.html", "vespula.html")
        for filename in gallery_names:
            with self.subTest(gallery=filename):
                page = (root / "review" / filename).read_text(encoding="utf-8")
                match = re.search(r"\bconst\s+items\s*=\s*(\[.*?\])\s*;", page, re.S)
                self.assertIsNotNone(match, "embedded candidate array missing")
                items = json.loads(match.group(1))
                self.assertTrue(items, "published gallery must contain reviewed candidates")

                local_originals = 0
                for item in items:
                    image_url = item.get("image_url")
                    self.assertIsInstance(image_url, str)
                    photo_id = str(item.get("photo_id", ""))
                    delivery = item.get("image_delivery")

                    if delivery == "LOCAL_UNMODIFIED_ORIGINAL":
                        local_originals += 1
                        self.assertIn(filename, ("all.html", "velutina.html"))
                        self.assertRegex(
                            image_url,
                            rf"^images/velutina/{re.escape(photo_id)}\.(?:jpe?g|png|webp)$",
                        )
                        self.assertRegex(item.get("original_sha256", ""), r"^[0-9a-f]{64}$")
                    else:
                        self.assertIn(delivery, (None, "REMOTE_INATURALIST_ORIGINAL"))
                        parsed = urlsplit(image_url)
                        self.assertEqual(parsed.scheme, "https")
                        if (parsed.hostname or "").lower() in ALLOWED_HOSTS:
                            self.assertTrue(
                                is_original_image_url(image_url, photo_id),
                                f"{filename}: non-original iNaturalist URL for photo {photo_id}",
                            )

                if filename in ("all.html", "velutina.html"):
                    self.assertGreater(local_originals, 0, "Velutina galleries must expose local original files")
                else:
                    self.assertEqual(local_originals, 0, "non-Velutina galleries must not contain Velutina files")



if __name__ == "__main__":
    unittest.main()
