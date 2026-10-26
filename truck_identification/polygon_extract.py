
import geopandas as gpd
import json
import os

# Path to your downloaded Sentinel-2 tile GeoJSON
file_path = "./geojson/30TXP.geojson"

# Check that the input file exists
if not os.path.isfile(file_path):
    raise FileNotFoundError(
        "GeoJSON file not found: {}".format(file_path)
    )

# Read the GeoJSON file
gdf = gpd.read_file(file_path)

# Inspect available columns and tile names
print("Columns:", gdf.columns.tolist())

if "Name" not in gdf.columns:
    raise KeyError(
        "The GeoJSON file does not contain a 'Name' column."
    )

print("\nAvailable tile names:")
print(gdf["Name"].tolist())

# Candidate tile IDs
tile_ids = ["30TXQ", "30TXP"]

# Filter using the actual column name
candidates = gdf[
    gdf["Name"].astype(str).str.strip().isin(tile_ids)
].copy()

if candidates.empty:
    print(
        "\nNo candidate tiles found in this file."
        "\nCheck whether the file contains these tile IDs."
    )
else:
    for _, row in candidates.iterrows():
        tile_id = row["Name"]
        geometry = row.geometry

        print("\n" + "=" * 50)
        print("Tile ID:", tile_id)
        print("Geometry type:", geometry.geom_type)
        print("CRS:", gdf.crs)
        print("Polygon coordinates (longitude, latitude "
              "if CRS is EPSG:4326):")

        print(json.dumps(
            geometry.__geo_interface__["coordinates"],
            indent=2
        ))

    # Save selected tile footprints
    output_file = "bordeaux_sentinel2_tiles.geojson"

    candidates.to_file(
        output_file,
        driver="GeoJSON"
    )

    print("\nSaved selected tile footprints to:", output_file)
