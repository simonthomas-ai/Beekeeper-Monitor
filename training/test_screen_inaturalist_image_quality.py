"""Offline tests for transient image-quality screening."""
import io
import unittest
from unittest.mock import patch

from PIL import Image

from training import screen_inaturalist_image_quality as screen


class FakeResponse:
    def __init__(self, body, url, content_type="image/jpeg"):
        self._body = body
        self._url = url
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit=-1):
        return self._body[:limit]

    def geturl(self):
        return self._url


def image_bytes(size=(1200, 900), color=(120, 30, 200)):
    output = io.BytesIO()
    Image.new("RGB", size, color).save(output, format="JPEG", quality=92)
    return output.getvalue()


class ImageQualityScreenTests(unittest.TestCase):
    def row(self, photo_id="42", url=None):
        return {
            "source_id": f"inaturalist-photo-{photo_id}",
            "source_url": "https://www.inaturalist.org/observations/99",
            "photo_id": photo_id,
            "observation_id": "99",
            "species_candidate": "Vespa velutina",
            "dataset_group": "asian_hornet",
            "image_url": url or f"https://static.inaturalist.org/photos/{photo_id}/square.jpg",
            "creator": "Test Observer",
            "creator_login": "test-observer",
            "license": "CC0-1.0",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "license_notice": "no rights reserved",
            "attribution": "Test Observer, no rights reserved (CC0)",
            "review_status": "UNREVIEWED",
        }

    def test_original_is_downloaded_and_dimensions_are_recorded(self):
        url = "https://static.inaturalist.org/photos/42/original.jpg"
        body = image_bytes()
        with patch.object(screen, "_open_original_derivative",
                          return_value=FakeResponse(body, url)) as mocked:
            result = screen.inspect_candidate(self.row())
        mocked.assert_called_once()
        self.assertEqual(result["original_review_url"], url)
        self.assertEqual(result["image_width"], 1200)
        self.assertEqual(result["image_height"], 900)
        self.assertGreater(result["image_bytes"], 0)
        self.assertTrue(result["sharpness_score"] != "")
        self.assertEqual(result["image_quality_status"], "PASS")
        self.assertEqual(result["resolution_tier"], "STANDARD")
        self.assertIn("ranking-only", result["quality_reason"])

    def test_high_resolution_tier_is_metadata_only(self):
        url = "https://static.inaturalist.org/photos/42/original.jpg"
        with patch.object(screen, "_open_original_derivative",
                          return_value=FakeResponse(image_bytes((1800, 1200)), url)):
            result = screen.inspect_candidate(self.row())
        self.assertEqual(result["resolution_tier"], "HIGH_RESOLUTION")
        self.assertEqual(result["image_quality_status"], "PASS")
        self.assertNotIn("training_approved", result)

    def test_small_image_is_rejected_and_never_ranked(self):
        url = "https://static.inaturalist.org/photos/42/original.jpg"
        with patch.object(screen, "_open_original_derivative",
                          return_value=FakeResponse(image_bytes((640, 400)), url)):
            result = screen.inspect_candidate(self.row())
        self.assertEqual(result["image_quality_status"], "REJECT_LOW_RESOLUTION")
        self.assertEqual(result["quality_rank"], "")

    def test_unverified_cc_by_license_fails_closed_without_network(self):
        row = self.row()
        row["license"] = "CC-BY-VERSION-UNVERIFIED"
        row["license_url"] = ""
        with patch.object(screen, "_open_original_derivative") as mocked:
            result = screen.inspect_candidate(row)
        mocked.assert_not_called()
        self.assertEqual(result["image_quality_status"], "UNAVAILABLE")
        self.assertIn("version-unverified", result["quality_reason"])

    def test_exact_cc_by_4_requires_creator_attribution_and_correct_license_url(self):
        row = self.row()
        row["license"] = "CC-BY-4.0"
        row["license_url"] = "https://creativecommons.org/licenses/by/4.0/"
        row["license_notice"] = "CC BY 4.0"
        row["attribution"] = "Test Observer (CC BY 4.0)"
        url = "https://static.inaturalist.org/photos/42/original.jpg"
        with patch.object(screen, "_open_original_derivative",
                          return_value=FakeResponse(image_bytes(), url)) as mocked:
            result = screen.inspect_candidate(row)
        mocked.assert_called_once()
        self.assertEqual(result["image_quality_status"], "PASS")

    def test_exact_cc_by_with_wrong_license_url_fails_before_network(self):
        row = self.row()
        row["license"] = "CC-BY-4.0"
        row["license_url"] = "https://creativecommons.org/licenses/by/3.0/"
        row["license_notice"] = "CC BY 4.0"
        row["attribution"] = "Test Observer (CC BY 4.0)"
        with patch.object(screen, "_open_original_derivative") as mocked:
            result = screen.inspect_candidate(row)
        mocked.assert_not_called()
        self.assertEqual(result["image_quality_status"], "UNAVAILABLE")
        self.assertIn("license URL", result["quality_reason"])

    def test_missing_creator_provenance_fails_closed_without_network(self):
        row = self.row()
        row["creator_login"] = ""
        with patch.object(screen, "_open_original_derivative") as mocked:
            result = screen.inspect_candidate(row)
        mocked.assert_not_called()
        self.assertEqual(result["image_quality_status"], "UNAVAILABLE")
        self.assertIn("rights provenance", result["quality_reason"])

    def test_bad_host_or_photo_id_fails_closed_without_network(self):
        row = self.row(url="https://example.org/photos/42/original.jpg")
        with patch.object(screen, "_open_original_derivative") as mocked:
            result = screen.inspect_candidate(row)
        mocked.assert_not_called()
        self.assertEqual(result["image_quality_status"], "UNAVAILABLE")

    def test_redirect_handler_blocks_untrusted_host_before_following(self):
        handler = screen._OriginalDerivativeRedirectHandler("42")
        request = screen.urllib.request.Request(
            "https://static.inaturalist.org/photos/42/original.jpg"
        )
        with self.assertRaises(screen.HTTPError):
            handler.redirect_request(
                request, None, 302, "Found", {},
                "https://evil.example/photos/42/original.jpg",
            )

    def test_redirect_handler_blocks_thumbnail_before_following(self):
        handler = screen._OriginalDerivativeRedirectHandler("42")
        request = screen.urllib.request.Request(
            "https://static.inaturalist.org/photos/42/original.jpg"
        )
        with self.assertRaises(screen.HTTPError):
            handler.redirect_request(
                request, None, 302, "Found", {},
                "https://static.inaturalist.org/photos/42/square.jpg",
            )

    def test_redirect_handler_allows_original_on_allowlisted_host(self):
        handler = screen._OriginalDerivativeRedirectHandler("42")
        request = screen.urllib.request.Request(
            "https://static.inaturalist.org/photos/42/original.jpg"
        )
        redirect = handler.redirect_request(
            request, None, 302, "Found", {},
            "https://inaturalist-open-data.s3.amazonaws.com/photos/42/original.jpg",
        )
        self.assertEqual(
            redirect.full_url,
            "https://inaturalist-open-data.s3.amazonaws.com/photos/42/original.jpg",
        )

    def test_redirect_must_resolve_to_original_variant(self):
        url = "https://static.inaturalist.org/photos/42/original.jpg"
        redirect = "https://static.inaturalist.org/photos/42/square.jpg"
        with patch.object(screen, "_open_original_derivative",
                          return_value=FakeResponse(image_bytes(), redirect)):
            result = screen.inspect_candidate(self.row())
        self.assertEqual(result["image_quality_status"], "UNAVAILABLE")
        self.assertIn("redirect", result["quality_reason"])

    def test_sharpness_is_ranking_only_and_no_automatic_approval(self):
        url_a = "https://static.inaturalist.org/photos/42/original.jpg"
        url_b = "https://static.inaturalist.org/photos/43/original.jpg"
        body = image_bytes()
        rows = [self.row("42"), self.row("43")]
        responses = [FakeResponse(body, url_a), FakeResponse(body, url_b)]
        with patch.object(screen, "_open_original_derivative", side_effect=responses), \
             patch.object(screen.time, "sleep"):
            results = screen.screen_rows(rows, pause=0)
        self.assertEqual([row["quality_rank"] for row in results], [1, 2])
        self.assertTrue(all(row["image_quality_status"] == "PASS" for row in results))
        self.assertFalse(any("training_approved" in row for row in results))


if __name__ == "__main__":
    unittest.main()
