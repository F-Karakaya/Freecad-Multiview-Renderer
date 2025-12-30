"""
FreeCAD STEP Multi-View Renderer
================================

This script automates the rendering of a STEP (.step / .stp) CAD model
from multiple predefined and random camera viewpoints using FreeCAD's
Python API.

It is suitable for:
- Dataset generation (computer vision, CAD ML pipelines)
- Documentation visuals
- Design inspection snapshots

Author: Furkan Karakaya
Repository-ready, production-quality implementation.
"""

import os
import time
import math
import random

import FreeCAD
import FreeCADGui
import Part
from pivy import coin


# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

STEP_FILE_PATH = "D:/general_codes/Freecad-Multiview-Renderer/data/inputs/Violin.step"
OUTPUT_DIR = "D:/general_codes/Freecad-Multiview-Renderer/data/outputs/3d_views_Violin_step"

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 768
BACKGROUND_COLOR = "White"

CAMERA_DISTANCE_SCALE = 1.8
GUI_UPDATE_DELAY_SEC = 0.5
NUM_RANDOM_VIEWS = 10


# ---------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------

def ensure_directory(path: str) -> None:
    """Create output directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def random_unit_vector() -> coin.SbVec3f:
    """
    Generate a random normalized 3D direction vector.

    Returns
    -------
    coin.SbVec3f
        Unit-length vector with random direction.
    """
    x, y, z = (
        random.uniform(-1.0, 1.0),
        random.uniform(-1.0, 1.0),
        random.uniform(-1.0, 1.0),
    )
    length = math.sqrt(x * x + y * y + z * z) or 1.0
    return coin.SbVec3f(x / length, y / length, z / length)


def save_view_image(
    view,
    file_path: str,
    width: int = IMAGE_WIDTH,
    height: int = IMAGE_HEIGHT,
    background: str = BACKGROUND_COLOR,
) -> None:
    """Save the current FreeCAD view to an image file."""
    view.saveImage(file_path, width, height, background)
    print(f"[INFO] Image saved: {file_path}")


# ---------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------

def main() -> None:
    """Main execution routine."""

    # --------------------------------------------------------------
    # 1. Document Creation & STEP Import
    # --------------------------------------------------------------
    print("[INFO] Creating new FreeCAD document...")
    document = FreeCAD.newDocument("STEP_Render_Document")

    print(f"[INFO] Importing STEP file: {STEP_FILE_PATH}")
    Part.insert(STEP_FILE_PATH, document.Name)

    # --------------------------------------------------------------
    # 2. View & Camera Initialization
    # --------------------------------------------------------------
    view = FreeCADGui.ActiveDocument.ActiveView
    view.fitAll()

    camera = view.getCameraNode()

    # Increase camera distance to ensure full model visibility
    current_position = camera.position.getValue()
    scaled_position = coin.SbVec3f(
        current_position[0] * CAMERA_DISTANCE_SCALE,
        current_position[1] * CAMERA_DISTANCE_SCALE,
        current_position[2] * CAMERA_DISTANCE_SCALE,
    )
    camera.position.setValue(scaled_position)

    ensure_directory(OUTPUT_DIR)

    # --------------------------------------------------------------
    # 3. Preset Orthographic Views
    # --------------------------------------------------------------
    preset_views = [
        ("isometric", None),
        ("top", coin.SbVec3f(0, 0, 1)),
        ("bottom", coin.SbVec3f(0, 0, -1)),
        ("front", coin.SbVec3f(0, -1, 0)),
        ("rear", coin.SbVec3f(0, 1, 0)),
        ("right", coin.SbVec3f(1, 0, 0)),
        ("left", coin.SbVec3f(-1, 0, 0)),
    ]

    print("[INFO] Rendering preset views...")
    for label, target_direction in preset_views:

        if target_direction is not None:
            # Default camera forward direction in FreeCAD is -Z
            rotation = coin.SbRotation()
            rotation.setValue(coin.SbVec3f(0, 0, -1), target_direction)
            camera.orientation.setValue(rotation)
        else:
            view.viewAxonometric()

        view.fitAll()
        FreeCADGui.updateGui()
        time.sleep(GUI_UPDATE_DELAY_SEC)

        output_path = os.path.join(OUTPUT_DIR, f"{label}.png")
        save_view_image(view, output_path)

    # --------------------------------------------------------------
    # 4. Randomized Camera Views
    # --------------------------------------------------------------
    print("[INFO] Rendering random camera views...")
    for index in range(NUM_RANDOM_VIEWS):

        rotation_axis = random_unit_vector()
        rotation_angle_rad = random.uniform(0.0, 2.0 * math.pi)
        rotation_angle_deg = int(math.degrees(rotation_angle_rad))

        rotation = coin.SbRotation(rotation_axis, rotation_angle_rad)
        camera.orientation.setValue(rotation)

        view.fitAll()
        FreeCADGui.updateGui()
        time.sleep(GUI_UPDATE_DELAY_SEC)

        ax, ay, az = rotation_axis
        output_filename = (
            f"random_view_{index + 1}_"
            f"axis_{ax:.2f}_{ay:.2f}_{az:.2f}_"
            f"angle_{rotation_angle_deg}.png"
        )

        output_path = os.path.join(OUTPUT_DIR, output_filename)
        save_view_image(view, output_path)

    print("[SUCCESS] All images have been successfully rendered.")


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()
