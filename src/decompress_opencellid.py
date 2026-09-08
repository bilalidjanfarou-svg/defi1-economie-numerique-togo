import gzip
import shutil
from pathlib import Path

src = Path(__file__).resolve().parent.parent / "data" / "raw" / "opencellid_togo.csv.gz"
dst = Path(__file__).resolve().parent.parent / "data" / "raw" / "opencellid_togo.csv"

try:
    with gzip.open(src, "rb") as f_in, open(dst, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"OK -> {dst}")
    print(f"Taille : {dst.stat().st_size} octets")
    with open(dst, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            print(line.strip())
            if i >= 10:
                break
except Exception as e:
    print(f"ERREUR: {type(e).__name__}: {e}")