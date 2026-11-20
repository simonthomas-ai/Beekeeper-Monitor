"""Report actual Varroa ONNX export readiness; never auto-approve unverified rights."""
import argparse
import json
from pathlib import Path


def assess(provenance: dict, *, rights_evidence: str | None = None,
           isolated_environment_evidence: str | None = None) -> dict:
    source_verified = provenance.get("source_blob_verified") is True
    digest = provenance.get("local_sha256")
    sha_valid = isinstance(digest, str) and len(digest) == 64 and all(c in "0123456789abcdef" for c in digest)
    rights_documented = isinstance(rights_evidence, str) and bool(rights_evidence.strip())
    isolation_documented = isinstance(isolated_environment_evidence, str) and bool(isolated_environment_evidence.strip())
    checks = {"source_integrity_verified": source_verified and sha_valid,
              "rights_evidence_supplied": rights_documented,
              "isolation_evidence_supplied": isolation_documented}
    return {"schema": "vespaguard.varroa-export-readiness.v1",
            "checks": checks,
            "ready_for_manual_security_and_legal_review": all(checks.values()),
            "automatic_export_authorized": False,
            "field_approved": False,
            "independent_model_validation_complete": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--rights-evidence", default="")
    parser.add_argument("--isolation-evidence", default="")
    args = parser.parse_args()
    print(json.dumps(assess(json.loads(args.provenance.read_text(encoding="utf-8")),
                            rights_evidence=args.rights_evidence,
                            isolated_environment_evidence=args.isolation_evidence), indent=2))


if __name__ == "__main__":
    main()
