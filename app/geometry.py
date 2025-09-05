from shapely.geometry import Polygon, MultiPolygon, mapping, shape
from shapely.validation import explain_validity
from shapely.ops import unary_union
from pyproj import Transformer

WGS84_TO_WEBMERCATOR = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)

def ensure_closed(ring):
    if ring[0] != ring[-1]:
        return ring + [ring[0]]
    return ring

def make_shapely_polygon(poly_in):
    outer = ensure_closed(poly_in.coordinates)
    holes = [ensure_closed(h) for h in poly_in.holes] if poly_in.holes else None
    return Polygon(outer, holes)

def validate_and_fix(poly: Polygon):
    if poly.is_valid:
        return poly
    fixed = poly.buffer(0)
    if fixed.is_empty:
        raise ValueError(f"Invalid polygon: {explain_validity(poly)}")
    return fixed

def reproject_geom(geom, transformer=WGS84_TO_WEBMERCATOR):
    if geom.geom_type == "Polygon":
        exterior = [transformer.transform(x, y) for x, y in geom.exterior.coords]
        interiors = [
            [transformer.transform(x, y) for x, y in ring.coords]
            for ring in geom.interiors
        ]
        return Polygon(exterior, interiors)
    elif geom.geom_type == "MultiPolygon":
        return MultiPolygon([reproject_geom(g) for g in geom.geoms])
    return geom
