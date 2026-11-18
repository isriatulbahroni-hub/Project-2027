"""Libur nasional dan cuti bersama Indonesia untuk generator PDF.

Data TIDAK ditulis di file ini. Sumber tunggalnya public/holidays.json, yang juga dibaca web (core.js).
Untuk menambah tahun: tambah isi "sumber" dan "libur" di JSON itu, lalu jalankan `python check_data.py`.

Kind: "N" = libur nasional, "C" = cuti bersama.
"""
import datetime as dt
import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "holidays.json")

with open(DATA_FILE, encoding="utf-8") as _f:
    _DATA = json.load(_f)

SOURCE = {int(y): s["ringkas"] for y, s in _DATA["sumber"].items()}

HOLIDAYS = {
    int(y): {dt.date.fromisoformat(h["tanggal"]): (h["nama"], h["jenis"]) for h in rows}
    for y, rows in _DATA["libur"].items()
}

if __name__ == "__main__":
    for year, table in HOLIDAYS.items():
        n = sum(1 for _, k in table.values() if k == "N")
        c = sum(1 for _, k in table.values() if k == "C")
        print(f"{year}: {n} libur nasional, {c} cuti bersama, total {len(table)}")
