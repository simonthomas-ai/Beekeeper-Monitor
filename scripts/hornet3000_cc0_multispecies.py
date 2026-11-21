"""Research-only multi-species CC0 photo screening, no deployment or training."""
import io
import json
import urllib.request
from urllib.parse import urlencode

from scripts.hornet3000_decode import CLASSES, decode_raw
from training.download_original_inaturalist_images import _download_exact_original
from training.inaturalist_media import original_image_url

TAXA = ("Vespa velutina", "Vespa crabro", "Vespula vulgaris", "Apis mellifera")
EXPECTED = {"Vespa velutina": "vvel", "Vespa crabro": "vcra",
            "Vespula vulgaris": "vespsp", "Apis mellifera": "amel"}


def _api(url):
    request = urllib.request.Request(url, headers={"User-Agent": "VespaGuard-CC0-research/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def run(model_path, per_species=3):
    if not isinstance(per_species, int) or not 1 <= per_species <= 10:
        raise ValueError("per_species must be 1..10")
    import numpy as np
    import onnxruntime as ort
    from PIL import Image, ImageOps

    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    if (len(session.get_inputs()) != 1 or session.get_inputs()[0].shape != [1, 3, 640, 640] or
            len(session.get_outputs()) != 1 or session.get_outputs()[0].shape != [1, 9, 8400]):
        raise ValueError("Unexpected ONNX contract")
    results = []
    hashes = set()
    for taxon in TAXA:
        query = urlencode({"taxon_name": taxon, "quality_grade": "research",
                           "photo_license": "cc0", "photos": "true", "per_page": 30})
        observations = _api("https://api.inaturalist.org/v1/observations?" + query).get("results", [])
        count = 0
        for candidate in observations:
            if count >= per_species:
                break
            if (candidate.get("quality_grade") != "research" or
                    (candidate.get("taxon") or {}).get("name") != taxon):
                continue
            obs_id = candidate.get("id")
            if not isinstance(obs_id, int):
                continue
            fresh = _api("https://api.inaturalist.org/v1/observations/" + str(obs_id)).get("results", [])
            if len(fresh) != 1:
                continue
            obs = fresh[0]
            if (obs.get("quality_grade") != "research" or
                    (obs.get("taxon") or {}).get("name") != taxon or
                    not (obs.get("user") or {}).get("login")):
                continue
            for photo in obs.get("photos", []):
                if count >= per_species:
                    break
                pid = str(photo.get("id", ""))
                if not pid.isdecimal() or str(photo.get("license_code", "")).lower() != "cc0":
                    continue
                try:
                    url = original_image_url(photo.get("url") or "", pid)
                    body, _, width, height, digest, _ = _download_exact_original(url, pid)
                except (OSError, ValueError):
                    continue
                if digest in hashes:
                    continue
                hashes.add(digest)
                with Image.open(io.BytesIO(body)) as image:
                    rgb = ImageOps.exif_transpose(image).convert("RGB")
                    tensor = np.asarray(rgb.resize((640, 640)), dtype=np.float32).transpose(2, 0, 1)[None] / 255
                decoded = decode_raw(session.run(["output0"], {"images": tensor})[0])
                codes = [d["class_code"] for d in decoded]
                results.append({"taxon_observation": taxon, "observation_id": obs_id,
                                "photo_id": pid, "sha256": digest, "size": [width, height],
                                "candidate_classes": codes, "expected_model_class": EXPECTED[taxon],
                                "expected_class_present": EXPECTED[taxon] in codes,
                                "velutina_candidate_present": "vvel" in codes,
                                "license": "cc0", "review": "unverified"})
                count += 1
        if count == 0:
            raise RuntimeError("No verified CC0 images for " + taxon + "; fail closed")
    positive = [x for x in results if x["taxon_observation"] == "Vespa velutina"]
    negative = [x for x in results if x["taxon_observation"] != "Vespa velutina"]
    return {"status": "research_screen_not_accuracy_validation", "images_tested": len(results),
            "velutina_candidate_on_velutina_observations": sum(x["velutina_candidate_present"] for x in positive),
            "velutina_observations": len(positive),
            "velutina_candidate_on_other_species": sum(x["velutina_candidate_present"] for x in negative),
            "other_species_observations": len(negative), "samples": results,
            "ground_truth_independently_verified": False, "license_of_model_approved": False,
            "accuracy_validated": False, "images_published": False}
