"""Synthetic decoder contract tests: no real images and no accuracy claims."""
import unittest
import numpy as np
from scripts.hornet3000_decode import decode_raw


class Hornet3000DecoderTests(unittest.TestCase):
    def setUp(self):
        self.raw = np.zeros((1, 9, 8400), dtype=np.float32)

    def put(self, index, class_id, score, x=100, y=100, w=50, h=50):
        self.raw[0, :4, index] = [x, y, w, h]
        self.raw[0, 4 + class_id, index] = score

    def test_class_three_is_velutina_unverified(self):
        self.put(0, 3, .95)
        result = decode_raw(self.raw)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["class_code"], "vvel")
        self.assertEqual(result[0]["class_id"], 3)
        self.assertEqual(result[0]["verification_status"], "unverified")

    def test_same_class_overlapping_suppressed(self):
        self.put(0, 3, .95)
        self.put(1, 3, .9, x=101)
        self.assertEqual(len(decode_raw(self.raw)), 1)

    def test_different_classes_not_suppressed(self):
        self.put(0, 3, .95)
        self.put(1, 1, .9)
        self.assertEqual(len(decode_raw(self.raw)), 2)

    def test_low_confidence_filtered(self):
        self.put(0, 3, .49)
        self.assertEqual(decode_raw(self.raw), [])

    def test_non_finite_fails_closed(self):
        self.raw[0, 4, 0] = np.nan
        with self.assertRaises(ValueError):
            decode_raw(self.raw)

    def test_wrong_shape_fails_closed(self):
        with self.assertRaises(ValueError):
            decode_raw(np.zeros((1, 9, 10), dtype=np.float32))

    def test_invalid_score_fails_closed(self):
        self.raw[0, 4, 0] = 1.5
        with self.assertRaises(ValueError):
            decode_raw(self.raw)

    def test_clipped_outside_image(self):
        self.put(0, 3, .95, x=2, y=2, w=20, h=20)
        result = decode_raw(self.raw)
        self.assertEqual(result[0]["box_xyxy_input_pixels"][:2], [0., 0.])


if __name__ == "__main__":
    unittest.main()
