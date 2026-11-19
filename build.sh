#!/bin/sh
# Build Vercel: validasi data tanggal merah, lalu buat PDF (2 awal minggu x semua tema x Lengkap/Ringkas).
set -e
PY=.venv/bin/python
$PY check_data.py
$PY make_icons.py
mkdir -p public/planners
for s in monday sunday; do
  for t in $($PY generate_planner.py --list-themes); do
    $PY generate_planner.py --year 2027 --start $s --theme $t --out public/planners/Planner-2027-$s-$t.pdf
    $PY generate_planner.py --year 2027 --start $s --theme $t --no-daily --out public/planners/Planner-2027-$s-$t-lite.pdf
  done
done
