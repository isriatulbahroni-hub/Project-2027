#!/bin/sh
# Build Vercel: validasi data tanggal merah, lalu buat 12 PDF (2 awal minggu x 3 tema x Lengkap/Ringkas).
set -e
PY=.venv/bin/python
$PY check_data.py
$PY make_icons.py
mkdir -p public/planners
for s in monday sunday; do
  for t in sage rose slate; do
    $PY generate_planner.py --year 2027 --start $s --theme $t --out public/planners/Planner-2027-$s-$t.pdf
    $PY generate_planner.py --year 2027 --start $s --theme $t --no-daily --out public/planners/Planner-2027-$s-$t-lite.pdf
  done
done
