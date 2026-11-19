"""Uji PDF planner: semua link menuju halaman yang ada, tidak ada link bertumpuk, dan area ketuk cukup besar.
Pakai: python tests/check_pdf.py file.pdf [jumlah_halaman]  (butuh: pip install -r requirements-dev.txt)"""
import ctypes
import sys

import pypdfium2 as pdfium
import pypdfium2.raw as raw

MIN_SIDE = 20.0   # pt: sisi link yang dianggap cukup untuk jari di HP
MIN_SHARE = 0.90  # minimal 90% link harus memenuhi MIN_SIDE; sisanya terjepit di grid terpadat (Index, Year overview, jarak 16-17 pt)


def main(path, want_pages=None):
    pdf = pdfium.PdfDocument(path)
    n = len(pdf)
    if want_pages and n != want_pages:
        sys.exit(f"GAGAL: {n} halaman, seharusnya {want_pages}")
    total = bad = small = overlap = 0
    for i in range(n):
        pg, rects = pdf[i], []
        pos, lk = ctypes.c_int(0), raw.FPDF_LINK()
        while raw.FPDFLink_Enumerate(pg.raw, ctypes.byref(pos), ctypes.byref(lk)):
            total += 1
            d = raw.FPDFLink_GetDest(pdf.raw, lk)
            if not d or raw.FPDFDest_GetDestPageIndex(pdf.raw, d) < 0:
                bad += 1
            r = raw.FS_RECTF()
            if raw.FPDFLink_GetAnnotRect(lk, ctypes.byref(r)):
                rects.append((r.left, r.bottom, r.right, r.top))
        for a in rects:
            if min(a[2] - a[0], a[3] - a[1]) < MIN_SIDE:
                small += 1
        for x in range(len(rects)):
            for y in range(x + 1, len(rects)):
                a, b = rects[x], rects[y]
                if a[0] < b[2] - 0.01 and b[0] < a[2] - 0.01 and a[1] < b[3] - 0.01 and b[1] < a[3] - 0.01:
                    overlap += 1
    share = 1 - small / total if total else 0
    print(f"{n} halaman, {total} link, tak terselesaikan {bad}, bertumpuk {overlap}, "
          f"area ketuk >= {MIN_SIDE:.0f}pt: {share:.1%}")
    if bad or overlap or share < MIN_SHARE:
        sys.exit("GAGAL: lihat angka di atas")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)
