"""
Two SRIM/TRIM benchmarks:
A) 50 MeV proton projected range in 4 cm water
B) 60 MeV proton exit energy after 1 cm water (10 000 ions)
"""
from pathlib import Path
import numpy as np
from srim import Ion, Layer, Target, TRIM
from srim.output import Range, Results

BIN  = "/opt/srim"          # inside the container
OUT  = Path("/workspace/runs"); OUT.mkdir(exist_ok=True)

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
