"""
Identifie les points mobile money dont le nom de prefecture ne correspond
a aucune des 39 prefectures officielles (recensement 2022) - la cause
probable de l'ecart entre le total brut (19 788) et le total agrege
utilise dans le dashboard (19 629).
"""
import pandas as pd

from load_data import load_mobile_money

mm = load_mobile_money()
demo = pd.read_csv("../data/processed/prefectures_demographie.csv")

prefectures_officielles = set(demo["prefecture"])
prefectures_mm = set(mm["prefecture_nom_bdd"].dropna().unique())

orphelines = prefectures_mm - prefectures_officielles

print(f"Total points mobile money (brut) : {len(mm)}")
print(f"Prefectures dans le fichier mobile money : {len(prefectures_mm)}")
print(f"Prefectures officielles (recensement) : {len(prefectures_officielles)}")

if orphelines:
    print(f"\n⚠️ Noms de prefecture SANS correspondance officielle :")
    for nom in sorted(orphelines):
        nb = (mm["prefecture_nom_bdd"] == nom).sum()
        print(f"  - '{nom}' : {nb} points")
    total_orphelin = mm[mm["prefecture_nom_bdd"].isin(orphelines)].shape[0]
    print(f"\nTotal de points orphelins : {total_orphelin}")
else:
    print("\n✅ Toutes les prefectures correspondent.")

# Valeurs manquantes
manquants = mm["prefecture_nom_bdd"].isna().sum()
print(f"\nPoints avec prefecture manquante (NaN) : {manquants}")