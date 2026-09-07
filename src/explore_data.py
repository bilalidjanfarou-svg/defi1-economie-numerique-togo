"""
Exploration rapide : colonnes, valeurs uniques des colonnes clés,
répartition géographique (région/préfecture) pour chaque couche.
"""
from load_data import (
    load_mobile_money,
    load_datacenters,
    load_agences_togocom,
    load_agences_moov,
)

def explore(name, df, region_col=None):
    print(f"\n=== {name} ===")
    print("Colonnes :", list(df.columns))
    if region_col and region_col in df.columns:
        print(f"\nRépartition par {region_col} :")
        print(df[region_col].value_counts())

if __name__ == "__main__":
    mm = load_mobile_money()
    explore("mobile_money", mm, region_col="region_nom_bdd")

    dc = load_datacenters()
    explore("datacenters", dc)

    togocom = load_agences_togocom()
    explore("agences_togocom", togocom)

    moov = load_agences_moov()
    explore("agences_moov", moov)