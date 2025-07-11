# save as quick_check.py
from srim import Ion, Layer, SR
BIN = "/opt/srim"

# --- 10 MeV proton through 0.2 cm water --------------------------------
ion   = Ion("H", 10e6)                                      # 10 MeV → eV
layer = Layer({"H": {"stoich": 2}, "O": {"stoich": 1}},
              density=1.0, width=0.2 * 1e8)                 # 0.2 cm → Å
exit_keV = SR(layer, ion).run(BIN).data[-1, 0]              # column 0 = E keV
print(f"Residual energy after 0.2 cm water: {exit_keV/1e3:.2f} MeV")
