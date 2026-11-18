# Project-2027 - All-in-One Digital Planner

Generator untuk planner digital PDF 2027 dengan navigasi hyperlink (tap untuk pindah halaman),
siap dipakai di GoodNotes, Notability, dan Noteshelf.

## Isi planner (versi lengkap: 468 halaman)

| Bagian | Halaman |
|---|---|
| Cover, Index (semua item bisa diklik), Year overview | 3 |
| Monthly (Jan-Des) dengan link ke minggu dan hari | 12 |
| Weekly (53 minggu) | 53 |
| Daily (365 hari: jadwal per jam, to-do, top 3, water, mood, notes) | 365 |
| Habit tracker per bulan | 12 |
| Mood tracker per bulan | 12 |
| Budget, Expense log, Meal planner, Grocery, Goal, Project, Reading tracker, Brain dump | 8 |
| Notes (lined, dotted, grid) | 3 |

Tab navigasi di bagian atas setiap halaman: INDEX, YEAR, JAN-DEC, NOTES.

## Cara pakai

```bash
pip install -r requirements.txt
python generate_planner.py --year 2027 --start monday --theme sage
```

Hasil ada di folder `dist/`.

Opsi:

- `--year` tahun planner (default 2027)
- `--start` `monday` atau `sunday`
- `--theme` `sage`, `rose`, atau `slate`
- `--no-daily` lewati halaman harian (file lebih kecil, sekitar 100 halaman)
- `--out` path file output

Contoh membuat semua varian:

```bash
for start in monday sunday; do
  for theme in sage rose slate; do
    python generate_planner.py --start $start --theme $theme
  done
done
```

## Catatan

- Desain dan isi dibuat orisinal lewat kode, jadi aman untuk dijual (Shopee, TikTok Shop, Etsy).
- File PDF tidak di-commit (lihat `.gitignore`); jalankan generator atau ambil dari GitHub Actions.
