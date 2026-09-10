"""
Dashboard Streamlit — Défi 1 Économie Numérique (Togo AI Lab)
Diagnostic de l'accès aux télécommunications et services numériques au Togo.
"""
import sys
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.plugins import MarkerCluster

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))
from load_data import load_agences_togocom, load_agences_moov, load_mobile_money, load_datacenters  # noqa: E402

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
[data-testid="stSidebar"] .stRadio > div {
    gap: 4px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #12161c;
    border: 1px solid #2a2f38 !important;
    border-radius: 10px !important;
    padding: 4px 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    transition: border-color 0.15s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: #22c55e !important;
    box-shadow: 0 2px 12px rgba(34,197,94,0.15);
}

.stButton > button {
    background-color: #1c2128 !important;
    color: #e6e6e6 !important;
    border: none !important;
    border-radius: 24px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #262b33 !important;
    box-shadow: 0 6px 16px rgba(0,0,0,0.4) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
    background-color: #22c55e !important;
    color: #0e1117 !important;
    box-shadow: 0 4px 14px rgba(34,197,94,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #16a34a !important;
    box-shadow: 0 6px 18px rgba(34,197,94,0.45) !important;
    transform: translateY(-1px);
}

hr { border-color: #2a2f38 !important; }
</style>
""", unsafe_allow_html=True)

if "mode_clair" not in st.session_state:
    st.session_state.mode_clair = False

if st.session_state.mode_clair:
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f5f5f5 !important;
        color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #d0d0d0;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-color: #d0d0d0 !important;
    }
    h1, h2, h3, p, span, div, label { color: #1a1a1a !important; }
    .kpi-label { color: #6b7280 !important; }
    .narrative { background-color: #f0f0f0 !important; color: #333 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Données (chargées une fois, avant tout le reste) ---
couverture = pd.read_csv(DATA_PROCESSED / "couverture_par_prefecture.csv")
togocom = load_agences_togocom()
moov = load_agences_moov()
agences_tot = pd.concat([togocom, moov], ignore_index=True)
mm = load_mobile_money()
datacenters = load_datacenters()
# --- Barre latérale : identité + navigation par axes ---
col_logo_sb, col_titre_sb = st.sidebar.columns([1, 3])
with col_logo_sb:
    st.image(str(BASE_DIR / "dashboard" / "assets" / "logo_connectivite.png"), width=45)
with col_titre_sb:
    st.markdown("### Atlas Connectivité")
st.sidebar.caption("TOGO · DÉFI 1 ÉCONOMIE NUMÉRIQUE")

st.sidebar.divider()
if st.sidebar.button("☀️ Mode clair" if not st.session_state.mode_clair else "🌙 Mode sombre"):
    st.session_state.mode_clair = not st.session_state.mode_clair
    st.rerun()
st.sidebar.divider()

st.sidebar.markdown(
    '<span class="axe-tag" style="font-size:11px;">NAVIGATION</span>',
    unsafe_allow_html=True,
)

page_labels_list = [
    "📊 Vue d'ensemble",
    "📡 Infrastructures",
    "🗺️ Couverture par préfecture",
    "📍 Cartographie",
    "🎯 Recommandations",
]

if "page_active" not in st.session_state:
    st.session_state.page_active = page_labels_list[0]

for label in page_labels_list:
    est_actif = st.session_state.page_active == label
    if st.sidebar.button(
        label,
        key=f"nav_{label}",
        type="primary" if est_actif else "secondary",
        use_container_width=True,
    ):
        st.session_state.page_active = label
        st.rerun()

page_labels = {
    "📊 Vue d'ensemble": "Vue d'ensemble",
    "📡 Infrastructures": "Infrastructures",
    "🗺️ Couverture par préfecture": "Couverture par préfecture",
    "📍 Cartographie": "Cartographie",
    "🎯 Recommandations": "Recommandations",
}
page = page_labels[st.session_state.page_active]

st.sidebar.divider()
st.sidebar.caption(f"📌 {len(couverture)} préfectures · 5 régions")
st.sidebar.caption(
    f"📶 {int(couverture['nb_agences'].sum())} agences · "
    f"{int(couverture['nb_points_mobile_money'].sum()):,}".replace(",", " ")
    + " points mobile money"
)
st.sidebar.caption("🗓️ Recensement 2022")
st.sidebar.caption("🔗 geodata.gouv.tg")

# --- En-tête institutionnel (présent sur toutes les pages) ---
col_titre, col_logo = st.columns([4, 1.5])

with col_titre:
    st.markdown(
        "<div style='color:#22c55e; font-size:12px; letter-spacing:3px; "
        "font-weight:600; margin-bottom:6px;'>SYNTHÈSE NATIONALE</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:38px; font-weight:800; color:#f0f0f0; "
        "line-height:1.15; margin-bottom:10px;'>"
        "Diagnostic connectivité et<br>services numériques</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='color:#8b949e; font-size:15px;'>"
        "Où en est le Togo sur l'accès aux télécommunications, et quelles "
        "préfectures restent en marge de la connectivité ?"
        "</div>",
        unsafe_allow_html=True,
    )

with col_logo:
    col_texte, col_embleme = st.columns([3, 1])
    with col_texte:
        st.markdown(
            "<div style='text-align:right; padding-top:18px;'>"
            "<div style='font-size:13px; font-weight:700; color:#e6e6e6;'>"
            "République togolaise · Togo AI Lab </div>"
            "<div style='font-size:11px; letter-spacing:2px; color:#8b949e; "
            "margin-top:4px;'>DATA CHALLENGE ÉCONOMIE NUMÉRIQUE</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        with col_embleme:
            st.image(str(BASE_DIR / "dashboard" / "assets" / "image.png"), width=70)

st.divider()


def kpi(label, value, sub=""):
    with st.container(border=True):
        st.markdown(
            f'<div style="padding:6px 10px 2px 10px;">'
            f'<span class="kpi-label">{label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="padding:0 10px; font-size:28px; font-weight:800; '
            f'color:#f0f0f0;">{value}</div>',
            unsafe_allow_html=True,
        )
        if sub:
            st.markdown(
                f'<div style="padding:2px 10px 8px 10px;">'
                f'<span style="color:#22c55e;">●</span> '
                f'<span class="kpi-sub">{sub}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


def narrative(text):
    st.markdown(f'<div class="narrative">{text}</div>', unsafe_allow_html=True)


def section_header(titre, aide=""):
    if aide:
        st.markdown(f"**❓ {titre}**", help=aide)
    else:
        st.markdown(f"**{titre}**")


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
        section_header("Répartition par opérateur", aide="Nombre d'agences physiques par opérateur télécom")
        st.bar_chart(agences_tot["operateur"].value_counts(), color="#22c55e")
        narrative(
            f"Togocom compte {(agences_tot['operateur'] == 'Togocom').sum()} agences "
            f"contre {(agences_tot['operateur'] == 'Moov').sum()} pour Moov — un rapport "
            f"de plus de 2 pour 1."
        )
        with st.expander("Voir plus — détail par opérateur"):
            st.dataframe(
                agences_tot["operateur"].value_counts().rename_axis("opérateur").reset_index(name="nb_agences"),
                use_container_width=True,
            )

    with col_b:
        section_header("Répartition par région", aide="Nombre d'agences physiques par région administrative")
        st.bar_chart(agences_tot["region_nom_bdd"].value_counts(), color="#22c55e")
        top_region = agences_tot["region_nom_bdd"].value_counts().idxmax()
        part = agences_tot["region_nom_bdd"].value_counts().max() / len(agences_tot) * 100
        narrative(
            f"La région {top_region} concentre à elle seule {part:.0f} % des agences "
            f"du pays, portée par le Grand Lomé."
        )
        with st.expander("Voir plus — détail par région"):
            st.dataframe(
                agences_tot["region_nom_bdd"].value_counts().rename_axis("région").reset_index(name="nb_agences"),
                use_container_width=True,
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

    mediane = couverture["agences_pour_100k_hab"].median()
    sous_mediane = (data["agences_pour_100k_hab"] < mediane).sum()
    narrative(
        f"{sous_mediane} préfecture(s) sur {len(data)} affichées sont sous la médiane "
        f"nationale de {mediane:.2f} agence(s) pour 100 000 habitants."
    )

# ============================================================
# PAGE : CARTOGRAPHIE
# ============================================================
elif page == "Cartographie":
    st.markdown('<span class="axe-tag">AXE · CARTOGRAPHIE & ACTION</span>', unsafe_allow_html=True)
    st.subheader("Où investir en premier")

    @st.cache_data
    def compute_priorite():
        c = couverture.copy()
        c["priorite"] = pd.qcut(
            c["agences_pour_100k_hab"].rank(method="first"),
            5,
            labels=["Très prioritaire", "Prioritaire", "À surveiller", "Modéré", "Satisfaisant"],
        )
        return c

    @st.cache_resource
    def build_map():
            with open(BASE_DIR / "data" / "raw" / "togo_prefectures.geojson", encoding="utf-8") as f:
                geo = json.load(f)

            choro_data = pd.read_csv(DATA_PROCESSED / "couverture_pour_choroplethe.csv")
            cp  = compute_priorite()

            m = folium.Map(
                location=[8.6, 1.0],
                zoom_start=7,
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
                attr="Esri, HERE, Garmin, FAO, NOAA, USGS",
            )

            # Choropleth leger, seul calque actif par defaut
            choropleth = folium.Choropleth(
                geo_data=geo,
                name="Agences pour 100k hab.",
                data=choro_data,
                columns=["prefecture_geojson", "agences_pour_100k_hab"],
                key_on="feature.properties.shapeName",
                fill_color="RdYlGn",
                fill_opacity=0.35,
                line_opacity=0.4,
                line_color="#0e1117",
                legend_name="Agences pour 100 000 habitants",
                nan_fill_color="#333333",
            ).add_to(m)
            choropleth.geojson.add_child(
                folium.GeoJsonTooltip(fields=["shapeName"], aliases=["Préfecture :"])
            )

            # Losanges de priorite (un par prefecture) - calque principal, propre
            couleurs_hex = {
                "Très prioritaire": "#ef4444",
                "Prioritaire": "#f97316",
                "À surveiller": "#eab308",
                "Modéré": "#3b82f6",
                "Satisfaisant": "#22c55e",
            }
            for _, row in cp.iterrows():
                pts = mm[mm["prefecture_nom_bdd"] == row["prefecture"]]
                if len(pts) == 0:
                    continue
                lat, lon = pts["lat"].mean(), pts["lon"].mean()
                couleur = couleurs_hex[row["priorite"]]
                icone_losange = f"""
                    <div style="
                        width: 16px; height: 16px;
                        background: {couleur};
                        border: 2px solid #0e1117;
                        transform: rotate(45deg);
                        box-shadow: 0 0 4px rgba(0,0,0,0.5);
                    "></div>
                """
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(html=icone_losange, icon_size=(16, 16), icon_anchor=(8, 8)),
                    tooltip=(
                        f"{row['prefecture']} — {row['priorite']}<br>"
                        f"{row['nb_agences']} agence(s) · {row['population_2022']:,} hab."
                    ),
                ).add_to(m)

            # Calques optionnels, desactives par defaut (pour ne pas surcharger)
            cluster_agences = folium.FeatureGroup(name="Agences individuelles", show=False)
            for _, row in togocom.iterrows():
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]], radius=4,
                    color="#1f77b4", fill=True, fill_opacity=0.8,
                    tooltip=f"Togocom - {row.get('etab_nom', 'Agence')}",
                ).add_to(cluster_agences)
            for _, row in moov.iterrows():
                folium.CircleMarker(
                    location=[row["lat"], row["lon"]], radius=4,
                    color="#ff7f0e", fill=True, fill_opacity=0.8,
                    tooltip=f"Moov - {row.get('etab_nom', 'Agence')}",
                ).add_to(cluster_agences)
            cluster_agences.add_to(m)

            for _, row in datacenters.iterrows():
                folium.Marker(
                    location=[row["lat"], row["lon"]],
                    icon=folium.Icon(color="purple", icon="server", prefix="fa"),
                    tooltip=f"Datacenter — {row.get('etab_nom', 'Centre de données')}",
                ).add_to(m)

            with open(DATA_PROCESSED / "densite_bounds.json") as f:
                bounds_densite = json.load(f)
            folium.raster_layers.ImageOverlay(
                image=str(DATA_PROCESSED / "densite_population.png"),
                bounds=[
                    [bounds_densite["south"], bounds_densite["west"]],
                    [bounds_densite["north"], bounds_densite["east"]],
                ],
                opacity=0.6,
                name="Densité de population (WorldPop 2020)",
                show=False,
            ).add_to(m)

            folium.LayerControl().add_to(m)
            return m

    if st.button("🗺️ Afficher la carte", type="primary"):
        with st.spinner("Génération de la carte..."):
            carte_html = build_map().get_root().render()
        components.html(carte_html, width=1200, height=600)
    else:
        st.info("Clique sur le bouton ci-dessus pour charger la carte.")
        st.write("")
    st.caption("🟣 Marqueurs violets = centres de données (3 sites recensés)")
    st.caption("🔥 Fond orange/jaune = densité de population réelle (WorldPop 2020, résolution 100m)")
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

    st.markdown("**1 · Priorité absolue**")
    if len(zones_critiques) > 0:
        noms = ", ".join(zones_critiques["prefecture"].tolist())
        st.error(f"Aucune présence télécom (ni agence ni mobile money) : {noms}")
    else:
        st.success("Aucune préfecture n'est totalement dépourvue de présence télécom.")

    st.markdown("**2 · Fort potentiel commercial**")
    if len(zones_grosse_pop) > 0:
        noms = ", ".join(
            f"{r['prefecture']} ({r['population_2022']:,} hab.)"
            for _, r in zones_grosse_pop.iterrows()
        )
        st.warning(f"Préfectures peuplées (>150 000 hab.) sans agence : {noms}")

    st.markdown("**3 · Recommandation méthodologique**")
    st.info(
        "Le Togo ne dispose d'aucune donnée ouverte de couverture réseau cellulaire "
        "(2G/3G/4G). La publication de ces données par l'ARCEP, à l'image de son "
        "homologue français, permettrait un diagnostic plus complet à l'avenir."
    )

    narrative(
        f"En croisant infrastructure et démographie, {len(zones_grosse_pop)} "
        f"préfecture(s) representent une priorité d'expansion à fort impact : "
        f"population importante, zéro agence, coût d'opportunité élevé pour les "
        f"opérateurs qui n'y sont pas encore implantés."
    )

st.divider()
st.caption(
    "⚠️ Limitation méthodologique : aucune donnée ouverte de couverture réseau "
    "cellulaire (2G/3G/4G) n'existe pour le Togo. La présence des agences "
    "télécoms et des points mobile money est utilisée comme proxy indirect."
)

