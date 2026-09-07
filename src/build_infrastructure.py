"""
Fusionne les agences télécoms (Togocom + Moov) en une seule table,
et calcule le nombre d'agences par préfecture et par canton
pour repérer les zones sans aucune agence (zones blanches "infrastructure").
"""
import pandas as pd
from load_data import load_agences_togocom, load_agences_moov, load_datacenters

def build_agences():
    togocom = load_agences_togocom()
    moov = load_agences_moov()
    agences = pd.concat([togocom, moov], ignore_index=True)
    return agences

if __name__ == "__main__":
    agences = build_agences()
    print(f"Total agences (Togocom + Moov) : {len(agences)}")

    print("\nAgences par préfecture :")
    print(agences["prefecture_nom_bdd"].value_counts())

    print("\nNombre de préfectures SANS aucune agence :")
    toutes_prefectures = set(agences["prefecture_nom_bdd"].dropna().unique())
    print(f"Préfectures couvertes : {len(toutes_prefectures)}")

    print("\nAgences par canton (top 10 et zones à 1 seule agence) :")
    par_canton = agences["canton_nom_bdd"].value_counts()
    print(par_canton.head(10))
    print(f"\nNombre de cantons avec exactement 1 agence : {(par_canton == 1).sum()}")

    # Sauvegarde pour la suite
    agences.to_csv("../data/processed/agences_fusionnees.csv", index=False)
    print("\n-> Sauvegardé dans data/processed/agences_fusionnees.csv")