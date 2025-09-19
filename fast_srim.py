# --- SRIM runtime bootstrap (Pathlib) -----------------------------------
import os
from pathlib import Path
from srim import Ion, Layer, SR

# Ensure we use the same 32-bit Wine prefix as in the Docker image
os.environ.setdefault("WINEPREFIX", "/opt/wine32")

# Resolve the SRIM program directory (BIN). It must contain "SR Module/SRModule.exe".
BIN = Path("/opt/srim")
if not (BIN / "SR Module").is_dir():
    # Handle nested layouts like /opt/srim/SRIM-2013-Std
    candidates = [BIN / "SRIM"] + sorted(BIN.glob("SRIM*"))
    for cand in candidates:
        if (cand / "SR Module").is_dir():
            BIN = cand
            break

# Create a writable working folder for outputs (mounted as ./outputs on host)
work = Path("/work")
work.mkdir(parents=True, exist_ok=True)
try:
    os.chdir(work)
except Exception:
    pass

# Minimal diagnostics to make path issues obvious
print(f"[SRIM] WINEPREFIX={os.environ.get('WINEPREFIX')}  BIN={BIN}  CWD={Path.cwd()}")
print(
    "[SRIM] SRModule:", (BIN / "SR Module" / "SRModule.exe").is_file(),
    "TRIM:", (BIN / "TRIM.exe").is_file()
)

# --- SR calculation: 10 MeV proton through 0.2 cm water -----------------
# IMPORTANT: SRModule.exe expects its working directory to be <BIN>/SR Module.
srmod_dir = BIN / "SR Module"
os.chdir(srmod_dir)  # Pathlib has no chdir; use os.chdir(Path) per Python docs. :contentReference[oaicite:1]{index=1}

ion   = Ion("H", 10e6)                           # 10 MeV → eV
layer = Layer({"H": {"stoich": 2}, "O": {"stoich": 1}},
              density=1.0, width=0.2 * 1e8)      # 0.2 cm → Å

# Pass str(BIN) to PySRIM. It writes inputs to "<BIN>/SR Module/..." and launches SRModule.exe. :contentReference[oaicite:2]{index=2}
exit_keV = SR(layer, ion).run(str(BIN)).data[-1, 0]   # column 0 = E [keV]
print(f"Residual energy after 0.2 cm water: {exit_keV/1e3:.2f} MeV")
