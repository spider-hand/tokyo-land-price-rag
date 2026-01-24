import json
from shapely.geometry import shape
from collections import defaultdict


GEOJSON_PATH = "data/N03-20250101_13.geojson"


def calculate_ward_centers():
    ward_geometries: dict[str, list[dict]] = defaultdict(list)

    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        ward_name = props.get("N03_004")
        if not ward_name:
            continue

        ward_without_suffix = ward_name[:-1]
        geom = feature.get("geometry")
        if geom:
            ward_geometries[ward_without_suffix].append(geom)

    ward_centers: dict[str, tuple[float, float]] = {}

    # Some wards have multiple geometries (e.g., islands).
    # Assume that the largest geometry is the main area of the ward here.
    for ward, geom_list in ward_geometries.items():
        max_coords = 0
        largest_geom = None

        for geom in geom_list:
            coords = geom.get("coordinates", [])
            coord_count = count_coordinates(coords)
            if coord_count > max_coords:
                max_coords = coord_count
                largest_geom = geom

        if largest_geom:
            shapely_geom = shape(largest_geom)
            centroid = shapely_geom.centroid
            ward_centers[ward] = (round(centroid.x, 4), round(centroid.y, 4))

    return ward_centers


def count_coordinates(coords) -> int:
    if not coords:
        return 0
    if isinstance(coords[0], (int, float)):
        return 1
    return sum(count_coordinates(c) for c in coords)


def main():
    centers = calculate_ward_centers()

    for ward in sorted(centers.keys()):
        lon, lat = centers[ward]
        print(f"  {ward}: [{lon}, {lat}],")


if __name__ == "__main__":
    main()
