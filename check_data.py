"""Validasi public/holidays.json. Gagal (exit 1) kalau data tidak konsisten dengan sumbernya."""
import datetime as dt
import json
import sys

d = json.load(open("public/holidays.json", encoding="utf-8"))
err = []
for y, rows in d["libur"].items():
    src = d["sumber"].get(y)
    if not src:
        err.append(f"{y}: tidak ada keterangan sumber")
        continue
    seen = set()
    for h in rows:
        try:
            t = dt.date.fromisoformat(h["tanggal"])
        except ValueError:
            err.append(f"{y}: tanggal tidak valid {h.get('tanggal')}")
            continue
        if str(t.year) != y:
            err.append(f"{y}: {h['tanggal']} bukan di tahun {y}")
        if h.get("jenis") not in ("N", "C"):
            err.append(f"{h['tanggal']}: jenis harus N atau C")
        if not h.get("nama", "").strip():
            err.append(f"{h['tanggal']}: nama kosong")
        key = (h["tanggal"], h.get("nama"))
        if key in seen:
            err.append(f"duplikat {key}")
        seen.add(key)
    n = sum(1 for h in rows if h.get("jenis") == "N")
    c = sum(1 for h in rows if h.get("jenis") == "C")
    j = src.get("jumlah", {})
    if (n, c) != (j.get("nasional"), j.get("cuti_bersama")):
        err.append(f"{y}: isi data {n} nasional + {c} cuti bersama, sumber menyatakan {j}")

# Daftar tema di generator (PDF) dan katalog (web) harus identik, termasuk warnanya
import re
_g = open("generate_planner.py", encoding="utf-8").read()
_k = open("public/katalog.js", encoding="utf-8").read()
gen = {m.group(1): m.group(2) for m in re.finditer(r'^\s+"(\w+)":\s+dict\((.*)\)', _g, re.M)}
gcol = {}
for name, body in gen.items():
    c = dict(re.findall(r'(\w+)="(#[0-9A-Fa-f]{6})"', body))
    gcol[name] = tuple(c.get(k, "").upper() for k in ("main", "soft", "accent", "bg"))
kat = {m.group(1): tuple(x.upper() for x in m.groups()[2:])
       for m in re.finditer(r'\["(\w+)","([^"]+)","(#[0-9A-Fa-f]{6})","(#[0-9A-Fa-f]{6})","(#[0-9A-Fa-f]{6})","(#[0-9A-Fa-f]{6})"\]', _k)}
if set(gcol) != set(kat):
    err.append(f"tema beda: generator {sorted(gcol)} vs katalog {sorted(kat)}")
for name in set(gcol) & set(kat):
    if gcol[name] != kat[name]:
        err.append(f"warna tema {name} beda: generator {gcol[name]} vs katalog {kat[name]}")
if err:
    print("DATA TIDAK VALID:\n- " + "\n- ".join(err))
    sys.exit(1)
print("Tema sinkron:", ", ".join(sorted(gcol)))
print("Data libur valid:", ", ".join(f"{y} ({len(r)} tanggal)" for y, r in d["libur"].items()))
