"""Zenodo inventory may read metadata, but must not fetch dataset bytes."""
import contextlib
import io
import sys
import unittest
from unittest.mock import patch

from scripts import zenodo_inventory


class ZenodoDownloadPolicyTests(unittest.TestCase):
    def test_explicit_dataset_download_is_blocked_before_metadata_or_file_network(self):
        argv = ["zenodo_inventory.py", "varroa-v2", "--download", "images.zip"]
        with patch.object(sys, "argv", argv), patch.object(zenodo_inventory, "get_json") as get_json:
            with self.assertRaises(SystemExit) as raised:
                zenodo_inventory.main()
        self.assertEqual(raised.exception.code, 2)
        get_json.assert_not_called()
        self.assertIs(zenodo_inventory.DOWNLOADS_ENABLED, False)

    def test_metadata_inventory_does_not_download_files(self):
        record = {"files": [{"key": "README.md", "size": 12, "checksum": "md5:00000000000000000000000000000000"}]}
        output = io.StringIO()
        argv = ["zenodo_inventory.py", "varroa-v2"]
        with patch.object(sys, "argv", argv), patch.object(zenodo_inventory, "get_json", return_value=record) as get_json, patch.object(zenodo_inventory.urllib.request, "urlopen") as urlopen, contextlib.redirect_stdout(output):
            zenodo_inventory.main()
        get_json.assert_called_once()
        urlopen.assert_not_called()
        self.assertIn("README.md", output.getvalue())


if __name__ == "__main__":
    unittest.main()
