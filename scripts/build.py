#!/usr/bin/env python3
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
for script in ["make_ascii_svg.py", "make_info_card.py", "render_heatmap_svg.py"]:
    runpy.run_path(str(HERE / script), run_name="__main__")
