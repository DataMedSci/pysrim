# --- SRIM runtime bootstrap (Pathlib) -----------------------------------
import os
from pathlib import Path
from srim import Ion, Layer, Target, TRIM
from srim.output import Range, Results

# Ensure we use the same 32-bit Wine prefix as in the Docker image
os.environ.setdefault("WINEPREFIX", "/opt/wine32")

# Resolve the SRIM program directory (BIN). It must contain TRIM.exe and "SR Module".
BIN = Path("/opt/srim")
if not (BIN / "SR Module").is_dir():
    # Handle nested layouts like /opt/srim/SRIM-2013-Std
    candidates = [BIN / "SRIM"] + sorted(BIN.glob("SRIM*"))
    for cand in candidates:
        if (cand / "SR Module").is_dir():
            BIN = cand
            break

# Create a writable working folder for outputs (mounted as ./outputs on host)
work = Path("/work"); work.mkdir(parents=True, exist_ok=True)
try:
    os.chdir(work)
except Exception:
    pass
OUT = work / "runs"; OUT.mkdir(parents=True, exist_ok=True)

# Minimal diagnostics to make path issues obvious
print(f"[SRIM] WINEPREFIX={os.environ.get('WINEPREFIX')}  BIN={BIN}  CWD={Path.cwd()}")
print(
    "[SRIM] SRModule:", (BIN / "SR Module" / "SRModule.exe").is_file(),
    "TRIM:", (BIN / "TRIM.exe").is_file()
)

# --- Helper definitions --------------------------------------------------
def water(cm: float) -> Layer:
    """Return a water layer of given thickness (cm). Width is in Å for SRIM."""
    return Layer({"H": {"stoich": 2}, "O": {"stoich": 1}},
                 density=1.0, width=cm * 1e8)

def job(name: str, ion: Ion, target: Target, n: int) -> Path:
    """
    Run a TRIM calculation and copy its outputs to OUT/name.
    TRIM.exe resides directly under BIN, so the working directory must be BIN.
    """
    os.chdir(BIN)  # TRIM.exe expects to run from the SRIM program directory. :contentReference[oaicite:3]{index=3}
    TRIM(target, ion, number_ions=n, calculation=1).run(str(BIN))  # PySRIM expects a string path. :contentReference[oaicite:4]{index=4}
    out_dir = OUT / name
    TRIM.copy_output_files(str(BIN), str(out_dir))
    return out_dir

# --- A) Proton range example --------------------------------------------
rng  = Range(job("50MeV_4cm", Ion("H", 50e6), Target([water(4)]), 20))
mean = (rng.depth * rng.ions).sum() / rng.ions.sum() * 1e-7  # Å → mm
print(f"50 MeV proton range in 4 cm H₂O: {mean:.1f} mm")

# --- B) Exit energy example ---------------------------------------------
res = Results(job("60MeV_1cm", Ion("H", 60e6), Target([water(1)]), 20))
ke  = res.ions["E(keV)"][-1].mean() / 1e3                    # keV → MeV
print(f"Mean exit energy after 1 cm H₂O: {ke:.1f} MeV")
