"""
Dashboard Streamlit — Défi 1 Économie Numérique (Togo AI Lab)
Diagnostic de l'accès aux télécommunications et services numériques au Togo.
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))
from load_data import load_agences_togocom, load_agences_moov, load_mobile_money  # noqa: E402

DATA_PROCESSED = BASE_DIR / "data" / "processed"

st.set_page_config(page_title="Défi 1 - Économie Numérique Togo", layout="wide")
st.title("📡 Diagnostic connectivité et services numériques — Togo")
st.caption("Togo AI Lab · Défi 1 Économie Numérique")

# --- Chargement des données ---
couverture = pd.read_csv(DATA_PROCESSED / "couverture_par_prefecture.csv")

# --- KPIs principaux ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Préfectures sans agence", f"{(couverture['nb_agences'] == 0).sum()} / 39")
col2.metric("Total agences (Togocom + Moov)", int(couverture["nb_agences"].sum()))
col3.metric("Total points mobile money", int(couverture["nb_points_mobile_money"].sum()))
col4.metric("Cantons sans agence", "326 / 372")

st.divider()

# --- Tableau préfectures les moins équipées ---
st.subheader("Préfectures les moins bien équipées (agences pour 100 000 hab.)")
st.dataframe(
    couverture.sort_values("agences_pour_100k_hab")[
        ["prefecture", "region", "population_2022", "nb_agences",
         "agences_pour_100k_hab", "nb_points_mobile_money"]
    ].head(15),
    use_container_width=True,
)

st.divider()

# --- Carte ---
st.subheader("Carte des infrastructures et zones blanches")

@st.cache_data
def build_map():
    m = folium.Map(location=[8.6, 1.0], zoom_start=7, tiles="OpenStreetMap")

    togocom = load_agences_togocom()
    for _, row in togocom.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]], radius=5,
            color="#1f77b4", fill=True, fill_opacity=0.8,
            tooltip=f"Togocom - {row.get('etab_nom', 'Agence')}",
        ).add_to(m)

    moov = load_agences_moov()
    for _, row in moov.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]], radius=5,
            color="#ff7f0e", fill=True, fill_opacity=0.8,
            tooltip=f"Moov - {row.get('etab_nom', 'Agence')}",
        ).add_to(m)

    mm = load_mobile_money()
    mm_layer = folium.FeatureGroup(name="Mobile Money", show=False)
    for _, row in mm.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]], radius=1.5,
            color="#7f7f7f", fill=True, fill_opacity=0.4,
        ).add_to(mm_layer)
    mm_layer.add_to(m)

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
    return m

st_folium(build_map(), width=1200, height=600)

st.divider()

# --- Répartition par opérateur et par région ---
st.subheader("Répartition des agences par opérateur et par région")

col_a, col_b = st.columns(2)

togocom = load_agences_togocom()
moov = load_agences_moov()
agences_tot = pd.concat([togocom, moov], ignore_index=True)

with col_a:
    par_operateur = agences_tot["operateur"].value_counts()
    st.bar_chart(par_operateur)
    st.caption("Nombre d'agences par opérateur")

with col_b:
    par_region = agences_tot["region_nom_bdd"].value_counts()
    st.bar_chart(par_region)
    st.caption("Nombre d'agences par région")

st.divider()

# --- Classement complet des 39 préfectures ---
st.subheader("Classement complet des 39 préfectures")
st.dataframe(
    couverture.sort_values("agences_pour_100k_hab")[
        ["prefecture", "region", "population_2022", "nb_agences",
         "agences_pour_100k_hab", "nb_points_mobile_money",
         "mobile_money_pour_100k_hab"]
    ],
    use_container_width=True,
    height=400,
)
st.divider()
st.caption(
    "⚠️ Limitation méthodologique : aucune donnée ouverte de couverture réseau "
    "cellulaire (2G/3G/4G) n'existe pour le Togo. La présence des agences "
    "télécoms et des points mobile money est utilisée comme proxy indirect."
)