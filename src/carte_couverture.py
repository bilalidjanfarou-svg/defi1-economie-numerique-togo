"""
Carte interactive : agences télécoms, points mobile money, et zones blanches
(préfectures sans agence), avec un marqueur par capitale de préfecture.
"""
from pathlib import Path
import folium
import pandas as pd
from load_data import load_agences_togocom, load_agences_moov, load_mobile_money

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DASHBOARD_DIR = BASE_DIR / "dashboard"
DASHBOARD_DIR.mkdir(exist_ok=True)

# Centre approximatif du Togo — OpenStreetMap, pas besoin de clé API
m = folium.Map(location=[8.6, 1.0], zoom_start=7, tiles="OpenStreetMap")

# Agences télécoms (bleu = Togocom, orange = Moov)
togocom = load_agences_togocom()
for _, row in togocom.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=5, color="#1f77b4", fill=True, fill_opacity=0.8,
        tooltip=f"Togocom - {row.get('etab_nom', 'Agence')}",
        popup=f"Togocom - {row.get('etab_nom', '')}",
    ).add_to(m)

moov = load_agences_moov()
for _, row in moov.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=5, color="#ff7f0e", fill=True, fill_opacity=0.8,
        tooltip=f"Moov - {row.get('etab_nom', 'Agence')}",
        popup=f"Moov - {row.get('etab_nom', '')}",
    ).add_to(m)

# Points mobile money : couche désactivée par défaut (trop dense sinon)
mm = load_mobile_money()
mm_layer = folium.FeatureGroup(name="Mobile Money", show=False)
for _, row in mm.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=1.5, color="#7f7f7f", fill=True, fill_opacity=0.4,
    ).add_to(mm_layer)
mm_layer.add_to(m)

# Préfectures sans agence : marqueur rouge
couverture = pd.read_csv(DATA_PROCESSED / "couverture_par_prefecture.csv")
zones_blanches = couverture[couverture["nb_agences"] == 0]
for _, row in zones_blanches.iterrows():
    pts = mm[mm["prefecture_nom_bdd"] == row["prefecture"]]
    if len(pts) > 0:
        lat, lon = pts["lat"].mean(), pts["lon"].mean()
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color="red", icon="exclamation-sign"),
            popup=f"ZONE BLANCHE: {row['prefecture']} ({row['population_2022']:,} hab.)",
        ).add_to(m)

folium.LayerControl().add_to(m)
output_path = DASHBOARD_DIR / "carte_couverture.html"
m.save(str(output_path))
print(f"Carte sauvegardée dans {output_path}")