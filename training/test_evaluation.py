import unittest

from training.class_schema import CLASS_NAMES
from training.evaluation import validate_per_class_summary


def rows():
    return [
        {
            "Class": name,
            "Images": 12 + index,
            "Instances": 20 + index,
            "Box-P": 0.90,
            "Box-R": 0.85,
            "Box-F1": 0.87,
            "mAP50": 0.88,
            "mAP75": 0.80,
            "mAP50-95": 0.70,
        }
        for index, name in enumerate(CLASS_NAMES)
    ]


class PerClassEvaluationTests(unittest.TestCase):
    def test_complete_seven_class_summary_is_ordered_by_shared_schema(self):
        report = validate_per_class_summary(list(reversed(rows())))
        self.assertEqual(list(report), list(CLASS_NAMES))
        self.assertEqual(report["other_insect"]["instances"], 26)
        self.assertEqual(report["vespa_velutina"]["precision"], 0.9)

    def test_missing_class_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing required classes"):
            validate_per_class_summary(rows()[:-1])

    def test_unknown_or_duplicate_class_fails_closed(self):
        unknown = rows()
        unknown[-1]["Class"] = "unreviewed_species"
        with self.assertRaisesRegex(ValueError, "unknown or invalid class"):
            validate_per_class_summary(unknown)
        duplicate = rows()
        duplicate[-1]["Class"] = duplicate[0]["Class"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_per_class_summary(duplicate)

    def test_nonfinite_and_out_of_range_metrics_fail_closed(self):
        for patch in ({"Box-P": float("nan")}, {"Box-R": float("inf")},
                      {"mAP50": -0.1}, {"mAP75": 1.1}, {"Box-F1": True}):
            candidate = rows()
            candidate[0].update(patch)
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                validate_per_class_summary(candidate)

    def test_zero_counts_and_boolean_counts_fail_closed(self):
        for patch in ({"Images": 0}, {"Instances": -1}, {"Images": True}, {"Instances": 1.5}):
            candidate = rows()
            candidate[0].update(patch)
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                validate_per_class_summary(candidate)

    def test_non_list_summary_fails_closed(self):
        with self.assertRaises(ValueError):
            validate_per_class_summary(None)


if __name__ == "__main__":
    unittest.main()
