#!/usr/bin/env python3
"""All-in-One Digital Planner generator (hyperlinked PDF for GoodNotes / Notability).

Usage:
    python generate_planner.py --year 2027 --start monday --theme sage
    python generate_planner.py --year 2027 --start sunday --theme rose --no-daily
    python generate_planner.py --year 2027 --no-holidays
"""
import argparse
import calendar
import datetime as dt
import os
import sys

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab import rl_config
from reportlab.pdfgen import canvas

from holidays_id import HOLIDAYS, SOURCE
from templates_extra import ExtraPages

rl_config.useA85 = 0  # Flate saja tanpa ASCII85: file ~20% lebih kecil, tetap standar PDF

W, H = 792, 612  # US Letter landscape (same as most planner marketplaces)
M = 28           # outer margin

THEMES = {
    "sage":  dict(bg="#FBFAF7", main="#5F7F6E", soft="#E3EBE5", accent="#E8D9C5", text="#2F3A34", line="#D5D9D4", muted="#9AA59E", hol="#B5483F", holbg="#F5E3DF"),
    "rose":  dict(bg="#FFFBFA", main="#B5707D", soft="#F6E4E7", accent="#EBD7C3", text="#40292E", line="#E6D6D8", muted="#B39CA0", hol="#C62828", holbg="#FBE0DC"),
    "slate": dict(bg="#F9FAFB", main="#4A5D78", soft="#E2E8F0", accent="#F0DFC8", text="#1F2937", line="#D3D9E2", muted="#8E98A8", hol="#C0392B", holbg="#F8E1DE"),
    "lavender": dict(bg="#FBFAFE", main="#7B6BA8", soft="#E9E5F4", accent="#EADFC9", text="#2E2A3F", line="#DAD6E6", muted="#A19BB5", hol="#B5483F", holbg="#F5E3DF"),
    "ocean": dict(bg="#F7FBFC", main="#3F7F95", soft="#DDEEF2", accent="#F1E2C8", text="#1F3540", line="#CFE0E5", muted="#8AA6B0", hol="#C0392B", holbg="#F8E1DE"),
    "peach": dict(bg="#FFFAF6", main="#D98560", soft="#FBE6DA", accent="#E6E3C8", text="#4A3028", line="#EBDCD2", muted="#BFA397", hol="#B3261E", holbg="#F9DDD8"),
    "mocha": dict(bg="#FAF7F3", main="#8B6B52", soft="#EDE3D9", accent="#D9E0CF", text="#3A2E26", line="#DDD2C7", muted="#A8978A", hol="#B3392F", holbg="#F4DFDA"),
    "mint": dict(bg="#F7FCFA", main="#3E9C86", soft="#DDF1EA", accent="#F3E5D0", text="#1F3A33", line="#CFE5DD", muted="#8CB0A5", hol="#C0392B", holbg="#F8E1DE"),
    # Tema gelap untuk iPad/tablet OLED: teks terang di latar gelap, huruf pada tombol memakai warna bg (gelap)
    "midnight": dict(bg="#1B1F2A", main="#9DB4E6", soft="#2A3040", accent="#3A4157", text="#E8ECF5", line="#3A4155", muted="#7F8AA3", hol="#FF8A80", holbg="#43303A"),
}

MONTHS = [calendar.month_name[i] for i in range(1, 13)]
MON_ABBR = [calendar.month_abbr[i].upper() for i in range(1, 13)]
ID_DAY = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
ID_MON = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

# Halaman kesehatan: diberi footer disclaimer otomatis (lihat Planner.x_page)
HEALTH_PAGES = {"tpl_period", "tpl_symptom", "tpl_meds", "tpl_doctor"}


class Planner(ExtraPages):
    def __init__(self, path, year, start, theme, daily, holidays=True):
        self.year, self.daily = year, daily
        self.wk0 = 0 if start == "monday" else 6
        self.t = {k: HexColor(v) for k, v in THEMES[theme].items()}
        self.hol = HOLIDAYS.get(year, {}) if holidays else {}
        self.c = canvas.Canvas(path, pagesize=(W, H))
        self.c.setTitle(f"All-in-One Digital Planner {year}")
        self.c.setAuthor("Project-2027")
        self.c.setSubject("Hyperlinked digital planner")
        # Catat semua tujuan bookmark dan semua link untuk validasi di akhir build
        self._dests, self._links = set(), set()
        _bookmark = self.c.bookmarkPage

        def bookmark(name, *a, **kw):
            self._dests.add(name)
            return _bookmark(name, *a, **kw)

        self.c.bookmarkPage = bookmark
        self.pages = 0
        first = dt.date(year, 1, 1)
        self.first = first - dt.timedelta((first.weekday() - self.wk0) % 7)
        self.n_weeks = (dt.date(year, 12, 31) - self.first).days // 7 + 1
        self.dow = [calendar.day_abbr[(self.wk0 + i) % 7].upper() for i in range(7)]

    # ---------- primitives ----------
    def txt(self, x, y, s, size=9, font="Helvetica", color="text", align="l"):
        c = self.c
        c.setFont(font, size)
        c.setFillColor(self.t[color])
        {"l": c.drawString, "r": c.drawRightString, "c": c.drawCentredString}[align](x, y, s)

    def link(self, x, y, w, h, dest):
        if dest:
            self._links.add(dest)
            self.c.linkRect("", dest, (x, y, x + w, y + h), relative=0, thickness=0)

    def box(self, x, y, w, h, fill=None, stroke="line", r=6, lw=0.7):
        c = self.c
        c.setLineWidth(lw)
        if stroke:
            c.setStrokeColor(self.t[stroke])
        if fill:
            c.setFillColor(self.t[fill])
        c.roundRect(x, y, w, h, r, stroke=1 if stroke else 0, fill=1 if fill else 0)

    def hline(self, x, y, w, color="line", lw=0.5):
        self.c.setStrokeColor(self.t[color])
        self.c.setLineWidth(lw)
        self.c.line(x, y, x + w, y)

    def lines(self, x, y_top, w, n, gap=18):
        for i in range(n):
            self.hline(x, y_top - i * gap, w)

    def checkbox(self, x, y, s=8):
        self.c.setStrokeColor(self.t["muted"])
        self.c.setLineWidth(0.7)
        self.c.roundRect(x, y, s, s, 2, stroke=1, fill=0)

    def circle(self, x, y, r=5):
        self.c.setStrokeColor(self.t["muted"])
        self.c.setLineWidth(0.6)
        self.c.circle(x, y, r, stroke=1, fill=0)

    def dots(self, x, y, w, h, gap=14):
        self.c.setFillColor(self.t["muted"])
        yy = y
        while yy <= y + h:
            xx = x
            while xx <= x + w:
                self.c.circle(xx, yy, 0.6, stroke=0, fill=1)
                xx += gap
            yy += gap

    # ---------- page chrome ----------
    def begin(self, dest, active=None, title=None, sub=None, outline=None, level=0):
        c = self.c
        c.bookmarkPage(dest)
        if outline:
            c.addOutlineEntry(outline, dest, level=level, closed=True)
        c.setFillColor(self.t["bg"])
        c.rect(0, 0, W, H, stroke=0, fill=1)
        self.tabs(active)
        if title:
            self.txt(M, H - 62, title, 22, "Helvetica-Bold", "main")
        if sub:
            self.txt(M, H - 78, sub, 9, "Helvetica", "muted")

    def tabs(self, active):
        items = [("INDEX", "index"), ("YEAR", "year")] + [(MON_ABBR[i], f"m{i+1:02d}") for i in range(12)] + [("NOTES", "notes")]
        w = (W - 2 * M) / len(items)
        for i, (label, dest) in enumerate(items):
            x = M + i * w
            on = dest == active
            self.box(x + 1, H - 30, w - 2, 17, fill="main" if on else "soft", stroke=None, r=5)
            self.txt(x + w / 2, H - 25, label, 6.5, "Helvetica-Bold", "bg" if on else "main", "c")
            self.link(x + 1, H - 30, w - 2, 17, dest)

    def nav(self, items):
        """items: list of (label, dest) right-aligned in header."""
        x = W - M
        for label, dest in reversed(items):
            if not dest:
                continue
            tw = self.c.stringWidth(label, "Helvetica-Bold", 8) + 14
            x -= tw
            self.box(x, H - 74, tw - 4, 16, fill="accent", stroke=None, r=5)
            self.txt(x + (tw - 4) / 2, H - 69, label, 8, "Helvetica-Bold", "text", "c")
            self.link(x, H - 74, tw - 4, 16, dest)

    def end(self):
        self.c.showPage()

    # ---------- date helpers ----------
    def week_no(self, d):
        return (d - self.first).days // 7 + 1

    def day_dest(self, d):
        if d.year != self.year:
            return None
        return f"d{d:%Y%m%d}" if self.daily else f"w{self.week_no(d)}"

    def week_month(self, s):
        mid = s + dt.timedelta(3)
        return 1 if mid.year < self.year else 12 if mid.year > self.year else mid.month

    def hol_name(self, d):
        """Nama libur untuk tanggal d (None kalau bukan tanggal merah)."""
        h = self.hol.get(d)
        if not h:
            return None
        return h[0] if h[1] == "N" else f"Cuti bersama {h[0]}"

    # ---------- pages ----------
    def cover(self):
        c = self.c
        c.bookmarkPage("cover")
        c.setFillColor(self.t["soft"])
        c.rect(0, 0, W, H, stroke=0, fill=1)
        self.box(60, 60, W - 120, H - 120, fill="bg", stroke="main", r=18, lw=1.5)
        self.txt(W / 2, 390, str(self.year), 110, "Helvetica-Bold", "main", "c")
        self.txt(W / 2, 335, "ALL-IN-ONE DIGITAL PLANNER", 26, "Helvetica-Bold", "text", "c")
        label = "Monday start" if self.wk0 == 0 else "Sunday start"
        self.txt(W / 2, 308, f"Hyperlinked  |  {label}  |  GoodNotes  Notability  Noteshelf", 10, "Helvetica", "muted", "c")
        self.hline(W / 2 - 110, 215, 220, "muted", 0.8)
        self.txt(W / 2, 200, "This planner belongs to", 9, "Helvetica", "muted", "c")
        self.box(W / 2 - 70, 120, 140, 30, fill="main", stroke=None, r=15)
        self.txt(W / 2, 130, "OPEN PLANNER", 11, "Helvetica-Bold", "bg", "c")
        self.link(W / 2 - 70, 120, 140, 30, "index")
        c.addOutlineEntry("Cover", "cover", level=0)
        self.end()

    def index(self):
        self.begin("index", "index", "INDEX", f"Tap any item to jump. Planner {self.year}.", "Index")
        top = H - 105
        cols = [M, M + 190, M + 380, M + 570]
        # Plan
        self.txt(cols[0], top, "PLAN", 10, "Helvetica-Bold", "main")
        y = top - 20
        for label, dest in [("Year overview", "year")] + [(MONTHS[i], f"m{i+1:02d}") for i in range(12)]:
            self.txt(cols[0] + 6, y, label, 9)
            self.link(cols[0], y - 4, 170, 14, dest)
            y -= 16
        # Libur nasional (hanya kalau data tanggal merah tersedia)
        if self.hol:
            self.txt(cols[0], top - 250, "HOLIDAYS", 10, "Helvetica-Bold", "main")
            self.txt(cols[0] + 6, top - 270, f"Libur nasional {self.year}", 9)
            self.link(cols[0], top - 274, 170, 14, "holidays")
        # Habit / mood
        self.txt(cols[1], top, "HABIT TRACKER", 10, "Helvetica-Bold", "main")
        for i in range(12):
            x = cols[1] + (i % 2) * 90
            yy = top - 20 - (i // 2) * 16
            self.txt(x + 6, yy, MON_ABBR[i], 9)
            self.link(x, yy - 4, 80, 14, f"habit{i+1:02d}")
        self.txt(cols[1], top - 130, "MOOD TRACKER", 10, "Helvetica-Bold", "main")
        for i in range(12):
            x = cols[1] + (i % 2) * 90
            yy = top - 150 - (i // 2) * 16
            self.txt(x + 6, yy, MON_ABBR[i], 9)
            self.link(x, yy - 4, 80, 14, f"mood{i+1:02d}")
        # Templates
        self.txt(cols[2], top, "LIFE & FINANCE", 10, "Helvetica-Bold", "main")
        tpls = [("Monthly budget", "tpl_budget"), ("Expense log", "tpl_expense"), ("Meal planner", "tpl_meal"),
                ("Grocery list", "tpl_grocery"), ("Goal planner", "tpl_goals"), ("Project planner", "tpl_project"),
                ("Reading tracker", "tpl_books"), ("Brain dump", "tpl_dump")]
        y = top - 20
        for label, dest in tpls:
            self.txt(cols[2] + 6, y, label, 9)
            self.link(cols[2], y - 4, 170, 14, dest)
            y -= 16
        # More templates (hub pages)
        self.txt(cols[1], top - 262, "MORE TEMPLATES", 10, "Helvetica-Bold", "main")
        for k, (label, dest) in enumerate([("Wellness", "hub_well"), ("Productivity", "hub_prod"), ("Lifestyle", "hub_life")]):
            self.txt(cols[1] + 6, top - 282 - k * 16, label, 9)
            self.link(cols[1], top - 286 - k * 16, 170, 14, dest)
        self.txt(cols[2], y - 14, "NOTES", 10, "Helvetica-Bold", "main")
        y -= 34
        for label, dest in [("Lined", "notes"), ("Dotted", "notes_dot"), ("Grid", "notes_grid")]:
            self.txt(cols[2] + 6, y, label, 9)
            self.link(cols[2], y - 4, 170, 14, dest)
            y -= 16
        # Weeks
        self.txt(cols[3], top, "WEEKS", 10, "Helvetica-Bold", "main")
        per = 6
        for n in range(1, self.n_weeks + 1):
            i = n - 1
            x = cols[3] + (i % per) * 28
            yy = top - 28 - (i // per) * 22
            self.box(x, yy, 25, 17, fill="soft", stroke=None, r=4)
            self.txt(x + 12.5, yy + 5, str(n), 7.5, "Helvetica-Bold", "main", "c")
            self.link(x, yy, 25, 17, f"w{n}")
        self.end()

    def year_page(self):
        self.begin("year", "year", f"{self.year}", "Year overview", "Year overview")
        cw, ch = (W - 2 * M - 3 * 14) / 4, 150
        for m in range(1, 13):
            col, row = (m - 1) % 4, (m - 1) // 4
            x = M + col * (cw + 14)
            y = H - 100 - (row + 1) * ch - row * 6
            self.box(x, y, cw, ch, fill="bg")
            self.txt(x + 8, y + ch - 16, MONTHS[m - 1].upper(), 9, "Helvetica-Bold", "main")
            self.link(x, y + ch - 24, cw, 22, f"m{m:02d}")
            dw = (cw - 16) / 7
            for i, d in enumerate(self.dow):
                self.txt(x + 8 + i * dw + dw / 2, y + ch - 32, d[0], 6.5, "Helvetica-Bold", "muted", "c")
            for r, week in enumerate(calendar.Calendar(self.wk0).monthdatescalendar(self.year, m)):
                for i, d in enumerate(week):
                    cx, cy = x + 8 + i * dw, y + ch - 46 - r * 17
                    inm = d.month == m
                    hol = inm and d in self.hol
                    self.txt(cx + dw / 2, cy, str(d.day), 7, "Helvetica-Bold" if hol else "Helvetica",
                             "hol" if hol else ("text" if inm else "line"), "c")
                    if inm:
                        self.link(cx, cy - 4, dw, 14, self.day_dest(d))
        self.end()

    def holidays_page(self):
        items = sorted(self.hol.items())
        n_nat = sum(1 for _, (_, k) in items if k == "N")
        n_cb = len(items) - n_nat
        self.begin("holidays", None, "HOLIDAYS", f"Libur nasional dan cuti bersama {self.year}  |  {n_nat} libur nasional, {n_cb} cuti bersama",
                   "Holidays", 1)
        self.nav([("YEAR", "year"), ("INDEX", "index")])
        half = (len(items) + 1) // 2
        colw = (W - 2 * M - 16) / 2
        top, rh = H - 104, 26
        for ci in range(2):
            x = M + ci * (colw + 16)
            for r, (d, (name, kind)) in enumerate(items[ci * half:(ci + 1) * half]):
                y = top - (r + 1) * rh
                nat = kind == "N"
                self.box(x, y, colw, rh - 3, fill="holbg" if nat else "bg", stroke="line", r=5)
                self.txt(x + 8, y + 9, f"{ID_DAY[d.weekday()]}, {d.day} {ID_MON[d.month - 1]}", 8.5, "Helvetica-Bold", "hol")
                self.txt(x + 80, y + 9, name, 8.5)
                self.txt(x + colw - 8, y + 9, "LIBUR" if nat else "CUTI BERSAMA", 6.5, "Helvetica-Bold", "muted", "r")
                self.link(x, y, colw, rh - 3, self.day_dest(d))
        y0 = top - half * rh - 14
        self.txt(M, y0, f"Sumber: {SOURCE.get(self.year, 'SKB 3 Menteri')}. Tanggal hari besar Islam mengikuti penetapan Menteri Agama.",
                 7, "Helvetica", "muted")
        self.txt(M, y0 - 26, "CATATAN", 9, "Helvetica-Bold", "main")
        self.lines(M, y0 - 44, W - 2 * M, max(int((y0 - 44 - 40) // 20) + 1, 0), 20)
        self.end()

    def month_page(self, m):
        weeks = calendar.Calendar(self.wk0).monthdatescalendar(self.year, m)
        self.begin(f"m{m:02d}", f"m{m:02d}", MONTHS[m - 1].upper(), str(self.year), MONTHS[m - 1], 1)
        self.nav([("YEAR", "year"), ("< PREV", f"m{m-1:02d}" if m > 1 else None), ("NEXT >", f"m{m+1:02d}" if m < 12 else None)])
        gx, gw = M + 26, 540
        cw = gw / 7
        top = H - 108
        ch = (top - 36) / len(weeks)
        for i, d in enumerate(self.dow):
            self.box(gx + i * cw + 1, top, cw - 2, 15, fill="main", stroke=None, r=4)
            self.txt(gx + i * cw + cw / 2, top + 4, d, 7.5, "Helvetica-Bold", "bg", "c")
        for r, week in enumerate(weeks):
            y = top - (r + 1) * ch
            wn = self.week_no(week[0])
            if 1 <= wn <= self.n_weeks:
                self.box(M, y + 2, 22, ch - 4, fill="soft", stroke=None, r=4)
                self.txt(M + 11, y + ch / 2 - 3, f"W{wn}", 6.5, "Helvetica-Bold", "main", "c")
                self.link(M, y + 2, 22, ch - 4, f"w{wn}")
            for i, d in enumerate(week):
                x = gx + i * cw
                inm = d.month == m
                hol = self.hol.get(d) if inm else None
                fill = ("holbg" if hol[1] == "N" else "bg") if hol else ("bg" if inm else None)
                self.box(x + 1, y + 2, cw - 2, ch - 4, fill=fill, stroke="line" if inm else None, r=4)
                self.txt(x + 6, y + ch - 14, str(d.day), 9, "Helvetica-Bold" if inm else "Helvetica",
                         "hol" if hol else ("text" if inm else "line"))
                if hol:
                    for k, ln in enumerate(simpleSplit(self.hol_name(d), "Helvetica", 5.8, cw - 12)[:3]):
                        self.txt(x + 6, y + ch - 25 - k * 7, ln, 5.8, "Helvetica", "hol")
                if inm:
                    self.link(x + 1, y + 2, cw - 2, ch - 4, self.day_dest(d))
        if self.hol:
            self.txt(M, 20, f"Merah = libur nasional / cuti bersama ({SOURCE.get(self.year, 'SKB 3 Menteri')})", 6.5, "Helvetica", "muted")
        px = gx + gw + 14
        pw = W - M - px
        self.txt(px, top + 4, "GOALS", 9, "Helvetica-Bold", "main")
        self.lines(px, top - 14, pw, 8, 20)
        self.txt(px, top - 190, "NOTES", 9, "Helvetica-Bold", "main")
        self.lines(px, top - 208, pw, 10, 20)
        self.end()

    def week_page(self, n):
        s = self.first + dt.timedelta(7 * (n - 1))
        e = s + dt.timedelta(6)
        rng = f"{s:%b} {s.day} - {e:%b} {e.day}"
        self.begin(f"w{n}", None, f"WEEK {n}", f"{rng}, {e.year}", f"Week {n}" if n in (1, self.n_weeks) else None, 1)
        mm = self.week_month(s)
        self.nav([(MONTHS[mm - 1][:3].upper(), f"m{mm:02d}"), ("< PREV", f"w{n-1}" if n > 1 else None),
                  ("NEXT >", f"w{n+1}" if n < self.n_weeks else None)])
        cols, gap = 4, 10
        bw = (W - 2 * M - (cols - 1) * gap) / cols
        bh = (H - 110 - 40 - gap) / 2
        for i in range(8):
            col, row = i % cols, i // cols
            x = M + col * (bw + gap)
            y = H - 100 - (row + 1) * bh - row * gap
            self.box(x, y, bw, bh, fill="bg")
            if i < 7:
                d = s + dt.timedelta(i)
                hol = self.hol.get(d)
                self.box(x, y + bh - 22, bw, 22, fill="holbg" if hol and hol[1] == "N" else "soft", stroke=None, r=6)
                self.txt(x + 8, y + bh - 15, f"{self.dow[i]}  {d.day}", 9, "Helvetica-Bold", "hol" if hol else "main")
                self.txt(x + bw - 8, y + bh - 15, d.strftime("%b"), 8, "Helvetica", "muted", "r")
                self.link(x, y + bh - 22, bw, 22, self.day_dest(d))
                if hol:
                    self.txt(x + 8, y + bh - 34, self.hol_name(d), 6.5, "Helvetica-Bold", "hol")
                self.lines(x + 8, y + bh - 42, bw - 16, int((bh - 50) // 20), 20)
            else:
                self.box(x, y + bh - 22, bw, 22, fill="accent", stroke=None, r=6)
                self.txt(x + 8, y + bh - 15, "WEEKLY FOCUS", 9, "Helvetica-Bold", "text")
                for k in range(4):
                    self.checkbox(x + 8, y + bh - 50 - k * 20, 8)
                    self.hline(x + 22, y + bh - 52 - k * 20, bw - 30)
                self.txt(x + 8, y + 92, "NOTES", 8, "Helvetica-Bold", "main")
                self.lines(x + 8, y + 76, bw - 16, 4, 18)
        self.end()

    def day_page(self, d):
        n = self.week_no(d)
        self.begin(f"d{d:%Y%m%d}", None, f"{d:%A}".upper(), f"{d:%B} {d.day}, {d.year}")
        prev, nxt = d - dt.timedelta(1), d + dt.timedelta(1)
        self.nav([(MONTHS[d.month - 1][:3].upper(), f"m{d.month:02d}"), (f"WEEK {n}", f"w{n}"),
                  ("< PREV", self.day_dest(prev)), ("NEXT >", self.day_dest(nxt))])
        hn = self.hol_name(d)
        if hn:
            tw = self.c.stringWidth(hn, "Helvetica-Bold", 8) + 16
            self.box(M + 175, H - 68, tw, 16, fill="holbg", stroke=None, r=5)
            self.txt(M + 175 + tw / 2, H - 63, hn, 8, "Helvetica-Bold", "hol", "c")
        top = H - 100
        # schedule
        self.txt(M, top, "SCHEDULE", 9, "Helvetica-Bold", "main")
        for i, hr in enumerate(range(6, 23)):
            y = top - 20 - i * 27.5
            self.txt(M, y - 8, f"{hr:02d}:00", 7.5, "Helvetica", "muted")
            self.hline(M + 34, y - 10, 232)
        # to-do
        x2 = M + 296
        self.txt(x2, top, "TO-DO", 9, "Helvetica-Bold", "main")
        for k in range(14):
            y = top - 22 - k * 24
            self.checkbox(x2, y - 2, 9)
            self.hline(x2 + 16, y - 4, 208)
        # priorities / habits
        x3 = M + 552
        w3 = W - M - x3
        self.txt(x3, top, "TOP 3", 9, "Helvetica-Bold", "main")
        for k in range(3):
            self.txt(x3, top - 22 - k * 20, str(k + 1), 8, "Helvetica-Bold", "muted")
            self.hline(x3 + 12, top - 24 - k * 20, w3 - 12)
        self.txt(x3, top - 100, "WATER", 9, "Helvetica-Bold", "main")
        for k in range(8):
            self.circle(x3 + 7 + k * 24, top - 120, 7)
        self.txt(x3, top - 150, "MOOD", 9, "Helvetica-Bold", "main")
        for k, lab in enumerate(["Great", "Good", "Okay", "Low", "Rough"]):
            self.circle(x3 + 8 + k * 40, top - 172, 7)
            self.txt(x3 + 8 + k * 40, top - 192, lab, 6, "Helvetica", "muted", "c")
        self.txt(x3, top - 220, "NOTES", 9, "Helvetica-Bold", "main")
        self.lines(x3, top - 240, w3, 13, 20)
        self.end()

    def habit_page(self, m):
        days = calendar.monthrange(self.year, m)[1]
        self.begin(f"habit{m:02d}", None, "HABIT TRACKER", f"{MONTHS[m-1]} {self.year}", f"Habit {MON_ABBR[m-1]}", 2)
        self.nav([("INDEX", "index"), (MONTHS[m - 1][:3].upper(), f"m{m:02d}")])
        lw = 140
        cw = (W - 2 * M - lw) / 31
        top = H - 108
        self.txt(M, top + 3, "HABIT", 8, "Helvetica-Bold", "main")
        for dd in range(1, days + 1):
            self.txt(M + lw + (dd - 1) * cw + cw / 2, top + 3, str(dd), 6.5, "Helvetica-Bold", "main", "c")
        rh = (top - 40) / 16
        for r in range(16):
            y = top - (r + 1) * rh
            if r % 2 == 0:
                self.box(M, y, W - 2 * M, rh, fill="soft", stroke=None, r=3)
            self.hline(M + 4, y + 4, lw - 12, "muted")
            for dd in range(days):
                self.circle(M + lw + dd * cw + cw / 2, y + rh / 2, 4.2)
        self.end()

    def mood_page(self, m):
        days = calendar.monthrange(self.year, m)[1]
        self.begin(f"mood{m:02d}", None, "MOOD TRACKER", f"{MONTHS[m-1]} {self.year}", f"Mood {MON_ABBR[m-1]}", 2)
        self.nav([("INDEX", "index"), (MONTHS[m - 1][:3].upper(), f"m{m:02d}")])
        lw = 70
        cw = (W - 2 * M - lw) / 31
        top = H - 108
        for dd in range(1, days + 1):
            self.txt(M + lw + (dd - 1) * cw + cw / 2, top + 3, str(dd), 6.5, "Helvetica-Bold", "main", "c")
        for r, lab in enumerate(["GREAT", "GOOD", "OKAY", "LOW", "ROUGH"]):
            y = top - (r + 1) * 40
            if r % 2 == 0:
                self.box(M, y, W - 2 * M, 40, fill="soft", stroke=None, r=3)
            self.txt(M + 6, y + 15, lab, 8, "Helvetica-Bold", "main")
            for dd in range(days):
                self.circle(M + lw + dd * cw + cw / 2, y + 20, 4.5)
        self.txt(M, top - 235, "HIGHLIGHTS OF THE MONTH", 9, "Helvetica-Bold", "main")
        self.lines(M, top - 255, W - 2 * M, 8, 22)
        self.end()

    # ---------- templates ----------
    def x_page(self, dest, *args, **kw):
        """Halaman template tambahan; halaman kesehatan mendapat footer disclaimer."""
        super().x_page(dest, *args, **kw)
        if dest in HEALTH_PAGES or dest.startswith("wlog"):
            self.txt(M, 16, "For personal tracking only. Not medical advice. Talk to your doctor about any health concern.",
                     6.5, "Helvetica", "muted")

    def tpl_page(self, dest, title, sub=None):
        self.begin(dest, None, title, sub, title, 1)
        self.nav([("INDEX", "index")])

    def table(self, x, y_top, widths, headers, rows, rh=20):
        xx = x
        for w, h in zip(widths, headers):
            self.box(xx, y_top - 16, w - 2, 16, fill="main", stroke=None, r=3)
            self.txt(xx + 5, y_top - 11, h, 7.5, "Helvetica-Bold", "bg")
            xx += w
        for r in range(rows):
            yy = y_top - 16 - (r + 1) * rh
            self.hline(x, yy, sum(widths) - 2)

    def tpl_budget(self):
        self.tpl_page("tpl_budget", "MONTHLY BUDGET", "Income, fixed costs and savings")
        top = H - 105
        self.txt(M, top, "INCOME", 10, "Helvetica-Bold", "main")
        self.table(M, top - 6, [130, 70, 70], ["Source", "Planned", "Actual"], 8, 22)
        self.txt(M, top - 238, "SAVINGS & GOALS", 10, "Helvetica-Bold", "main")
        self.table(M, top - 244, [130, 70, 70], ["Goal", "Target", "Saved"], 6, 22)
        x2 = M + 290
        self.txt(x2, top, "EXPENSES", 10, "Helvetica-Bold", "main")
        self.table(x2, top - 6, [170, 70, 70, 70], ["Category", "Planned", "Actual", "Diff"], 17, 21)
        self.end()

    def tpl_expense(self):
        self.tpl_page("tpl_expense", "EXPENSE LOG", "Track every spend")
        top = H - 100
        self.table(M, top, [80, 270, 150, 110, 126], ["Date", "Description", "Category", "Amount", "Paid with"], 22, 21)
        self.end()

    def tpl_meal(self):
        self.tpl_page("tpl_meal", "MEAL PLANNER", "Plan the week")
        top = H - 100
        self.table(M, top, [80, 115, 115, 115, 115], ["Day", "Breakfast", "Lunch", "Dinner", "Snack"], 7, 56)
        for i in range(7):
            self.txt(M + 6, top - 16 - (i + 1) * 56 + 40, self.dow[i], 8, "Helvetica-Bold", "main")
        x2 = M + 560
        self.txt(x2, top - 8, "GROCERY", 9, "Helvetica-Bold", "main")
        for k in range(18):
            self.checkbox(x2, top - 30 - k * 22, 8)
            self.hline(x2 + 14, top - 32 - k * 22, W - M - x2 - 14)
        self.end()

    def tpl_grocery(self):
        self.tpl_page("tpl_grocery", "GROCERY LIST", "Check items off as you shop")
        top = H - 105
        cw = (W - 2 * M - 20) / 3
        for i, name in enumerate(["PRODUCE", "PROTEIN & DAIRY", "PANTRY & OTHER"]):
            x = M + i * (cw + 10)
            self.box(x, top - 16, cw, 16, fill="main", stroke=None, r=4)
            self.txt(x + 8, top - 11, name, 8, "Helvetica-Bold", "bg")
            for k in range(20):
                self.checkbox(x + 4, top - 38 - k * 23, 8)
                self.hline(x + 18, top - 40 - k * 23, cw - 22)
        self.end()

    def tpl_goals(self):
        self.tpl_page("tpl_goals", "GOAL PLANNER", f"Dream it, plan it, do it - {self.year}")
        top = H - 105
        bw = (W - 2 * M - 20) / 3
        for i in range(3):
            x = M + i * (bw + 10)
            self.box(x, 40, bw, top - 40, fill="bg")
            self.box(x, top - 22, bw, 22, fill="soft", stroke=None, r=6)
            self.txt(x + 8, top - 15, f"GOAL {i+1}", 9, "Helvetica-Bold", "main")
            self.txt(x + 8, top - 40, "I want to...", 7.5, "Helvetica", "muted")
            self.lines(x + 8, top - 56, bw - 16, 2, 18)
            self.txt(x + 8, top - 100, "Why it matters", 7.5, "Helvetica", "muted")
            self.lines(x + 8, top - 116, bw - 16, 2, 18)
            self.txt(x + 8, top - 160, "ACTION STEPS", 8, "Helvetica-Bold", "main")
            for k in range(7):
                self.checkbox(x + 8, top - 186 - k * 22, 8)
                self.hline(x + 22, top - 188 - k * 22, bw - 30)
            self.txt(x + 8, 76, "Deadline", 7.5, "Helvetica", "muted")
            self.hline(x + 50, 74, bw - 58)
        self.end()

    def tpl_project(self):
        self.tpl_page("tpl_project", "PROJECT PLANNER", "Milestones and tasks")
        top = H - 100
        self.txt(M, top - 6, "PROJECT", 8, "Helvetica-Bold", "main")
        self.hline(M + 54, top - 8, 280)
        self.txt(M + 360, top - 6, "DEADLINE", 8, "Helvetica-Bold", "main")
        self.hline(M + 418, top - 8, 140)
        self.txt(M + 580, top - 6, "STATUS", 8, "Helvetica-Bold", "main")
        self.hline(M + 622, top - 8, 114)
        self.table(M, top - 26, [30, 330, 120, 100, 80, 76], ["#", "Task", "Owner", "Due", "Priority", "Done"], 17, 23)
        self.end()

    def tpl_books(self):
        self.tpl_page("tpl_books", "READING TRACKER", f"Books of {self.year}")
        top = H - 100
        self.table(M, top, [30, 230, 160, 80, 80, 156], ["#", "Title", "Author", "Started", "Finished", "Rating"], 20, 22)
        self.end()

    def tpl_dump(self):
        self.tpl_page("tpl_dump", "BRAIN DUMP", "Get it all out of your head")
        self.box(M, 36, W - 2 * M, H - 36 - 100, fill="bg")
        self.dots(M + 8, 44, W - 2 * M - 16, H - 36 - 116, 16)
        self.end()

    def notes_page(self, dest, kind, title):
        self.begin(dest, "notes" if dest == "notes" else None, title, "Notes", title if dest != "notes" else "Notes", 0)
        self.nav([("LINED", "notes"), ("DOTTED", "notes_dot"), ("GRID", "notes_grid")])
        y0, y1 = 40, H - 94
        if kind == "lined":
            for k in range(int((y1 - y0) // 22) + 1):
                self.hline(M, y1 - k * 22, W - 2 * M)
        elif kind == "dotted":
            self.dots(M, y0, W - 2 * M, y1 - y0, 16)
        else:
            self.c.setStrokeColor(self.t["line"])
            self.c.setLineWidth(0.4)
            x = M
            while x <= W - M:
                self.c.line(x, y0, x, y1)
                x += 18
            y = y0
            while y <= y1:
                self.c.line(M, y, W - M, y)
                y += 18
        self.end()

    # ---------- build ----------
    def build(self):
        self.cover()
        self.index()
        self.year_page()
        if self.hol:
            self.holidays_page()
        for m in range(1, 13):
            self.month_page(m)
        for n in range(1, self.n_weeks + 1):
            self.week_page(n)
        if self.daily:
            d = dt.date(self.year, 1, 1)
            while d.year == self.year:
                self.day_page(d)
                d += dt.timedelta(1)
        for m in range(1, 13):
            self.habit_page(m)
        for m in range(1, 13):
            self.mood_page(m)
        self.tpl_budget()
        self.tpl_expense()
        self.tpl_meal()
        self.tpl_grocery()
        self.tpl_goals()
        self.tpl_project()
        self.tpl_books()
        self.tpl_dump()
        self.extra_templates()
        self.notes_page("notes", "lined", "NOTES")
        self.notes_page("notes_dot", "dotted", "NOTES")
        self.notes_page("notes_grid", "grid", "NOTES")
        self.pages = self.c.getPageNumber() - 1
        self.check_links()
        self.c.save()

    def check_links(self):
        """Gagalkan build kalau ada link yang menuju halaman yang tidak ada."""
        missing = sorted(self._links - self._dests)
        if missing:
            print(f"GAGAL: {len(missing)} link menuju halaman yang tidak ada: {', '.join(missing[:20])}", file=sys.stderr)
            sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="Generate a hyperlinked digital planner PDF")
    ap.add_argument("--year", type=int, default=2027)
    ap.add_argument("--start", choices=["monday", "sunday"], default="monday")
    ap.add_argument("--theme", choices=list(THEMES), default="sage")
    ap.add_argument("--list-themes", action="store_true", help="cetak nama semua tema lalu keluar (dipakai build.sh)")
    ap.add_argument("--no-daily", action="store_true", help="skip the 365 daily pages (smaller file)")
    ap.add_argument("--no-holidays", action="store_true", help="jangan tandai libur nasional / cuti bersama Indonesia")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.list_themes:
        print(" ".join(THEMES))
        return
    out = a.out or os.path.join("dist", f"All-in-One-Digital-Planner-{a.year}-{a.start.capitalize()}-{a.theme}.pdf")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    planner = Planner(out, a.year, a.start, a.theme, not a.no_daily, not a.no_holidays)
    planner.build()
    print("OK ->", out, f"({planner.pages} halaman)")


if __name__ == "__main__":
    main()
