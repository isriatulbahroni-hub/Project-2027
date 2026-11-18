# Project-2027 - All-in-One Digital Planner

Generator untuk planner digital PDF 2027 dengan navigasi hyperlink (tap untuk pindah halaman),
siap dipakai di GoodNotes, Notability, dan Noteshelf. Tanggal merah (libur nasional dan cuti bersama)
Indonesia 2027 sudah ditandai di kalender, mingguan, dan harian.

## Web: Planner OS

Versi web sudah berjalan (folder `public/`): satu dashboard utama dan modul terpisah untuk Planner, Goals, Wellness,
Journal, Productivity, Finance, Calendar, Katalog, dan Downloads. Data pribadi tersimpan di perangkat (lihat `PRIVACY.md`)
dan bisa diekspor atau dipulihkan sebagai JSON. Bisa dipasang sebagai aplikasi (PWA).

Belum ada: akun dan login, sinkron antar perangkat, panel admin (disembunyikan sampai login ada), dan aplikasi APK.
Rencananya satu backend bersama untuk akun, lisensi, dan data, dengan hak akses premium divalidasi di server.
Generator Python tetap menjadi mesin pembuat PDF. Rencana ini belum final.

## Isi planner (versi lengkap: 501 halaman)

| Bagian | Halaman |
|---|---|
| Cover, Index (semua item bisa diklik), Year overview | 3 |
| Holidays (daftar 18 libur nasional + 8 cuti bersama, bisa diklik ke harinya) | 1 |
| Monthly (Jan-Des) dengan link ke minggu dan hari | 12 |
| Weekly (53 minggu) | 53 |
| Daily (365 hari: jadwal per jam, to-do, top 3, water, mood, notes) | 365 |
| Habit tracker per bulan | 12 |
| Mood tracker per bulan | 12 |
| Budget, Expense log, Meal planner, Grocery, Goal, Project, Reading tracker, Brain dump | 8 |
| Wellness: hub, Daily log 12 bulan, Period tracker, Symptom log, Medication log, Doctor visit | 17 |
| Productivity: hub, Quarterly, SMART goal, Appointments, Meeting minutes, Pomodoro, Contacts, Password tracker, Order tracker | 9 |
| Lifestyle: hub, Birthdays, Chore chart, Cleaning checklist, Outfit planner, Bucket list | 6 |
| Notes (lined, dotted, grid) | 3 |

Tab navigasi di bagian atas setiap halaman: INDEX, YEAR, JAN-DEC, NOTES.

Tanpa halaman harian (`--no-daily`): 136 halaman. Tanpa tanggal merah (`--no-holidays`): kurang 1 halaman Holidays.

## Cara pakai

```bash
pip install -r requirements.txt
python generate_planner.py --year 2027 --start monday --theme sage
```

Hasil ada di folder `dist/`. Setelah selesai, generator mencetak jumlah halaman.

Opsi:

- `--year` tahun planner (default 2027)
- `--start` `monday` atau `sunday`
- `--theme` `sage`, `rose`, atau `slate`
- `--no-daily` lewati halaman harian (file lebih kecil, sekitar 136 halaman)
- `--no-holidays` jangan tandai tanggal merah Indonesia
- `--out` path file output

Contoh membuat semua varian:

```bash
for start in monday sunday; do
  for theme in sage rose slate; do
    python generate_planner.py --start $start --theme $theme
  done
done
```

## Tanggal merah

Semua tanggal merah dibaca dari satu file data: `public/holidays.json`. Generator PDF (lewat `holidays_id.py`) dan web
(`core.js`) memakai file yang sama, jadi tidak ada tanggal yang ditulis ulang di kode. Isi 2027 mengikuti SKB Menteri Agama,
Menteri Ketenagakerjaan, dan Menteri PANRB No. 1205, 3, dan 2 Tahun 2026 (ditetapkan 15 September 2026): 18 hari libur
nasional dan 8 cuti bersama. Kalender (hari dalam seminggu, panjang bulan, tahun kabisat) dihitung dari fungsi tanggal, bukan ditulis manual.

Menambah atau memperbarui tahun: ubah `public/holidays.json` (isi `sumber` lengkap dengan jumlah resmi, dan daftar `libur`),
lalu jalankan `python check_data.py`. Validator memeriksa format tanggal, tahun, jenis, duplikat, dan kecocokan jumlah dengan sumber.
Kalau Kemenag menetapkan tanggal hari besar Islam yang berbeda dari SKB, perbarui file itu lalu build ulang.

Tahun yang belum ada di file data tetap bisa dibuat, hanya tanpa tanda libur.

## Cek otomatis

Saat build, `check_data.py` memeriksa data libur dan generator memeriksa semua link. Kalau ada link yang menuju halaman yang tidak ada, build gagal
dan nama tujuan yang bermasalah dicetak, jadi tidak ada link mati yang ikut terjual.

## Deploy (Vercel)

`vercel.json` membuat 6 PDF (2 awal minggu x 3 tema) ke `public/planners/` saat build, dan `public/index.html`
menampilkan pratinjau serta tombol unduh. Versi reportlab dikunci di `requirements.txt` supaya hasil build konsisten.

## Catatan

- Desain dan isi dibuat orisinal lewat kode, jadi aman untuk dijual (Shopee, TikTok Shop, Etsy).
- Ketentuan pemakaian untuk pembeli ada di `TERMS.md`, dan kebijakan privasi web di `PRIVACY.md` (keduanya draft, sesuaikan sebelum dipakai).
- Halaman kesehatan (Period, Symptom, Medication, Doctor Visit, Wellness log) diberi footer "bukan nasihat medis" secara otomatis.
- File PDF tidak di-commit (lihat `.gitignore`); jalankan generator atau ambil hasil build dari Vercel.
