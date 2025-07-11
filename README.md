# SRIM in Docker — Python 3.11 Edition

A reproducible Docker environment that runs **SRIM 2013** and **PySRIM** on modern
Python 3.11.  
It follows the same idea as Christopher Ostrouchov’s original
[`costrouc/pysrim`](https://github.com/costrouc/pysrim) image, but:

* starts from a **slim Debian 12 / Python 3.11** base instead of Ubuntu 16.04 / Python 3.6;  
* installs the **VB 6 runtime** (`winetricks vb6run`) in a fresh **32-bit** Wine prefix,
  letting SRIM’s Visual-Basic executables run without crashing;  
* wraps Wine with **`xvfb-run`** automatically so SRIM can run head-less;  
* patches PySRIM’s deprecated `yaml.load()` call for compatibility with
  PyYAML ≥ 6.0.

---

## Repository layout

| File              | Purpose                                                                                  |
|-------------------|------------------------------------------------------------------------------------------|
| **Dockerfile**    | Builds the complete SRIM + PySRIM stack (see below).                                     |
| **`my_srim.py`**  | Slow **TRIM** benchmark: 50 MeV range in 4 cm water & 60 MeV exit energy after 1 cm water. |
| **`fast_srim.py`**| Tiny **SR** sanity check: 10 MeV proton residual energy after 0.2 cm water; finishes fast. |

*(Add your own scripts in the same directory—`/workspace` in the container maps
to your current host folder.)*

---

## Building the image

```bash
docker build -t srim_pysrim:latest .
```

### What happens during the build

1. **System packages** – installs Wine 8 (x86 + x64), Winetricks, `cabextract`, `unzip`, `xvfb`, `xauth`, and helper tools on Debian 12 slim.

2. **Head-less Wine wrapper** – replaces `/usr/bin/wine` with a tiny script that runs  
   `xvfb-run -a wine-bin …`, so every Wine/Winetricks call has a dummy X-server.

3. **32-bit Wine prefix + VB6 runtime** – deletes any old prefix, creates a fresh
   `WINEARCH=win32` prefix, and runs `winetricks -q vb6run` to install `MSVBVM60.DLL`
   and the common VB6 OCXs SRIM needs.

4. **SRIM 2013 extraction** – downloads `SRIM-2013-Std.e` from srim.org, unpacks it
   silently with `7z`, and stores everything in `/opt/srim`.

5. **Python layer** – installs NumPy 2.3.1 and PySRIM 0.5.10 on Python 3.11, then
   patches a deprecated `yaml.load()` call to `yaml.safe_load()` for PyYAML ≥ 6.

---

## Running scripts

```bash
# quick SR sanity check (seconds)
docker run --rm -v ${PWD}:/workspace srim_pysrim:latest \
       python /workspace/fast_srim.py

# full TRIM benchmark (minutes)
docker run --rm -v ${PWD}:/workspace srim_pysrim:latest \
       python /workspace/my_srim.py
```

/opt/srim is on the container’s **PATH**; the default working directory inside the container is **/workspace**.


---

## Notes & caveats

* **Layer-width limit** – SRIM’s deterministic SR tables can only handle layers  
  ≤ **21.47 cm** (2 147 483 648 Å). Use multiple thin slabs or TRIM for thicker water
  phantoms.
* **Root warnings** – Wine/Winetricks complain about running as root; inside a
  Docker container this is safe and expected.
* **Performance tips** – For faster TRIM runs, lower `number_ions` in your scripts
  or spin up multiple containers in parallel and merge the outputs.

---

## References

* SRIM home page – <http://www.srim.org>  
* costrouc/pysrim Docker image – <https://github.com/costrouc/pysrim>  
* WineHQ FAQ on running as root – <https://wiki.winehq.org/FAQ>  
* Winetricks documentation – <https://github.com/Winetricks/winetricks>  
* PySRIM documentation – <https://pysrim.readthedocs.io>
