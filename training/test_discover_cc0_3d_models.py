import io
import json
import unittest
import urllib.error
import tempfile
from pathlib import Path

from discover_cc0_3d_models import candidates, fetch_all, _write_status


class CC0ModelDiscoveryTests(unittest.TestCase):
    def test_no_beet_or_beef_false_positives(self):
        rows = [{"row": {"title": title, "license": "CC0-1.0", "media_usage_access": "CC0"}} for title in ("De la Fuente sugar beet knife", "Bully beef can opener")]
        self.assertEqual(candidates(rows), [])

    def test_only_cc0_and_no_approvals(self):
        rows = [
            {"row": {"package_id": "1", "title": "Vespa crabro", "license": "CC0-1.0", "media_usage_access": "CC0", "mesh_url": "https://example.org/model.glb"}},
            {"row": {"package_id": "2", "title": "Vespa velutina", "license": "CC-BY-NC", "media_usage_access": "Restricted"}},
            {"row": {"package_id": "3", "title": "Chair", "license": "CC0-1.0", "media_usage_access": "CC0"}},
        ]
        result = candidates(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["package_id"], "1")
        self.assertEqual(result[0]["training_approved"], "NO")
        self.assertEqual(result[0]["species_verified"], "NO")
        self.assertEqual(result[0]["geometry_verified"], "NO")

    def test_fetch_retries_gateway_502_then_succeeds(self):
        calls, delays = [], []

        def opener(request, timeout):
            calls.append((request.full_url, timeout))
            if len(calls) == 1:
                raise urllib.error.HTTPError(request.full_url, 502, "Bad Gateway", {}, io.BytesIO(b""))
            return io.BytesIO(json.dumps({"rows": [], "num_rows_total": 0}).encode())

        self.assertEqual(fetch_all(urlopen=opener, sleep_fn=delays.append), [])
        self.assertEqual(len(calls), 2)
        self.assertEqual(delays, [0.5])

    def test_fetch_retries_rate_limit_and_honours_bounded_retry_after(self):
        calls, delays = [], []

        def opener(request, timeout):
            calls.append(request.full_url)
            if len(calls) == 1:
                raise urllib.error.HTTPError(
                    request.full_url, 429, "Too Many Requests",
                    {"Retry-After": "120"}, io.BytesIO(b""),
                )
            return io.BytesIO(json.dumps({"rows": [], "num_rows_total": 0}).encode())

        self.assertEqual(fetch_all(urlopen=opener, sleep_fn=delays.append), [])
        self.assertEqual(len(calls), 2)
        self.assertEqual(delays, [30.0])

    def test_permanent_http_failure_is_not_retried(self):
        calls, delays = [], []

        def opener(request, timeout):
            calls.append(request.full_url)
            raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, io.BytesIO(b""))

        with self.assertRaises(urllib.error.HTTPError):
            fetch_all(urlopen=opener, sleep_fn=delays.append)
        self.assertEqual(len(calls), 1)
        self.assertEqual(delays, [])

    def test_retry_limit_is_bounded(self):
        calls, delays = [], []

        def opener(request, timeout):
            calls.append(request.full_url)
            raise urllib.error.HTTPError(request.full_url, 502, "Bad Gateway", {}, io.BytesIO(b""))

        with self.assertRaises(urllib.error.HTTPError):
            fetch_all(urlopen=opener, sleep_fn=delays.append, max_attempts=3)
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [0.5, 1.0])

    def test_malformed_success_response_fails_without_retry(self):
        calls, delays = [], []

        def opener(request, timeout):
            calls.append(request.full_url)
            return io.BytesIO(b'{"not_rows": []}')

        with self.assertRaisesRegex(ValueError, "rows array"):
            fetch_all(urlopen=opener, sleep_fn=delays.append)
        self.assertEqual(len(calls), 1)
        self.assertEqual(delays, [])

    def test_status_artifact_is_valid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "status.json"
            expected = {"status": "upstream_unavailable", "error_type": "HTTPError"}
            _write_status(path, expected)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), expected)


if __name__ == "__main__":
    unittest.main()
