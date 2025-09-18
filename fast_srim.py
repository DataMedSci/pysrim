# --- SRIM runtime bootstrap (items 1,5,6,7,9) --------------------------
import os, glob
from srim import Ion, Layer, SR

# 1) Wymuś ten sam 32-bitowy prefix co w obrazie
os.environ.setdefault("WINEPREFIX", "/opt/wine32")

# 5) Znajdź właściwe BIN: /opt/srim albo zagnieżdżony /opt/srim/SRIM*
BIN = "/opt/srim"
if not os.path.isdir(os.path.join(BIN, "SR Module")):
    for cand in ["/opt/srim/SRIM"] + sorted(glob.glob("/opt/srim/SRIM*")):
        if os.path.isdir(os.path.join(cand, "SR Module")):
            BIN = cand
            break

# 6) Katalog roboczy na wyniki (montowany jako ./outputs)
os.makedirs("/work", exist_ok=True)
try:
    os.chdir("/work")
except Exception:
    pass

# 7) Minimalny log diagnostyczny
print(f"[SRIM] WINEPREFIX={os.environ.get('WINEPREFIX')}  BIN={BIN}  CWD={os.getcwd()}")
print("[SRIM] SRModule:",
      os.path.isfile(os.path.join(BIN, "SR Module", "SRModule.exe")),
      "TRIM:", os.path.isfile(os.path.join(BIN, "TRIM.exe")))

# --- 10 MeV proton through 0.2 cm water --------------------------------
ion   = Ion("H", 10e6)                                      # 10 MeV → eV
layer = Layer({"H": {"stoich": 2}, "O": {"stoich": 1}},
              density=1.0, width=0.2 * 1e8)                 # 0.2 cm → Å
exit_keV = SR(layer, ion).run(BIN).data[-1, 0]              # column 0 = E keV
print(f"Residual energy after 0.2 cm water: {exit_keV/1e3:.2f} MeV")
