# ----------------------------------------------------------------------
# SRIM 2013 + PySRIM on Python 3.11 (Debian 12 slim)
# ----------------------------------------------------------------------
FROM python:3.11-slim

# Non-interactive apt; quiet Wine; headless display; fixed 32-bit Wine prefix
ENV DEBIAN_FRONTEND=noninteractive \
    WINEDLLOVERRIDES="mscoree,mshtml=" \
    WINEDEBUG="-all" \
    DISPLAY=:1 \
    WINEPREFIX=/opt/wine32 \
    WINEARCH=win32

# 1) Install Wine/Winetricks/Xvfb and helper tools
RUN dpkg --add-architecture i386 \
 && printf "deb http://deb.debian.org/debian bookworm main contrib\n" \
      > /etc/apt/sources.list.d/contrib.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates wget unzip p7zip-full cabextract xauth xvfb \
      wine wine32:i386 winetricks \
 && rm -rf /var/lib/apt/lists/*

# 2) Wrap Wine so every call runs under Xvfb (headless GUI)
RUN mv /usr/bin/wine /usr/bin/wine-bin \
 && printf '#!/bin/sh\nexec xvfb-run -a -s "-screen 0 1024x768x16" /usr/bin/wine-bin "$@"\n' \
      > /usr/local/bin/wine \
 && chmod +x /usr/local/bin/wine

# 3) Initialize a clean 32-bit Wine prefix and install VB6 runtimes/OCX
RUN rm -rf "$WINEPREFIX" \
 && wineboot --init \
 && winetricks -q vb6run comctl32ocx mfc42

# 4) Install SRIM 2013 into /opt/srim (ensure SR Module/SRModule.exe and TRIM.exe exist)
RUN mkdir -p /opt/srim \
 && wget -q -O /tmp/SRIM-2013.e http://www.srim.org/SRIM/SRIM-2013-Std.e \
 && 7z x -y -o/tmp/srim_unpack /tmp/SRIM-2013.e \
 && set -e; \
    if [ -d "/tmp/srim_unpack/SR Module" ] || [ -f "/tmp/srim_unpack/TRIM.exe" ]; then \
        cp -a /tmp/srim_unpack/. /opt/srim/; \
    else \
        inner="$(find /tmp/srim_unpack -mindepth 1 -maxdepth 1 -type d -name 'SRIM*' | head -n1)"; \
        if [ -n "$inner" ]; then \
            cp -a "$inner"/. /opt/srim/; \
        else \
            cp -a /tmp/srim_unpack/. /opt/srim/; \
        fi; \
    fi \
 && rm -rf /tmp/SRIM-2013.e /tmp/srim_unpack \
 && test -f "/opt/srim/SR Module/SRModule.exe" \
 && test -f "/opt/srim/TRIM.exe"

# 5) Python deps: pin versions and patch PySRIM to use yaml.safe_load
RUN pip install --no-cache-dir numpy==2.3.1 pysrim==0.5.10 \
 && python - <<'PY'
import sysconfig, pathlib, re
p = pathlib.Path(sysconfig.get_paths()['purelib']) / 'srim/core/elementdb.py'
p.write_text(re.sub(r'yaml\.load\(', 'yaml.safe_load(', p.read_text(), 1))
print("✓ Patched", p)
PY

# 6) Writable work directory for outputs; default workdir for mounted code
RUN mkdir -p /work
WORKDIR /workspace

CMD ["python"]
