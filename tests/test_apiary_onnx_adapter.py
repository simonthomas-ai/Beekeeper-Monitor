import unittest
from scripts.apiary_onnx_adapter import run_local_onnx
from scripts.apiary_module_registry import ModuleNotReady

class AdapterSafetyTests(unittest.TestCase):
    def test_disabled_model_never_reads_image_or_needs_dependencies(self):
        with self.assertRaises(ModuleNotReady):
            run_local_onnx({"schema":"vespaguard.apiary-module.v1",
                "id":"varroa_board","enabled":False,
                "release_status":"research_only","human_confirmation_required":True},
                "nonexistent.onnx","nonexistent.jpg",input_width=640,input_height=640)

if __name__ == "__main__":
    unittest.main()
