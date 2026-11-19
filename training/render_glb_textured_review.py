"""Blender background script: textured review-only renders, never training data.

Usage: blender -b -t 2 --python training/render_glb_textured_review.py -- /tmp/bee.glb training/bee-textured
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    source, dest = Path(args[0]), Path(args[1])
    dest.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("GLB has no mesh objects")
    points = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
    lo = Vector([min(p[i] for p in points) for i in range(3)])
    hi = Vector([max(p[i] for p in points) for i in range(3)])
    center = (lo + hi) / 2
    scale = max(hi[i] - lo[i] for i in range(3))
    if scale <= 0:
        raise RuntimeError("Degenerate model")
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "REVIEW_CAMERA"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale * 1.55
    bpy.context.scene.camera = camera
    bpy.ops.object.light_add(type="AREA")
    light = bpy.context.object
    light.data.energy = 450
    light.data.shape = "DISK"
    light.data.size = scale * 4
    light.location = center + Vector((scale * 2, -scale * 3, scale * 4))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.8, 0.8, 0.8)
    views = {"x_positive": (1, 0, 0), "x_negative": (-1, 0, 0),
             "y_positive": (0, 1, 0), "y_negative": (0, -1, 0),
             "z_positive": (0, 0, 1), "z_negative": (0, 0, -1)}
    for label, direction in views.items():
        camera.location = center + Vector(direction) * scale * 3
        camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str((dest / (label + ".png")).resolve())
        bpy.ops.render.render(write_still=True)
    report = {"review_only": True, "species_verified": "NO", "geometry_verified": "NO",
              "license_verified": "NO", "training_approved": "NO", "mesh_objects": len(meshes),
              "views": list(views), "image_resolution": [1400, 1400],
              "model_file": source.name, "textures_rendered_by_blender": True}
    (dest / "review.json").write_text(json.dumps(report, indent=2) + "\n")

if __name__ == "__main__":
    main()
