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
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    views = [("Front", (0, 0)), ("Side", (0, 90)), ("Top", (90, 0)), ("Rear", (0, 180))]
    fig = plt.figure(figsize=(12, 12))
    for i, (name, (elev, azim)) in enumerate(views, 1):
        ax = fig.add_subplot(2, 2, i, projection="3d")
        ax.add_collection3d(Poly3DCollection(tris, facecolor="#b9a479", edgecolor="none", alpha=1))
        ax.set(xlim=(-.6,.6), ylim=(-.6,.6), zlim=(-.6,.6), title=f"{name} (orientation unverified)")
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
    fig.suptitle("Grab3D bee — geometry preview ONLY; taxonomy / rights NOT approved")
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
