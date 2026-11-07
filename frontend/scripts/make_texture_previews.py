#!/usr/bin/env python3
"""Write small JPEG/PNG stand-ins for the orrery maps.

Full-resolution files stay in static/textures. The scene paints these previews
first and fetches a full map only for a body that is focused or large on screen.
Normal and roughness maps have no preview; they load with that body's detail pass.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "static" / "textures"
OUT = ROOT / "preview"
SKIP = ("normal", "roughness")
STARFIELD = {"stars.jpg": (1280, 640)}
PLANET = (640, 320)


def main() -> None:
    Image.MAX_IMAGE_PIXELS = None
    OUT.mkdir(parents=True, exist_ok=True)
    for source in sorted(ROOT.iterdir()):
        if not source.is_file() or source.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        if any(token in source.name for token in SKIP):
            continue
        image = Image.open(source)
        if source.name in STARFIELD:
            image.thumbnail(STARFIELD[source.name], Image.Resampling.LANCZOS)
        elif source.suffix.lower() == ".png":
            image.thumbnail((1024, 128), Image.Resampling.LANCZOS)
        else:
            image.thumbnail(PLANET, Image.Resampling.LANCZOS)
        dest = OUT / source.name
        if source.suffix.lower() == ".png":
            image.save(dest, "PNG", optimize=True)
        else:
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(dest, "JPEG", quality=68, optimize=True, progressive=True)
        print(f"{dest.name:24} {dest.stat().st_size / 1024:7.1f} KB  {image.size}")


if __name__ == "__main__":
    main()
