"""
Chargement et parsing de base des couches de données du défi.
Extrait lon/lat depuis la colonne `geometry` (format WKT: POINT (lon lat)).
"""
from pathlib import Path
import re
import pandas as pd

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

POINT_RE = re.compile(r"POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)")


def _extract_coords(df: pd.DataFrame) -> pd.DataFrame:
    coords = df["geometry"].str.extract(POINT_RE)
    df["lon"] = coords[0].astype(float)
    df["lat"] = coords[1].astype(float)
    return df


def load_mobile_money() -> pd.DataFrame:
    df = pd.read_csv(DATA_RAW / "agents_mobile_money.csv")
    # Correction d'une faute de frappe a la source : "Tandjoaré" -> "Tandjouaré"
    df["prefecture_nom_bdd"] = df["prefecture_nom_bdd"].replace(
        {"Tandjoaré": "Tandjouaré"}
    )
    return _extract_coords(df)


def load_datacenters() -> pd.DataFrame:
    df = pd.read_csv(DATA_RAW / "datacenters.csv")
    return _extract_coords(df)


def load_agences_togocom() -> pd.DataFrame:
    df = pd.read_csv(DATA_RAW / "agences_togocom.csv")
    df["operateur"] = "Togocom"
    return _extract_coords(df)


def load_agences_moov() -> pd.DataFrame:
    df = pd.read_csv(DATA_RAW / "agences_moov.csv")
    df["operateur"] = "Moov"
    return _extract_coords(df)


if __name__ == "__main__":
    for name, loader in [
        ("mobile_money", load_mobile_money),
        ("datacenters", load_datacenters),
        ("agences_togocom", load_agences_togocom),
        ("agences_moov", load_agences_moov),
    ]:
        d = loader()
        print(f"{name}: {len(d)} lignes, {d['lon'].isna().sum()} coord. manquantes")