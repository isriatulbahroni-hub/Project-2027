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
if err:
    print("DATA LIBUR TIDAK VALID:\n- " + "\n- ".join(err))
    sys.exit(1)
print("Data libur valid:", ", ".join(f"{y} ({len(r)} tanggal)" for y, r in d["libur"].items()))
