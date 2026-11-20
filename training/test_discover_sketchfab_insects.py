import unittest
import urllib.error
from training.discover_sketchfab_insects import discover, normalize, verified_license_slug, TERMS


class SketchfabDiscoveryTests(unittest.TestCase):
    def test_cc0_is_review_only(self):
        item = {"uid": "abcdef1234567890", "name": "Vespa", "license": {"slug": "cc0"},
                "isDownloadable": True, "user": {"username": "creator"}}
        row = normalize(item, TERMS[0])
        self.assertEqual(row["training_approved"], "NO")
        self.assertEqual(row["species_verified"], "NO")
        self.assertEqual(row["rights_verified"], "NO")

    def test_noncommercial_and_missing_license_rejected(self):
        base = {"uid": "abcdef1234567890", "isDownloadable": True}
        for slug in ("cc-by-nc", "cc-by-nd", "", "proprietary"):
            self.assertIsNone(normalize(dict(base, license={"slug": slug}), TERMS[0]))

    def test_not_downloadable_rejected(self):
        self.assertIsNone(normalize({"uid": "abcdef1234567890",
                                   "license": {"slug": "cc0"}, "isDownloadable": False}, TERMS[0]))

    def test_deduplicates_and_limits_queries(self):
        item = {"uid": "abcdef1234567890", "license": {"slug": "cc-by"},
                "isDownloadable": True}
        calls = []
        def fetch(url):
            calls.append(url)
            return {"results": [item, item]}
        rows, errors = discover(fetch)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(calls), len(TERMS))
        self.assertEqual(errors, [])

    def test_uid_license_details_are_resolved_and_cached(self):
        item = {"uid": "abcdef1234567890", "license": {"uid": "cc-by", "label": "Attribution"},
                "isDownloadable": True}
        urls = []
        def fetch(url):
            urls.append(url)
            if "/v3/licences/" in url:
                return {"uid": "cc-by", "label": "Attribution"}
            return {"results": [item, item]}
        diagnostics = {}
        rows, errors = discover(fetch, diagnostics)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["license_slug"], "cc-by")
        self.assertEqual(diagnostics["license_detail_requests"], 1)
        self.assertEqual(len([url for url in urls if "/v3/licences/" in url]), 1)
        self.assertEqual(rows[0]["training_approved"], "NO")

    def test_unverified_or_disallowed_license_uid_fails_closed(self):
        item = {"uid": "abcdef1234567890", "license": {"uid": "custom", "label": "CC0"},
                "isDownloadable": True}
        def fetch(url):
            if "/v3/licences/" in url:
                return {"uid": "cc-by-nc", "label": "Noncommercial"}
            return {"results": [item]}
        rows, errors = discover(fetch)
        self.assertEqual(rows, [])
        self.assertEqual(errors, [])
        self.assertEqual(verified_license_slug(item, lambda url: {}), "")

    def test_license_lookup_failure_does_not_approve(self):
        item = {"uid": "abcdef1234567890", "license": {"uid": "cc0"}, "isDownloadable": True}
        def fetch(url):
            if "/v3/licences/" in url:
                raise OSError("offline")
            return {"results": [item]}
        rows, errors = discover(fetch)
        self.assertEqual(rows, [])
        self.assertEqual(errors, [])

    def test_license_lookup_diagnostics_are_aggregate_only(self):
        item = {"uid": "abcdef1234567890", "license": {"uid": "secretLicenseId"},
                "isDownloadable": True}
        def fetch(url):
            if "/v3/licences/" in url:
                raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
            return {"results": [item]}
        diagnostics = {}
        rows, errors = discover(fetch, diagnostics)
        self.assertEqual(rows, [])
        self.assertEqual(errors, [])
        self.assertEqual(diagnostics["license_lookup_outcomes"]["http_404"], 1)
        self.assertEqual(diagnostics["license_detail_requests"], 1)
        self.assertNotIn("secretLicenseId", str(diagnostics))

    def test_license_lookup_diagnostics_record_response_shape(self):
        item = {"uid": "abcdef1234567890", "license": {"uid": "other"},
                "isDownloadable": True}
        def fetch(url):
            if "/v3/licences/" in url:
                return {"uid": "noncommercial", "label": "Some label"}
            return {"results": [item]}
        diagnostics = {}
        rows, errors = discover(fetch, diagnostics)
        self.assertEqual(rows, [])
        self.assertEqual(errors, [])
        self.assertEqual(diagnostics["license_lookup_outcomes"]["field_uid_str"], 1)
        self.assertEqual(diagnostics["license_lookup_outcomes"]["unverified_detail"], 1)

    def test_model_detail_probe_is_bounded_and_never_approves(self):
        item = {"uid": "abcdef1234567890", "license": {"uid": "unknown"},
                "isDownloadable": True}
        calls = []
        def fetch(url):
            calls.append(url)
            if "/v3/licences/" in url:
                raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
            if "/v3/models/" in url:
                return {"license": {"uid": "cc0", "label": "CC0"}}
            return {"results": [item, item]}
        diagnostics = {}
        rows, errors = discover(fetch, diagnostics)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["license_slug"], "cc0")
        self.assertEqual(rows[0]["training_approved"], "NO")
        self.assertEqual(errors, [])
        self.assertEqual(diagnostics["model_detail_outcomes"]["verified_allowed"], 1)
        self.assertEqual(len([url for url in calls if "/v3/models/" in url]), 1)

    def test_model_detail_noncommercial_stays_rejected(self):
        item = {"uid": "abcdef1234567890", "license": {"uid": "other"},
                "isDownloadable": True}
        def fetch(url):
            if "/v3/licences/" in url:
                raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
            if "/v3/models/" in url:
                return {"license": {"slug": "cc-by-nc"}}
            return {"results": [item]}
        diagnostics = {}
        rows, errors = discover(fetch, diagnostics)
        self.assertEqual(rows, [])
        self.assertEqual(errors, [])
        self.assertEqual(diagnostics["model_detail_outcomes"]["unverified_detail"], 1)

    def test_upstream_failure_is_not_zero_candidates_claim(self):
        rows, errors = discover(lambda url: (_ for _ in ()).throw(OSError("offline")))
        self.assertEqual(rows, [])
        self.assertEqual(len(errors), len(TERMS))


if __name__ == "__main__":
    unittest.main()
