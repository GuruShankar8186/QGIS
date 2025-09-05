from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from app.models import PolygonsPayload
from app.geometry import make_shapely_polygon, validate_and_fix, reproject_geom
from app.renderer import create_image_from_geoms
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon, mapping
import tempfile, os

router = APIRouter()

@router.post("/validate")
async def validate(payload: PolygonsPayload):
    try:
        shapes = [validate_and_fix(make_shapely_polygon(p)) for p in payload.polygons]
        merged = unary_union(shapes)
        if isinstance(merged, Polygon):
            geoms = [merged]
        elif isinstance(merged, MultiPolygon):
            geoms = list(merged.geoms)
        else:
            raise ValueError("No valid geometry")

        geojson = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "properties": {"id": i}, "geometry": mapping(g)}
                for i, g in enumerate(geoms)
            ],
        }
        return JSONResponse(content=geojson)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/georeference")
async def georeference(payload: PolygonsPayload):
    try:
        shapes = [validate_and_fix(make_shapely_polygon(p)) for p in payload.polygons]
        merged = unary_union(shapes)
        if isinstance(merged, Polygon):
            geoms = [merged]
        elif isinstance(merged, MultiPolygon):
            geoms = list(merged.geoms)
        else:
            raise ValueError("No valid geometry")

        geoms_proj = [reproject_geom(g) for g in geoms]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.close()
        create_image_from_geoms(geoms_proj, tmp.name)

        geojson = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "properties": {"id": i}, "geometry": mapping(g)}
                for i, g in enumerate(geoms)
            ],
        }

        return {"image_file": os.path.basename(tmp.name), "geojson": geojson}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/image/{filename}")
async def get_image(filename: str):
    path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path, media_type="image/png")
