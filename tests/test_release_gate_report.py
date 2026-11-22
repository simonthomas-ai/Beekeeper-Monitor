"""Sicherheitsregeln für den automatischen Freigabebericht."""
import unittest
from scripts.release_gate_report import render


class ReleaseGateReportTests(unittest.TestCase):
    def setUp(self):
        self.checklist = "# Checkliste\n\n- [x] Historischer CI-Test\n- [ ] Rechtliche Freigabe\n- [ ] Feldtest\n"

    def test_green_ci_never_unblocks_release(self):
        result = render(self.checklist, {
            "Qualitätsprüfung": "success",
            "Validierung": "success",
            "Browser-Integration": "success",
        })
        self.assertIn("Freigabestatus: GESPERRT", result)
        self.assertIn("Offene Freigabepunkte: **2**", result)
        self.assertIn("historische Nachweise: **1**", result)
        self.assertIn("keine Feldvalidierung", result)

    def test_unknown_and_invalid_ci_results_are_not_success(self):
        result = render(self.checklist, {"Qualitätsprüfung": "nonsense", "Validierung": "unknown"})
        self.assertNotIn("nonsense", result)
        self.assertIn("| Qualitätsprüfung | unknown |", result)
        self.assertIn("Freigabestatus: GESPERRT", result)

    def test_ai_data_failures_remain_visible(self):
        result = render(self.checklist, {
            "Echte Trainingsdaten": "failure",
            "Fachlich geprüfte Annotationen": "failure",
        })
        self.assertIn("| Echte Trainingsdaten | failure |", result)
        self.assertIn("| Fachlich geprüfte Annotationen | failure |", result)
        self.assertIn("Freigabestatus: GESPERRT", result)

    def test_taxonomy_failure_is_visible_without_release(self):
        result = render(self.checklist, {"Europäische Taxonomie (Online-API)": "failure"})
        self.assertIn("| Europäische Taxonomie (Online-API) | failure |", result)
        self.assertIn("Freigabestatus: GESPERRT", result)

    def test_empty_checklist_fails_closed(self):
        with self.assertRaises(ValueError):
            render("# leer\n", {"Qualitätsprüfung": "success"})


if __name__ == "__main__":
    unittest.main()
