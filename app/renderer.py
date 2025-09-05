from shapely.geometry import Polygon, MultiPolygon
from PIL import Image, ImageDraw
import tempfile
import math

def create_image_from_geoms(geoms, out_path: str, padding: int = 20):
    bounds_list = [g.bounds for g in geoms]
    minx = min(b[0] for b in bounds_list)
    miny = min(b[1] for b in bounds_list)
    maxx = max(b[2] for b in bounds_list)
    maxy = max(b[3] for b in bounds_list)

    w = maxx - minx
    h = maxy - miny
    img_w, img_h = 800, int((h / w) * 800)

    def to_px(x, y):
        px = padding + (x - minx) * ((img_w - 2 * padding) / w)
        py = padding + (maxy - y) * ((img_h - 2 * padding) / h)
        return (px, py)

    img = Image.new("RGBA", (img_w, img_h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    for g in geoms:
        if g.geom_type == "Polygon":
            ext = [to_px(x, y) for x, y in g.exterior.coords]
            ints = [[to_px(x, y) for x, y in r.coords] for r in g.interiors]
            draw.polygon(ext, fill=(150, 200, 255, 180), outline=(0, 0, 0))
            for hole in ints:
                draw.polygon(hole, fill=(255, 255, 255, 255), outline=(0, 0, 0))
        elif g.geom_type == "MultiPolygon":
            for p in g.geoms:
                ext = [to_px(x, y) for x, y in p.exterior.coords]
                draw.polygon(ext, fill=(150, 200, 255, 180), outline=(0, 0, 0))

    img.save(out_path, "PNG")
    return out_path
