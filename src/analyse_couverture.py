"""
Croise les agences télécoms + les points mobile money avec la population
par préfecture, pour calculer un indicateur de couverture et repérer
les préfectures sous-équipées (zones blanches).
"""
import pandas as pd
from load_data import load_agences_togocom, load_agences_moov, load_mobile_money

DEMO_PATH = "../data/processed/prefectures_demographie.csv"


def build_agences():
    togocom = load_agences_togocom()
    moov = load_agences_moov()
    return pd.concat([togocom, moov], ignore_index=True)


def main():
    demo = pd.read_csv(DEMO_PATH)

    agences = build_agences()
    agences_par_pref = (
        agences.groupby("prefecture_nom_bdd")
        .size()
        .rename("nb_agences")
        .reset_index()
        .rename(columns={"prefecture_nom_bdd": "prefecture"})
    )

    mm = load_mobile_money()
    mm_par_pref = (
        mm.groupby("prefecture_nom_bdd")
        .size()
        .rename("nb_points_mobile_money")
        .reset_index()
        .rename(columns={"prefecture_nom_bdd": "prefecture"})
    )

    # Merge en partant de la liste OFFICIELLE des 39 préfectures (left join)
    # -> les préfectures absentes des fichiers d'agences apparaîtront avec NaN -> 0
    result = demo.merge(agences_par_pref, on="prefecture", how="left")
    result = result.merge(mm_par_pref, on="prefecture", how="left")
    result["nb_agences"] = result["nb_agences"].fillna(0).astype(int)
    result["nb_points_mobile_money"] = result["nb_points_mobile_money"].fillna(0).astype(int)

    result["agences_pour_100k_hab"] = (
        result["nb_agences"] / result["population_2022"] * 100_000
    ).round(2)
    result["mobile_money_pour_100k_hab"] = (
        result["nb_points_mobile_money"] / result["population_2022"] * 100_000
    ).round(2)

    result = result.sort_values("agences_pour_100k_hab")

    print(f"Nombre total de préfectures : {len(result)}")
    print(f"\nPréfectures SANS AUCUNE agence télécom ({(result['nb_agences'] == 0).sum()}) :")
    print(result.loc[result["nb_agences"] == 0, ["prefecture", "region", "population_2022"]])

    print(f"\nPréfectures SANS AUCUN point mobile money ({(result['nb_points_mobile_money'] == 0).sum()}) :")
    print(result.loc[result["nb_points_mobile_money"] == 0, ["prefecture", "region", "population_2022"]])

    print("\nTop 10 préfectures les moins bien équipées (agences/100k hab) :")
    print(result[["prefecture", "region", "population_2022", "nb_agences", "agences_pour_100k_hab"]].head(10))

    result.to_csv("../data/processed/couverture_par_prefecture.csv", index=False)
    print("\n-> Sauvegardé dans data/processed/couverture_par_prefecture.csv")


if __name__ == "__main__":
    main()