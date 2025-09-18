# --- SRIM runtime bootstrap (items 1,5,6,7,9) --------------------------
import os, glob
from pathlib import Path
from srim import Ion, Layer, Target, TRIM
from srim.output import Range, Results

# 1) Stały 32-bit prefix
os.environ.setdefault("WINEPREFIX", "/opt/wine32")

# 5) BIN autodetect
BIN = "/opt/srim"
if not os.path.isdir(os.path.join(BIN, "SR Module")):
    for cand in ["/opt/srim/SRIM"] + sorted(glob.glob("/opt/srim/SRIM*")):
        if os.path.isdir(os.path.join(cand, "SR Module")):
            BIN = cand
            break

# 6) Roboczy katalog na wyniki
os.makedirs("/work", exist_ok=True)
try:
    os.chdir("/work")
except Exception:
    pass
OUT  = Path("/work/runs"); OUT.mkdir(parents=True, exist_ok=True)

# 7) Log diagnostyczny
print(f"[SRIM] WINEPREFIX={os.environ.get('WINEPREFIX')}  BIN={BIN}  CWD={os.getcwd()}")
print("[SRIM] SRModule:",
      os.path.isfile(os.path.join(BIN, "SR Module", "SRModule.exe")),
      "TRIM:", os.path.isfile(os.path.join(BIN, "TRIM.exe")))
# --- Scenariusze obliczeniowe --------------------------------------------

def water(cm):
    return Layer({"H": {"stoich": 2}, "O": {"stoich": 1}},
                 density=1.0, width=cm*1e8)   # cm → Å

def job(name, ion, target, n):
    TRIM(target, ion, number_ions=n, calculation=1).run(BIN)
    TRIM.copy_output_files(BIN, OUT/name); return OUT/name

# A) Range
rng   = Range(job("50MeV_4cm", Ion("H", 50e6), Target([water(4)]), 20))
mean  = (rng.depth*rng.ions).sum()/rng.ions.sum()*1e-7  # Å → mm
print(f"50 MeV proton range in 4 cm H₂O: {mean:.1f} mm")

# B) Exit energy
res   = Results(job("60MeV_1cm", Ion("H", 60e6), Target([water(1)]), 20))
ke    = res.ions["E(keV)"][-1].mean()/1e3               # keV → MeV
print(f"Mean exit energy after 1 cm H₂O: {ke:.1f} MeV")
