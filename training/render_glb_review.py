#!/usr/bin/env python3
"""Render review-only orthographic mesh previews; never label species or approve training."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

def render(glb: Path, output: Path):
    scene = trimesh.load(str(glb), force="scene", process=False)
    meshes = scene.to_geometry()
    if not isinstance(meshes, trimesh.Trimesh) or len(meshes.faces) == 0:
        raise ValueError("No mesh faces available")
    if not np.isfinite(meshes.vertices).all():
        raise ValueError("Non-finite vertex positions")
    bounds = meshes.bounds
    span = bounds[1] - bounds[0]
    if np.max(span) <= 0:
        raise ValueError("Degenerate mesh")
    center = meshes.bounds.mean(axis=0)
    # Deterministic, bounded sampling; preview is not a geometry verification.
    faces = meshes.faces
    indices = np.linspace(0, len(faces) - 1, min(12000, len(faces)), dtype=int)
    tris = (meshes.vertices[faces[indices]] - center) / np.max(span)
    # Project dense triangle centroids and vertices into orthogonal 2D views.\n    # A dark, high-contrast point cloud avoids matplotlib 3D face-order artifacts.\n    points = tris.reshape(-1, 3)\n    views = [("XY projection", (0, 1)), ("XZ projection", (0, 2)),\n             ("YZ projection", (1, 2)), ("XY reverse", (0, 1))]\n    fig, axes = plt.subplots(2, 2, figsize=(12, 12))\n    for ax, (name, (a, b)) in zip(axes.flat, views):\n        projected = points[:, [a, b]]\n        if name == "XY reverse":\n            projected = projected * [-1, 1]\n        ax.scatter(projected[:, 0], projected[:, 1], s=0.45, c="#202020", alpha=0.85, linewidths=0, rasterized=True)\n        ax.set(xlim=(-.55,.55), ylim=(-.55,.55), title=f"{name} (axes, anatomy unverified)")\n        ax.set_aspect("equal", adjustable="box")\n        ax.axis("off")
    fig.suptitle("Grab3D bee — high-contrast geometry preview ONLY; taxonomy / rights NOT approved")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return {"source_file": glb.name, "mesh_faces": int(len(faces)), "sampled_faces": int(len(indices)),
            "bounds": bounds.tolist(), "training_approved": "NO", "species_verified": "NO",
            "geometry_verified": "NO", "preview_only": True}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--glb", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    report = render(args.glb, args.output)
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))

if __name__ == "__main__":
    main()
