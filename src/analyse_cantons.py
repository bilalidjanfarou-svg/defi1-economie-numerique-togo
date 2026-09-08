"""
Identifie, pour chaque préfecture, si les agences sont concentrées
dans un seul canton (souvent la capitale) ou réparties.
Complète l'analyse zones blanches faite au niveau préfecture.
"""
import pandas as pd
from load_data import load_agences_togocom, load_agences_moov, load_mobile_money

def main():
    togocom = load_agences_togocom()
    moov = load_agences_moov()
    agences = pd.concat([togocom, moov], ignore_index=True)

    # Nombre de cantons différents touchés, par préfecture
    concentration = (
        agences.groupby("prefecture_nom_bdd")["canton_nom_bdd"]
        .nunique()
        .rename("nb_cantons_avec_agence")
        .reset_index()
        .rename(columns={"prefecture_nom_bdd": "prefecture"})
    )

    nb_agences = (
        agences.groupby("prefecture_nom_bdd")
        .size()
        .rename("nb_agences")
        .reset_index()
        .rename(columns={"prefecture_nom_bdd": "prefecture"})
    )

    result = nb_agences.merge(concentration, on="prefecture")
    result["ratio_concentration"] = (
        result["nb_cantons_avec_agence"] / result["nb_agences"]
    ).round(2)

    # Cas les plus concentrés : plusieurs agences, mais dans 1 seul canton
    concentres = result[
        (result["nb_agences"] >= 3) & (result["nb_cantons_avec_agence"] == 1)
    ].sort_values("nb_agences", ascending=False)

    print("Préfectures avec plusieurs agences mais toutes dans UN SEUL canton :")
    print(concentres)

    # Total de cantons distincts au Togo (via mobile money, qui couvre presque tout)
    mm = load_mobile_money()
    tous_cantons = set(mm["canton_nom_bdd"].dropna().unique())
    cantons_avec_agence = set(agences["canton_nom_bdd"].dropna().unique())
    cantons_sans_agence = tous_cantons - cantons_avec_agence

    print(f"\nNombre total de cantons (via mobile money) : {len(tous_cantons)}")
    print(f"Cantons avec au moins 1 agence : {len(cantons_avec_agence)}")
    print(f"Cantons SANS agence : {len(cantons_sans_agence)}")

    result.to_csv("../data/processed/concentration_par_prefecture.csv", index=False)
    print("\n-> Sauvegardé dans data/processed/concentration_par_prefecture.csv")

if __name__ == "__main__":
    main()