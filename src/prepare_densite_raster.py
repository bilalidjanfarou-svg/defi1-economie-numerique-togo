"""
Convertit la grille de population WorldPop (100m) en image de densite
superposable sur la carte Folium (ImageOverlay), et calcule la population
reelle par prefecture (croisement avec les polygones GeoJSON) pour comparer
avec le recensement 2022 utilise jusqu'ici.
"""
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"

RASTER_PATH = DATA_RAW / "togo_population_100m.tif"
GEOJSON_PATH = DATA_RAW / "togo_prefectures.geojson"


def main():
    with rasterio.open(RASTER_PATH) as src:
        data = src.read(1)
        data = np.where(data < 0, 0, data)  # nodata -> 0
        bounds = src.bounds
        transform = src.transform

        # --- Image de densite (PNG semi-transparent) pour overlay carte ---
        # Echelle logarithmique car la population est tres concentree (Lomé)
        data_log = np.log1p(data)
        norm = mcolors.Normalize(vmin=0, vmax=np.percentile(data_log[data_log > 0], 99))
        cmap = plt.cm.inferno
        rgba = cmap(norm(data_log))
        rgba[..., 3] = np.where(data > 0, 0.65, 0)  # transparent hors zones habitees

        output_png = DATA_PROCESSED / "densite_population.png"
        plt.imsave(output_png, rgba)
        print(f"Image de densite sauvegardee : {output_png}")
        print(f"Bounds (pour ImageOverlay) : {bounds}")

        # --- Population reelle par prefecture (zonal stats) ---
        with open(GEOJSON_PATH, encoding="utf-8") as f:
            geo = json.load(f)

        resultats = []
        for feat in geo["features"]:
            nom = feat["properties"]["shapeName"]
            mask = geometry_mask(
                [feat["geometry"]],
                out_shape=data.shape,
                transform=transform,
                invert=True,
            )
            pop_totale = float(data[mask].sum())
            resultats.append({"prefecture_geojson": nom, "population_worldpop_2020": round(pop_totale)})

        import pandas as pd
        df = pd.DataFrame(resultats)
        df.to_csv(DATA_PROCESSED / "population_worldpop_par_prefecture.csv", index=False)
        print(f"\nPopulation WorldPop par prefecture sauvegardee.")
        print(df.sort_values("population_worldpop_2020", ascending=False).head(10))

        # Sauvegarde des bounds pour utilisation dans le dashboard
        with open(DATA_PROCESSED / "densite_bounds.json", "w") as f:
            json.dump({
                "south": bounds.bottom, "north": bounds.top,
                "west": bounds.left, "east": bounds.right,
            }, f)


if __name__ == "__main__":
    main()