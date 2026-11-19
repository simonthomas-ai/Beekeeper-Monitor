#!/usr/bin/env python3
"""Offline safety tests for authorized image importer. No fabricated training data."""
import importlib.util
import ipaddress
import pathlib
import unittest
from unittest.mock import patch

MODULE = pathlib.Path(__file__).with_name("import_authorized_images.py")
spec = importlib.util.spec_from_file_location("authorized_import", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ImportSafetyTests(unittest.TestCase):
    def test_approved_license_allowlist(self):
        self.assertEqual(mod.ALLOWED, {"CC0-1.0", "CC-BY-4.0"})
        self.assertNotIn("CC-BY-VERSION-UNVERIFIED", mod.ALLOWED)

    def test_canonical_license_references(self):
        self.assertEqual(mod.LICENSE_URLS['CC0-1.0'], 'https://creativecommons.org/publicdomain/zero/1.0/')
        self.assertEqual(mod.LICENSE_URLS['CC-BY-4.0'], 'https://creativecommons.org/licenses/by/4.0/')

    def test_provenance_fields_retained(self):
        for field in ("source_id", "source_url", "image_url", "creator",
                      "license", "license_url", "attribution", "sha256"):
            self.assertIn(field, mod.OUTPUT)

    def test_reject_non_https(self):
        for url in ("http://example.org/a.jpg", "file:///etc/passwd",
                    "https://user:pass@example.org/a.jpg", "https://localhost/a.jpg"):
            with self.assertRaises(ValueError):
                mod.public_https(url)

    def test_reject_private_resolved_addresses(self):
        from types import SimpleNamespace
        for address in ("127.0.0.1", "10.1.2.3", "192.168.1.2", "::1", "169.254.169.254"):
            with self.subTest(address=address):
                with patch.object(mod.socket, "getaddrinfo", return_value=[
                    (None, None, None, None, (address, 443))
                ]):
                    with self.assertRaises(ValueError):
                        mod.public_https("https://example.org/a.jpg")

    def test_accept_public_resolved_address(self):
        with patch.object(mod.socket, "getaddrinfo", return_value=[
            (None, None, None, None, ("8.8.8.8", 443))
        ]):
            self.assertEqual(mod.public_https("https://example.org/a.jpg"),
                             "https://example.org/a.jpg")

    def test_redirects_rejected(self):
        with self.assertRaises(ValueError):
            mod.NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://example.org/a.jpg")

if __name__ == "__main__":
    unittest.main()
