## Limitation méthodologique : couverture réseau mobile

Aucune donnée ouverte de couverture réseau cellulaire (2G/3G/4G) n'est disponible
pour le Togo :
- ARCEP Togo publie des rapports de qualité de service (PDF), sans données SIG
  téléchargeables.
- GSMA Coverage Explorer nécessite un accès payant/entreprise.
- OpenCellID (base communautaire ouverte) ne recense que 33 antennes pour tout
  le Togo, toutes concentrées sur le Grand Lomé — inexploitable comme indicateur
  national.

**Choix retenu** : la présence des agences télécoms (Togocom, Moov) et des points
mobile money est utilisée comme *proxy indirect* de la présence des opérateurs
sur le territoire, en l'absence de données de couverture radio. Cette limite
est mentionnée explicitement dans le rapport final.

## Statut

- [x] Création du projet et récupération des données brutes
- [x] Nettoyage / extraction des coordonnées (lon, lat)
- [x] Recherche de la donnée démographique (recensement 2022 + WorldPop 100m)
- [x] Indicateurs de couverture par préfecture/commune/canton
- [x] Identification des zones blanches (39 préfectures, 372 cantons)
- [x] Dashboard (Streamlit)
- [x] Rapport PowerPoint (10 diapositives)

## Corrections notables

- Une faute de frappe dans les données sources (`Tandjoaré` au lieu de
  `Tandjouaré`) faisait perdre 159 points mobile money de l'agrégation.
  Corrigée dans `src/load_data.py`.

## Livrables finaux

- `dashboard/app.py` — dashboard Streamlit (voir README pour lancement)
- `diagnostic_connectivite_togo.pptx` — rapport de synthèse (10 slides)