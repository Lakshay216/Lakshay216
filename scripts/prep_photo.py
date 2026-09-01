#!/usr/bin/env python3
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent

if len(sys.argv) < 2:
    raise SystemExit("Usage: python scripts/prep_photo.py path/to/photo.jpg")

source = Path(sys.argv[1])
output = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "source-prepped.png"
cutout = remove(Image.open(source).convert("RGBA"))
rgb = np.asarray(cutout.convert("RGB"))
alpha = np.asarray(cutout.getchannel("A"))
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
gray = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8)).apply(gray)
gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=18)
mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255, (0, 0), 1)
result = gray * mask + 255 * (1 - mask)
Image.fromarray(np.clip(result, 0, 255).astype(np.uint8), mode="L").save(output)
print(f"Wrote {output}")
