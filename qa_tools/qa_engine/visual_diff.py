from __future__ import annotations

from pathlib import Path
from typing import Optional


def compare_images(img_a: str | Path, img_b: str | Path, out_path: Optional[str | Path] = None) -> bool:
    try:
        from PIL import Image, ImageChops
    except Exception:
        print("Pillow not installed; visual diff unavailable. Install with 'pip install pillow'")
        return False

    a = Image.open(img_a).convert('RGBA')
    b = Image.open(img_b).convert('RGBA')

    if a.size != b.size:
        print(f"Image sizes differ: {a.size} vs {b.size}")
        return False

    diff = ImageChops.difference(a, b)
    bbox = diff.getbbox()
    if bbox is None:
        # Images are identical
        if out_path:
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            diff.save(out_path)
        return True

    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        # Enhance visibility by multiplying the diff
        enhanced = diff
        enhanced.save(out_path)
    return False
