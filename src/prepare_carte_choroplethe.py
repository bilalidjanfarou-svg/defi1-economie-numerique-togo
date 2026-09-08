"""
Prepare les donnees de couverture pour matcher les polygones du GeoJSON
(qui utilise un decoupage administratif legerement plus ancien : 37 zones
au lieu de 39, avec Agoe-Nyive/Lome Commune fusionnes dans Golfe, et
Kpendjal-Ouest / Oti-Sud fusionnes dans Kpendjal / Oti).
"""
import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_RAW = BASE_DIR / "data" / "raw"

# Correction des noms pour matcher les accents du GeoJSON
RENOMMAGE_VERS_GEOJSON = {
    "Kéran": "Keran",
    "Avé": "Ave",
    "Tandjouaré": "Tandjouare",
    "Tône": "Tone",
    "Mô": "Plaine de Mô",
}

# Fusion des prefectures recentes vers leur prefecture-mere dans le GeoJSON
FUSION_VERS_PREFECTURE_MERE = {
    "Agoè-Nyivé": "Golfe",
    "Kpendjal-Ouest": "Kpendjal",
    "Oti-Sud": "Oti",
}


def main():
    couverture = pd.read_csv(DATA_PROCESSED / "couverture_par_prefecture.csv")

    # Etape 1 : fusionner les prefectures recentes vers leur prefecture-mere
    couverture["prefecture_geojson"] = couverture["prefecture"].replace(FUSION_VERS_PREFECTURE_MERE)
    couverture["prefecture_geojson"] = couverture["prefecture_geojson"].replace(RENOMMAGE_VERS_GEOJSON)

    agg = couverture.groupby("prefecture_geojson").agg(
        population_2022=("population_2022", "sum"),
        nb_agences=("nb_agences", "sum"),
        nb_points_mobile_money=("nb_points_mobile_money", "sum"),
        region=("region", "first"),
    ).reset_index()

    agg["agences_pour_100k_hab"] = (agg["nb_agences"] / agg["population_2022"] * 100_000).round(2)

    # Verification : les noms doivent tous matcher le GeoJSON
    with open(DATA_RAW / "togo_prefectures.geojson", encoding="utf-8") as f:
        geo = json.load(f)
    noms_geojson = {feat["properties"]["shapeName"] for feat in geo["features"]}
    noms_data = set(agg["prefecture_geojson"])

    manquants_dans_geojson = noms_data - noms_geojson
    manquants_dans_data = noms_geojson - noms_data

    print(f"Prefectures agregees : {len(agg)}")
    print(f"Zones dans le GeoJSON : {len(noms_geojson)}")
    if manquants_dans_geojson:
        print(f"\n⚠️ Dans les donnees mais absents du GeoJSON : {manquants_dans_geojson}")
    if manquants_dans_data:
        print(f"\n⚠️ Dans le GeoJSON mais absents des donnees : {manquants_dans_data}")
    if not manquants_dans_geojson and not manquants_dans_data:
        print("\n✅ Correspondance parfaite entre les donnees et le GeoJSON.")
    # "Lome Commune" est une sous-partie de Golfe non suivie separement dans nos
    # donnees — on lui attribue les memes indicateurs que Golfe pour eviter un
    # trou visuel sur la carte, plutot que de la laisser sans donnee.
    if "Golfe" in agg["prefecture_geojson"].values:
        ligne_golfe = agg[agg["prefecture_geojson"] == "Golfe"].copy()
        ligne_golfe["prefecture_geojson"] = "Lome Commune"
        agg = pd.concat([agg, ligne_golfe], ignore_index=True)
    agg.to_csv(DATA_PROCESSED / "couverture_pour_choroplethe.csv", index=False)
    print(f"\n-> Sauvegarde dans {DATA_PROCESSED / 'couverture_pour_choroplethe.csv'}")


if __name__ == "__main__":
    main()