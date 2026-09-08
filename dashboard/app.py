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
from folium.plugins import HeatMap, MarkerCluster

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))
from load_data import load_agences_togocom, load_agences_moov, load_mobile_money  # noqa: E402

DATA_PROCESSED = BASE_DIR / "data" / "processed"

st.set_page_config(
    page_title="Diagnostic Connectivité Togo",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS custom : look "atlas institutionnel" sombre / monospace ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"], .stMarkdown, .stDataFrame, [data-testid="stSidebar"] {
    font-family: 'JetBrains Mono', 'Courier New', monospace !important;
}

h1, h2, h3 { letter-spacing: -0.5px; }

.kpi-label {
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #8b949e;
}
.kpi-sub {
    font-size: 12px;
    color: #22c55e;
    font-weight: 600;
}
.axe-tag {
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #22c55e;
    font-weight: 600;
}
.narrative {
    font-size: 14px;
    line-height: 1.6;
    color: #c9d1d9;
    background-color: #161b22;
    border-left: 3px solid #22c55e;
    padding: 12px 16px;
    border-radius: 4px;
    margin-top: 10px;
}

[data-testid="stSidebar"] {
    border-right: 1px solid #2a2f38;
}
[data-testid="stSidebar"] label {
    font-size: 14px;
}

/* Boutons radio de la sidebar : espacement plus aere */
[data-testid="stSidebar"] .stRadio > div {
    gap: 4px;
}

hr { border-color: #2a2f38 !important; }
</style>
""", unsafe_allow_html=True)

# --- Données (chargées une fois, avant tout le reste) ---
couverture = pd.read_csv(DATA_PROCESSED / "couverture_par_prefecture.csv")
togocom = load_agences_togocom()
moov = load_agences_moov()
agences_tot = pd.concat([togocom, moov], ignore_index=True)
mm = load_mobile_money()

# --- Barre latérale : identité + navigation par axes ---
st.sidebar.markdown("### 📡 Atlas Connectivité")
st.sidebar.caption("TOGO · DÉFI 1 ÉCONOMIE NUMÉRIQUE")
st.sidebar.divider()

st.sidebar.markdown("**SYNTHÈSE**")
page_labels = {
    "📊 Vue d'ensemble": "Vue d'ensemble",
    "📡 Infrastructures": "Infrastructures",
    "🗺️ Couverture par préfecture": "Couverture par préfecture",
    "📍 Cartographie": "Cartographie",
    "🎯 Recommandations": "Recommandations",
}
choix_affiche = st.sidebar.radio(
    label="navigation",
    options=list(page_labels.keys()),
    label_visibility="collapsed",
)
page = page_labels[choix_affiche]

st.sidebar.divider()
st.sidebar.caption(f"{len(couverture)} préfectures · 5 régions")
st.sidebar.caption("Recensement 2022 · geodata.gouv.tg")

# --- En-tête institutionnel (présent sur toutes les pages) ---
col_titre, col_logo = st.columns([4, 1])
with col_titre:
    st.markdown('<span class="axe-tag">SYNTHÈSE NATIONALE</span>', unsafe_allow_html=True)
    st.title("Diagnostic connectivité et services numériques")
with col_logo:
    st.markdown(
        "<div style='text-align:right; font-size:12px; color:#8b949e; padding-top:20px;'>"
        "République togolaise<br>Togo AI Lab — Défi Économie Numérique"
        "</div>",
        unsafe_allow_html=True,
    )

st.divider()


def kpi(label, value, sub=""):
    with st.container(border=True):
        st.markdown(
            f'<span class="kpi-label">{label}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f"### {value}")
        if sub:
            st.markdown(
                f'<span class="kpi-sub">{sub}</span>',
                unsafe_allow_html=True,
            )


def narrative(text):
    st.markdown(f'<div class="narrative">{text}</div>', unsafe_allow_html=True)


# ============================================================
# PAGE : VUE D'ENSEMBLE
# ============================================================
if page == "Vue d'ensemble":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi("Préfectures sans agence", f"{(couverture['nb_agences'] == 0).sum()} / 39")
    with c2:
        kpi("Total agences", int(couverture["nb_agences"].sum()), "Togocom + Moov")
    with c3:
        kpi("Points mobile money", f"{int(couverture['nb_points_mobile_money'].sum()):,}".replace(",", " "))
    with c4:
        kpi("Cantons sans agence", "326 / 372", "88 % du territoire")

    st.write("")
    st.subheader("Où sont les zones blanches")
    st.dataframe(
        couverture.sort_values("agences_pour_100k_hab")[
            ["prefecture", "region", "population_2022", "nb_agences", "agences_pour_100k_hab"]
        ].head(12),
        use_container_width=True,
    )
    narrative(
        "12 préfectures n'ont aucune agence télécom, dont Lacs et Vo qui comptent "
        "à elles seules plus de 460 000 habitants : l'absence d'agence n'y est pas "
        "un effet de faible population."
    )

# ============================================================
# PAGE : INFRASTRUCTURES
# ============================================================
elif page == "Infrastructures":
    st.markdown('<span class="axe-tag">AXE · INFRASTRUCTURES</span>', unsafe_allow_html=True)
    st.subheader("Répartition des agences")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Par opérateur**")
        st.bar_chart(agences_tot["operateur"].value_counts(), color="#22c55e")
        narrative(
            f"Togocom compte {(agences_tot['operateur'] == 'Togocom').sum()} agences "
            f"contre {(agences_tot['operateur'] == 'Moov').sum()} pour Moov — un rapport "
            f"de plus de 2 pour 1."
        )
    with col_b:
        st.markdown("**Par région**")
        st.bar_chart(agences_tot["region_nom_bdd"].value_counts(), color="#22c55e")
        top_region = agences_tot["region_nom_bdd"].value_counts().idxmax()
        part = agences_tot["region_nom_bdd"].value_counts().max() / len(agences_tot) * 100
        narrative(
            f"La région {top_region} concentre à elle seule {part:.0f} % des agences "
            f"du pays, portée par le Grand Lomé."
        )

    st.write("")
    st.subheader("Concentration au sein des préfectures")
    concentration = pd.read_csv(DATA_PROCESSED / "concentration_par_prefecture.csv")
    concentres = concentration[
        (concentration["nb_agences"] >= 3) & (concentration["nb_cantons_avec_agence"] == 1)
    ].sort_values("nb_agences", ascending=False)
    if len(concentres) > 0:
        st.dataframe(concentres, use_container_width=True)
        narrative(
            f"{len(concentres)} préfecture(s) ont plusieurs agences mais toutes "
            f"regroupées dans un seul et même canton — signe que la couverture "
            f"intra-préfectorale reste très inégale, même là où des agences existent."
        )

# ============================================================
# PAGE : COUVERTURE PAR PRÉFECTURE
# ============================================================
elif page == "Couverture par préfecture":
    st.markdown('<span class="axe-tag">AXE · COUVERTURE</span>', unsafe_allow_html=True)
    st.subheader("Classement complet des 39 préfectures")

    regions_dispo = ["Toutes"] + sorted(couverture["region"].unique().tolist())
    region_choisie = st.selectbox("Filtrer par région", regions_dispo)
    data = couverture if region_choisie == "Toutes" else couverture[couverture["region"] == region_choisie]

    st.dataframe(
        data.sort_values("agences_pour_100k_hab")[
            ["prefecture", "region", "population_2022", "nb_agences",
             "agences_pour_100k_hab", "nb_points_mobile_money", "mobile_money_pour_100k_hab"]
        ],
        use_container_width=True,
        height=450,
    )

# ============================================================
# PAGE : CARTOGRAPHIE
# ============================================================
elif page == "Cartographie":
    st.markdown('<span class="axe-tag">AXE · CARTOGRAPHIE & ACTION</span>', unsafe_allow_html=True)
    st.subheader("Où investir en premier")

        
    @st.cache_data
    def compute_priorite():
        """Score de priorité 1 (satisfaisant) à 5 (très prioritaire),
        base sur agences_pour_100k_hab (moins d'agences = plus prioritaire)."""
        c = couverture.copy()
        c["priorite"] = pd.qcut(
            c["agences_pour_100k_hab"].rank(method="first"),
            5,
            labels=["Très prioritaire", "Prioritaire", "À surveiller", "Modéré", "Satisfaisant"],
        )
        return c

    @st.cache_data
    def build_map():
        m = folium.Map(location=[8.6, 1.0], zoom_start=7, tiles="CartoDB dark_matter")
        cluster_agences = MarkerCluster(name="Agences").add_to(m)
        # Agences : gardees en points individuels (seulement 90, pas de souci de perf)
        for _, row in togocom.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]], radius=5,
                color="#1f77b4", fill=True, fill_opacity=0.8,
                tooltip=f"Togocom - {row.get('etab_nom', 'Agence')}",
            ).add_to(cluster_agences)
        for _, row in moov.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]], radius=5,
                color="#ff7f0e", fill=True, fill_opacity=0.8,
                tooltip=f"Moov - {row.get('etab_nom', 'Agence')}",
            ).add_to(cluster_agences)
        # Mobile money : heatmap en un seul calque (rapide, meme avec 19 788 points)
        heat_data = mm[["lat", "lon"]].values.tolist()
        HeatMap(heat_data, radius=8, blur=6, min_opacity=0.3, name="Densite mobile money", show=False).add_to(m)

        # Marqueurs de priorite par prefecture (couleur selon niveau)
        couleurs_priorite = {
            "Très prioritaire": "red",
            "Prioritaire": "orange",
            "À surveiller": "beige",
            "Modéré": "lightblue",
            "Satisfaisant": "green",
        }
        cp = compute_priorite()
        for _, row in cp.iterrows():
            pts = mm[mm["prefecture_nom_bdd"] == row["prefecture"]]
            if len(pts) > 0:
                lat, lon = pts["lat"].mean(), pts["lon"].mean()
            else:
                continue
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color=couleurs_priorite[row["priorite"]], icon="info-sign"),
                popup=(
                    f"{row['prefecture']} — {row['priorite']}<br>"
                    f"{row['nb_agences']} agence(s) · {row['population_2022']:,} hab."
                ),
                tooltip=row["prefecture"],
            ).add_to(m)

        folium.LayerControl().add_to(m)
        return m

    st_folium(build_map(), width=1200, height=600)

    st.write("")
    st.markdown("**Légende priorité** (basée sur le nombre d'agences pour 100 000 hab.)")
    leg1, leg2, leg3, leg4, leg5 = st.columns(5)
    leg1.markdown("🔴 Très prioritaire")
    leg2.markdown("🟠 Prioritaire")
    leg3.markdown("🟡 À surveiller")
    leg4.markdown("🔵 Modéré")
    leg5.markdown("🟢 Satisfaisant")

# ============================================================
# PAGE : RECOMMANDATIONS
# ============================================================
elif page == "Recommandations":
    st.markdown('<span class="axe-tag">DÉCISION</span>', unsafe_allow_html=True)
    st.subheader("Recommandations prioritaires")

    zones_critiques = couverture[
        (couverture["nb_agences"] == 0) & (couverture["nb_points_mobile_money"] == 0)
    ]
    zones_grosse_pop = couverture[
        (couverture["nb_agences"] == 0) & (couverture["population_2022"] > 150_000)
    ].sort_values("population_2022", ascending=False)

    if len(zones_critiques) > 0:
        noms = ", ".join(zones_critiques["prefecture"].tolist())
        st.error(f"**Priorité absolue** — aucune présence télécom : {noms}")

    if len(zones_grosse_pop) > 0:
        noms = ", ".join(
            f"{r['prefecture']} ({r['population_2022']:,} hab.)"
            for _, r in zones_grosse_pop.iterrows()
        )
        st.warning(f"**Fort potentiel commercial** sans agence : {noms}")

    st.info(
        "**Recommandation méthodologique** — Le Togo ne dispose d'aucune donnée "
        "ouverte de couverture réseau cellulaire. La publication de ces données "
        "par l'ARCEP permettrait un diagnostic plus complet."
    )

st.divider()
st.caption(
    "⚠️ Limitation méthodologique : aucune donnée ouverte de couverture réseau "
    "cellulaire (2G/3G/4G) n'existe pour le Togo. La présence des agences "
    "télécoms et des points mobile money est utilisée comme proxy indirect."
)