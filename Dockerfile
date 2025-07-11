# ---------------------------------------------------------------
# SRIM 2013 + PySRIM on Python 3.11
# ---------------------------------------------------------------
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    WINEDLLOVERRIDES="mscoree,mshtml=" \
    WINEDEBUG="-all" \
    DISPLAY=:1

# --- Wine, Winetricks, helpers ---------------------------------
RUN dpkg --add-architecture i386 \
 && printf "deb http://deb.debian.org/debian bookworm main contrib\n" \
      > /etc/apt/sources.list.d/contrib.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
        wine wine32 wine64 xvfb xauth winetricks cabextract unzip \
        wget p7zip-full \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- wrap wine with xvfb-run (MUST come before winetricks) -----
RUN mv /usr/bin/wine /usr/bin/wine-bin \
 && printf '#!/bin/sh\nexec xvfb-run -a /usr/bin/wine-bin "$@"\n' \
         > /usr/local/bin/wine \
 && chmod +x /usr/local/bin/wine

# --- fresh 32-bit prefix + VB6 runtime -------------------------
RUN rm -rf /root/.wine \
 && WINEARCH=win32 wineboot --init \
 && winetricks -q vb6run        # installs MSVBVM60.DLL & OCXs

# --- download & unpack SRIM 2013 -------------------------------
RUN mkdir -p /opt/srim \
 && wget -q -O /tmp/SRIM-2013.e \
        http://www.srim.org/SRIM/SRIM-2013-Std.e \
 && 7z x -o/opt/srim /tmp/SRIM-2013.e \
 && rm /tmp/SRIM-2013.e

# --- Python stack ----------------------------------------------
RUN pip install --no-cache-dir \
        numpy==2.3.1 pysrim==0.5.10 \
 && python - <<'PY'
import sysconfig, pathlib, re
f = pathlib.Path(sysconfig.get_paths()['purelib']) / 'srim/core/elementdb.py'
f.write_text(re.sub(r'yaml\.load\(', 'yaml.safe_load(', f.read_text(), 1))
print("✓ Patched", f)
PY

WORKDIR /workspace
CMD ["python"]
