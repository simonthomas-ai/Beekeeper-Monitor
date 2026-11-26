import unittest

from scripts.check_model_catalog import validate


def candidate(model_id, task, fmt):
    return {
        "id": model_id,
        "task": task,
        "upstream": "example/model",
        "commit": "b" * 40,
        "path": "weights/model." + fmt,
        "bytes": 1024,
        "git_blob": "a" * 40,
        "format": fmt,
        "review_status": "rights_and_runtime_pending",
    }


def valid_catalog():
    return {
        "schema_version": 1,
        "status": "candidates_only_no_execution",
        "models": [
            candidate("hornet-model", "hornet_detection", "onnx"),
            candidate("sticky-board", "varroa_sticky_board", "pt"),
            candidate("varroa-on-bee", "varroa_on_bee", "pt"),
        ],
    }


class ModelCatalogTests(unittest.TestCase):
    def test_accepts_all_tasks_only_with_pinned_blocked_candidates(self):
        rows = validate(valid_catalog())
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(len(row[5]) == 40 for row in rows))

    def test_rejects_missing_or_malformed_commit_pin(self):
        for commit in (None, "", "main", "a" * 39, "G" * 40):
            data = valid_catalog()
            if commit is None:
                del data["models"][0]["commit"]
            else:
                data["models"][0]["commit"] = commit
            with self.subTest(commit=commit), self.assertRaisesRegex(ValueError, "immutable"):
                validate(data)

    def test_rejects_candidate_without_pending_rights_and_runtime_status(self):
        data = valid_catalog()
        data["models"][0]["review_status"] = "approved"
        with self.assertRaisesRegex(ValueError, "rights/runtime pending"):
            validate(data)

    def test_rejects_execution_or_unverified_approval_fields(self):
        for field, value in (
            ("enabled", False),
            ("active", False),
            ("inference_enabled", False),
            ("deployable", False),
            ("sha256", "0" * 64),
            ("license_approved", True),
        ):
            data = valid_catalog()
            data["models"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "must not contain"):
                validate(data)

    def test_rejects_windows_path_separators_and_traversal(self):
        for path in ("../model.onnx", "weights\\model.onnx", "/tmp/model.onnx", "weights//model.onnx"):
            data = valid_catalog()
            data["models"][0]["path"] = path
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "Unsafe model path"):
                validate(data)

    def test_rejects_invalid_top_level_and_boolean_schema_version(self):
        for data in ([], {"schema_version": True, "status": "candidates_only_no_execution", "models": []}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate(data)

    def test_rejects_non_object_rows_and_unknown_tasks(self):
        data = valid_catalog()
        data["models"][0] = []
        with self.assertRaisesRegex(ValueError, "must be an object"):
            validate(data)
        data = valid_catalog()
        data["models"][0]["task"] = "other"
        with self.assertRaisesRegex(ValueError, "Unknown model task"):
            validate(data)

    def test_rejects_duplicate_ids(self):
        data = valid_catalog()
        data["models"][1]["id"] = data["models"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate model ID"):
            validate(data)


if __name__ == "__main__":
    unittest.main()
