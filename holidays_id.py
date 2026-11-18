"""Libur nasional dan cuti bersama Indonesia, dipakai generate_planner.py untuk menandai tanggal merah.

Sumber 2027: SKB Menteri Agama, Menteri Ketenagakerjaan, dan Menteri PANRB
No. 1205 Tahun 2026, No. 3 Tahun 2026, No. 2 Tahun 2026 (ditetapkan 15 September 2026):
18 hari libur nasional + 8 hari cuti bersama.

Catatan: SKB menyebut tanggal 1 Ramadan, Idulfitri, dan Iduladha ditetapkan dengan Keputusan
Menteri Agama. Cek ulang tanggal hari besar Islam sebelum rilis kalau ada pengumuman baru.

Kind: "N" = libur nasional, "C" = cuti bersama.

Cara menambah tahun lain: tambah isi SOURCE, buat daftar _RAW_<tahun> dengan format yang sama,
lalu daftarkan di HOLIDAYS. Jalankan `python holidays_id.py` untuk mencetak jumlah per tahun.
"""
import datetime as dt

SOURCE = {
    2027: "SKB 3 Menteri No. 1205, 3 dan 2 Tahun 2026 (15 Sep 2026)",
}

_RAW_2027 = [
    (1, 1, "Tahun Baru 2027 Masehi", "N"),
    (1, 5, "Isra Mikraj Nabi Muhammad SAW", "N"),
    (2, 5, "Tahun Baru Imlek 2578", "C"),
    (2, 6, "Tahun Baru Imlek 2578 Kongzili", "N"),
    (3, 8, "Hari Suci Nyepi (Saka 1949)", "N"),
    (3, 9, "Idulfitri 1448 H", "C"),
    (3, 10, "Idulfitri 1448 H", "N"),
    (3, 11, "Idulfitri 1448 H", "N"),
    (3, 12, "Idulfitri 1448 H", "C"),
    (3, 15, "Idulfitri 1448 H", "C"),
    (3, 25, "Wafat Yesus Kristus", "C"),
    (3, 26, "Wafat Yesus Kristus", "N"),
    (3, 28, "Paskah", "N"),
    (5, 1, "Hari Buruh Internasional", "N"),
    (5, 6, "Kenaikan Yesus Kristus", "N"),
    (5, 17, "Iduladha 1448 H", "N"),
    (5, 18, "Iduladha 1448 H", "C"),
    (5, 19, "Waisak 2571 BE", "C"),
    (5, 20, "Hari Raya Waisak 2571 BE", "N"),
    (6, 1, "Hari Lahir Pancasila", "N"),
    (6, 6, "1 Muharam 1449 H", "N"),
    (8, 15, "Maulid Nabi Muhammad SAW", "N"),
    (8, 17, "Proklamasi Kemerdekaan RI", "N"),
    (12, 24, "Natal", "C"),
    (12, 25, "Natal", "N"),
    (12, 26, "Isra Mikraj Nabi Muhammad SAW", "N"),
]

HOLIDAYS = {
    2027: {dt.date(2027, m, d): (name, kind) for m, d, name, kind in _RAW_2027},
}

if __name__ == "__main__":
    for year, table in HOLIDAYS.items():
        n = sum(1 for _, k in table.values() if k == "N")
        c = sum(1 for _, k in table.values() if k == "C")
        print(f"{year}: {n} libur nasional, {c} cuti bersama, total {len(table)}")
