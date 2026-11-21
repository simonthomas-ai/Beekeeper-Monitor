"""Isolated research test on a live CC0 iNaturalist photo; no storage or publication."""
import hashlib
import io
import json
import urllib.request
from urllib.parse import urlencode

from training.inaturalist_media import original_image_url
from training.download_original_inaturalist_images import _download_exact_original
from scripts.hornet3000_decode import decode_raw


def run(model_path):
    import numpy as np
    import onnxruntime as ort
    from PIL import Image, ImageOps

    params = urlencode({"taxon_name": "Vespa velutina", "quality_grade": "research",
                        "photo_license": "cc0", "photos": "true", "per_page": 10})
    req = urllib.request.Request("https://api.inaturalist.org/v1/observations?" + params,
                                 headers={"User-Agent": "VespaGuard-research-CC0-validation/1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        observations = json.load(response).get("results", [])
    checked = None
    for obs in observations:
        if (obs.get("quality_grade") != "research" or
                (obs.get("taxon") or {}).get("name") != "Vespa velutina"):
            continue
        for photo in obs.get("photos", []):
            if str(photo.get("license_code", "")).lower() != "cc0":
                continue
            pid = str(photo.get("id", ""))
            if not pid.isdecimal():
                continue
            # Fresh exact observation recheck prevents stale search metadata.
            audit_req = urllib.request.Request(
                "https://api.inaturalist.org/v1/observations/" + str(obs["id"]),
                headers={"User-Agent": "VespaGuard-research-CC0-validation/1"})
            with urllib.request.urlopen(audit_req, timeout=30) as response:
                fresh = json.load(response).get("results", [])
            if len(fresh) != 1:
                continue
            current = fresh[0]
            if (current.get("quality_grade") != "research" or
                    (current.get("taxon") or {}).get("name") != "Vespa velutina"):
                continue
            current_photo = next((p for p in current.get("photos", [])
                                  if str(p.get("id")) == pid and
                                  str(p.get("license_code", "")).lower() == "cc0"), None)
            if not current_photo:
                continue
            if not (current.get("user") or {}).get("login"):
                continue
            url = original_image_url(current_photo.get("url") or "", pid)
            body, fmt, width, height, digest, _ = _download_exact_original(url, pid)
            checked = (current, current_photo, body, width, height, digest)
            break
        if checked:
            break
    if not checked:
        raise RuntimeError("No currently verified CC0 Vespa velutina photo found; fail closed")
    obs, photo, body, width, height, digest = checked
    with Image.open(io.BytesIO(body)) as image:
        rgb = ImageOps.exif_transpose(image).convert("RGB")
        # Stretch follows the current research-only adapter, not validated preprocessing.
        tensor = np.asarray(rgb.resize((640, 640)), dtype=np.float32).transpose(2, 0, 1)[None] / 255
    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    if (len(session.get_inputs()) != 1 or session.get_inputs()[0].shape != [1, 3, 640, 640] or
            len(session.get_outputs()) != 1 or session.get_outputs()[0].shape != [1, 9, 8400]):
        raise ValueError("Unexpected ONNX model contract")
    detections = decode_raw(session.run(["output0"], {"images": tensor})[0])
    return {"status": "single_real_cc0_photo_research_only", "observation_id": obs["id"],
            "photo_id": photo["id"], "source": "iNaturalist", "photo_license": "cc0",
            "image_sha256": digest, "image_dimensions": [width, height],
            "unverified_candidates": len(detections),
            "unverified_velutina_candidates": sum(d["class_id"] == 3 for d in detections),
            "accuracy_validated": False, "species_independently_confirmed": False,
            "image_published": False, "training_performed": False}
