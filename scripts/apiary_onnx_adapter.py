"""Local ONNX inference adapter. Research-only raw outputs; never a diagnosis.

Requires: pip install onnxruntime pillow numpy
Model must be separately licensed, approved and matched to its preprocessing.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
from scripts.apiary_module_registry import validate_manifest, ModuleNotReady

def run_local_onnx(
    manifest: dict,
    weights_path: str | Path,
    image_path: str | Path,
    *,
    input_width: int,
    input_height: int,
) -> dict[str, Any]:
    """Return raw output tensor shapes, not unvalidated detection labels."""
    guard = validate_manifest(manifest, weights_path=weights_path)
    if not (isinstance(input_width, int) and isinstance(input_height, int)
            and 32 <= input_width <= 2048 and 32 <= input_height <= 2048):
        raise ValueError("Invalid model input dimensions")
    try:
        import numpy as np
        import onnxruntime as ort
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise RuntimeError("Install optional dependencies: onnxruntime numpy pillow") from exc
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as source:
        source.verify()
    with Image.open(path) as source:
        rgb = ImageOps.exif_transpose(source).convert("RGB")
        if rgb.width * rgb.height > 40_000_000:
            raise ValueError("Image too large")
        rgb = rgb.resize((input_width, input_height))
        array = np.asarray(rgb, dtype=np.float32).transpose(2, 0, 1)[None] / 255.0
    session = ort.InferenceSession(str(weights_path), providers=["CPUExecutionProvider"])
    inputs = session.get_inputs()
    if len(inputs) != 1 or inputs[0].type != "tensor(float)":
        raise ModuleNotReady("Expected one float32 image tensor input")
    shape = inputs[0].shape
    if len(shape) != 4 or any(isinstance(x, int) and x != y for x, y in zip(shape, array.shape)):
        raise ModuleNotReady("Model input shape does not match image preprocessing")
    outputs = session.run(None, {inputs[0].name: array})
    return {
        "module": guard["id"],
        "status": "raw_inference_only_not_a_species_or_health_result",
        "output_shapes": [list(np.asarray(output).shape) for output in outputs],
        "confirmed_detections": [],
    }
