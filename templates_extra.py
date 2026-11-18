"""Template tambahan (Wellness, Productivity, Lifestyle) untuk generate_planner.py.

Dipakai sebagai mixin: `class Planner(ExtraPages)`. Semua halaman memakai primitif
Planner (txt, box, hline, table, ...) sehingga tema warna ikut otomatis.
"""
import calendar
import math

from reportlab.lib.utils import simpleSplit

W, H, M = 792, 612, 28  # harus sama dengan generate_planner.py
T = H - 100             # batas atas area konten
MONTHS = [calendar.month_name[i] for i in range(1, 13)]
MON_ABBR = [calendar.month_abbr[i].upper() for i in range(1, 13)]

# (dest hub, judul, subjudul, [(judul kartu, deskripsi, target)])
HUBS = [
    ("hub_well", "WELLNESS", "Sleep, cycle, symptoms, medication and doctor visits. Tap a card to open.", [
        ("Daily Log", "Sleep, water and steps in one page per month.", "wlog01"),
        ("Period Tracker", "Twelve-month cycle log with flow and symptom key.", "tpl_period"),
        ("Symptom Log", "Note what you feel, how strong and what triggered it.", "tpl_symptom"),
        ("Medication Log", "Medication list plus a weekly AM / PM intake check.", "tpl_meds"),
        ("Doctor Visit", "Prepare your questions and record the visit.", "tpl_doctor"),
    ]),
    ("hub_prod", "PRODUCTIVITY", "Plan, focus and keep your work organised. Tap a card to open.", [
        ("Quarterly Planner", "Four quarters at a glance with themes and goals.", "tpl_quarter"),
        ("SMART Goal", "Turn a wish into a specific, measurable goal.", "tpl_smart"),
        ("Appointments", "Dates, people, places and follow-ups in one list.", "tpl_appt"),
        ("Meeting Minutes", "Agenda, notes, decisions and action items.", "tpl_meeting"),
        ("Pomodoro", "Plan focus sessions and log distractions.", "tpl_pomo"),
        ("Contacts", "Names, numbers and birthdays of people you need.", "tpl_contacts"),
        ("Password Tracker", "Keep hints and 2FA status, never full passwords.", "tpl_pass"),
        ("Order Tracker", "Orders, payments and shipping for small shops.", "tpl_orders"),
    ]),
    ("hub_life", "LIFESTYLE", "Home, style and the things you want to do. Tap a card to open.", [
        ("Birthdays", "Twelve months of birthdays and special dates.", "tpl_bday"),
        ("Chore Chart", "Weekly chores with who does what and when.", "tpl_chores"),
        ("Cleaning Checklist", "Daily, weekly, monthly and seasonal routines.", "tpl_clean"),
        ("Outfit Planner", "Plan seven looks with weather and occasion.", "tpl_outfit"),
        ("Bucket List", "Forty things to do, with the date you did them.", "tpl_bucket"),
    ]),
]


class ExtraPages:
    # ---------- helpers ----------
    def x_page(self, dest, title, sub, hub, outline=None, extra_nav=()):
        hname = next(h[1] for h in HUBS if h[0] == hub)
        self.begin(dest, None, title, sub, outline or title.title(), 1)
        self.nav(list(extra_nav) + [(hname, hub), ("INDEX", "index")])

    def field(self, x, y, w, label, size=8):
        lw = self.c.stringWidth(label, "Helvetica-Bold", size) + 6
        self.txt(x, y + 2, label, size, "Helvetica-Bold", "main")
        self.hline(x + lw, y, w - lw)

    def section(self, x, y, w, title, fill="soft"):
        self.box(x, y - 18, w, 18, fill=fill, stroke=None, r=5)
        self.txt(x + 8, y - 13, title, 8.5, "Helvetica-Bold", "main" if fill == "soft" else "text")
        return y - 18

    def check_lines(self, x, y, w, n, gap=22, labels=()):
        for k in range(n):
            yy = y - k * gap
            self.checkbox(x, yy, 8)
            if k < len(labels) and labels[k]:
                self.txt(x + 14, yy + 0.5, labels[k], 8.5)
            self.hline(x + 14, yy - 2, w - 14)

    def circles(self, pts, r):
        """Banyak lingkaran dalam satu path (file lebih kecil dari circle() satu per satu)."""
        c = self.c
        c.setStrokeColor(self.t["muted"])
        c.setLineWidth(0.6)
        p = c.beginPath()
        for x, y in pts:
            p.circle(x, y, r)
        c.drawPath(p, stroke=1, fill=0)

    def col_checks(self, x, y_top, widths, col, rows, rh, s=9):
        cx = x + sum(widths[:col]) + (widths[col] - 2) / 2
        for r in range(rows):
            yy = y_top - 16 - (r + 1) * rh
            self.checkbox(cx - s / 2, yy + (rh - s) / 2, s)

    def row_numbers(self, x, y_top, rows, rh):
        for r in range(rows):
            yy = y_top - 16 - (r + 1) * rh
            self.txt(x + 6, yy + rh / 2 - 3, str(r + 1), 8, "Helvetica-Bold", "muted")

    # ---------- hub ----------
    def hub_page(self, hub):
        dest, name, sub, items = hub
        self.begin(dest, None, name, sub, name.title(), 0)
        self.nav([(h[1], h[0]) for h in HUBS if h[0] != dest] + [("INDEX", "index")])
        cols, gap, bh = 4, 12, 130
        bw = (W - 2 * M - (cols - 1) * gap) / cols
        for i, (title, desc, target) in enumerate(items):
            x = M + (i % cols) * (bw + gap)
            y = T - (i // cols + 1) * bh - (i // cols) * gap
            self.box(x, y, bw, bh, fill="bg")
            self.box(x, y + bh - 34, bw, 34, fill="soft", stroke=None, r=6)
            self.c.setFillColor(self.t["main"])
            self.c.circle(x + 20, y + bh - 17, 11, stroke=0, fill=1)
            self.txt(x + 20, y + bh - 21, str(i + 1), 10, "Helvetica-Bold", "bg", "c")
            self.txt(x + 38, y + bh - 21, title, 10.5, "Helvetica-Bold", "main")
            for k, ln in enumerate(simpleSplit(desc, "Helvetica", 9, bw - 20)):
                self.txt(x + 10, y + bh - 54 - k * 12, ln, 9)
            self.box(x + 10, y + 10, 58, 18, fill="accent", stroke=None, r=6)
            self.txt(x + 39, y + 16, "OPEN >", 7.5, "Helvetica-Bold", "text", "c")
            self.link(x, y, bw, bh, target)
        rows = math.ceil(len(items) / cols)
        y_end = T - rows * bh - (rows - 1) * gap - 18
        if dest == "hub_well":
            self.txt(M, y_end - 4, "DAILY LOG - JUMP TO A MONTH", 9, "Helvetica-Bold", "main")
            cw = (W - 2 * M - 11 * 6) / 12
            for m in range(12):
                x = M + m * (cw + 6)
                self.box(x, y_end - 34, cw, 22, fill="accent", stroke=None, r=6)
                self.txt(x + cw / 2, y_end - 27, MON_ABBR[m], 8, "Helvetica-Bold", "text", "c")
                self.link(x, y_end - 34, cw, 22, f"wlog{m + 1:02d}")
            y_end -= 56
        self.txt(M, y_end - 4, "NOTES", 9, "Helvetica-Bold", "main")
        self.lines(M, y_end - 22, W - 2 * M, max(int((y_end - 14 - 44) // 20), 0), 20)
        self.end()

    # ---------- wellness ----------
    def wlog_page(self, m):
        days = calendar.monthrange(self.year, m)[1]
        self.x_page(f"wlog{m:02d}", "WELLNESS LOG", f"{MONTHS[m-1]} {self.year}  |  sleep, water and steps",
                    "hub_well", f"Wellness {MON_ABBR[m-1]}", [(MONTHS[m - 1][:3].upper(), f"m{m:02d}")])
        lw, rh = 70, 14
        cw = (W - 2 * M - lw) / 31
        y = T
        blocks = [("SLEEP (hrs)", ["10", "9", "8", "7", "6", "5", "4"]),
                  ("WATER (cups)", ["8", "7", "6", "5", "4", "3", "2", "1"]),
                  ("STEPS (x1000)", ["14", "12", "10", "8", "6", "4", "2"])]
        for title, labels in blocks:
            self.box(M, y - 16, W - 2 * M, 16, fill="main", stroke=None, r=4)
            self.txt(M + 8, y - 12, title, 7, "Helvetica-Bold", "bg")
            for d in range(days):
                self.txt(M + lw + d * cw + cw / 2, y - 12, str(d + 1), 6.5, "Helvetica-Bold", "bg", "c")
            pts = []
            for r, lab in enumerate(labels):
                yy = y - 16 - (r + 1) * rh
                if r % 2 == 0:
                    self.box(M, yy, W - 2 * M, rh, fill="soft", stroke=None, r=2)
                self.txt(M + lw - 10, yy + 4, lab, 7, "Helvetica-Bold", "main", "r")
                pts += [(M + lw + d * cw + cw / 2, yy + rh / 2) for d in range(days)]
            self.circles(pts, 3.8)
            y -= 16 + len(labels) * rh + 8
        bw = (W - 2 * M - 30) / 4
        for i, lab in enumerate(["AVG SLEEP (hrs)", "AVG WATER (cups)", "AVG STEPS", "MY WIN THIS MONTH"]):
            x = M + i * (bw + 10)
            self.box(x, y - 48, bw, 44, fill="bg")
            self.txt(x + 8, y - 17, lab, 7.5, "Helvetica-Bold", "main")
        self.end()

    def tpl_period(self):
        self.x_page("tpl_period", "PERIOD TRACKER", f"Cycle log {self.year}", "hub_well")
        widths = [40, 110, 110, 90, 90, 110, 186]
        self.table(M, T, widths, ["#", "Start date", "End date", "Cycle (days)", "Period (days)", "Flow", "Notes"], 12, 21)
        self.row_numbers(M, T, 12, 21)
        fx = M + sum(widths[:5]) + 10
        for r in range(12):
            yy = T - 16 - (r + 1) * 21
            for k, lab in enumerate("LMH"):
                self.circle(fx + 12 + k * 30, yy + 10.5, 5.5)
                self.txt(fx + 12 + k * 30, yy + 8.5, lab, 6, "Helvetica-Bold", "muted", "c")
        y0 = T - 16 - 12 * 21 - 14
        cw = (W - 2 * M - 24) / 3
        y1 = self.section(M, y0, cw, "AVERAGES")
        for k, lab in enumerate(["Average cycle (days)", "Average period (days)", "Next period expected"]):
            self.field(M + 4, y1 - 28 - k * 28, cw - 8, lab)
        x2 = M + cw + 12
        y1 = self.section(x2, y0, cw, "SYMPTOM KEY  (write the letter in Notes)")
        for k, lab in enumerate(["C  Cramps", "H  Headache", "B  Bloating", "M  Mood swings", "F  Fatigue", "A  Acne"]):
            self.txt(x2 + 10 + (k // 3) * 112, y1 - 24 - (k % 3) * 18, lab, 8.5)
        self.txt(x2 + 10, y1 - 92, "FLOW:  L = light   M = medium   H = heavy", 8.5, "Helvetica-Bold", "main")
        x3 = M + 2 * (cw + 12)
        y1 = self.section(x3, y0, cw, "NOTES")
        self.lines(x3, y1 - 24, cw, 7, 20)
        self.end()

    def tpl_symptom(self):
        self.x_page("tpl_symptom", "SYMPTOM LOG", "What you feel, how strong, and what may cause it", "hub_well")
        widths = [70, 60, 180, 110, 80, 130, 106]
        self.table(M, T, widths, ["Date", "Time", "Symptom", "Severity (1-5)", "Duration", "Trigger / cause", "Notes"], 20, 21)
        sx = M + sum(widths[:3]) + 18
        for r in range(20):
            yy = T - 16 - (r + 1) * 21
            for k in range(5):
                self.circle(sx + k * 20, yy + 10.5, 5)
        self.txt(M, 52, "Severity:  1 = mild    3 = bothersome    5 = severe, call your doctor", 8.5, "Helvetica", "text")
        self.end()

    def tpl_meds(self):
        self.x_page("tpl_meds", "MEDICATION LOG", "Medication list and weekly intake check", "hub_well")
        self.table(M, T, [190, 90, 120, 150, 186], ["Medication", "Dose", "Frequency", "Purpose", "Prescribed by / notes"], 6, 22)
        y = self.section(M, T - 16 - 6 * 22 - 14, W - 2 * M, "WEEKLY INTAKE CHECK  (tick AM / PM when taken)")
        dw = (W - 2 * M - 190) / 7
        self.box(M, y - 16, 188, 16, fill="main", stroke=None, r=3)
        self.txt(M + 5, y - 11, "Medication", 7.5, "Helvetica-Bold", "bg")
        for i, d in enumerate(self.dow):
            x = M + 190 + i * dw
            self.box(x, y - 16, dw - 2, 16, fill="main", stroke=None, r=3)
            self.txt(x + dw / 2, y - 11, d, 7.5, "Helvetica-Bold", "bg", "c")
        y -= 16
        for r in range(6):
            yy = y - (r + 1) * 26
            self.hline(M, yy, W - 2 * M)
            for i in range(7):
                cx = M + 190 + i * dw + dw / 2
                for k, lab in enumerate(("AM", "PM")):
                    self.circle(cx - 17 + k * 34, yy + 15, 5)
                    self.txt(cx - 17 + k * 34, yy + 3, lab, 6.5, "Helvetica-Bold", "muted", "c")
        yb = y - 6 * 26 - 28
        for k, lab in enumerate(["Pharmacy", "Next refill", "Doctor to call"]):
            self.field(M + k * 250, yb, 236, lab)
        self.txt(M, yb - 28, "NOTES", 8.5, "Helvetica-Bold", "main")
        self.lines(M, yb - 44, W - 2 * M, 3, 20)
        self.end()

    def tpl_doctor(self):
        self.x_page("tpl_doctor", "DOCTOR VISIT", "Prepare before, record during, follow up after", "hub_well")
        lw = 360
        rx = M + 376
        y = self.section(M, T, lw, "APPOINTMENT")
        for k, lab in enumerate(["Doctor / clinic", "Specialty", "Date and time", "Phone / address", "Reason for visit"]):
            self.field(M + 4, y - 22 - k * 24, lw - 8, lab)
        y = self.section(M, T - 148, lw, "QUESTIONS TO ASK")
        self.check_lines(M + 4, y - 20, lw - 8, 6, 22)
        y = self.section(M, T - 312, lw, "SYMPTOMS TO MENTION")
        self.lines(M + 4, y - 20, lw - 8, 6, 22)
        y = self.section(rx, T, lw, "DURING THE VISIT")
        self.lines(rx + 4, y - 20, lw - 8, 8, 22)
        y = self.section(rx, T - 204, lw, "DIAGNOSIS AND INSTRUCTIONS")
        self.lines(rx + 4, y - 20, lw - 8, 3, 22)
        y = self.section(rx, T - 302, lw, "MEDICATION PRESCRIBED")
        self.lines(rx + 4, y - 20, lw - 8, 2, 22)
        for k, lab in enumerate(["Follow-up date", "Tests needed", "Next appointment"]):
            self.field(rx + 4, 116 - k * 26, lw - 8, lab)
        self.end()

    # ---------- productivity ----------
    def tpl_quarter(self):
        self.x_page("tpl_quarter", "QUARTERLY PLANNER", f"Four quarters of {self.year}", "hub_prod")
        gap = 12
        bw, bh = (W - 2 * M - gap) / 2, 230
        for q in range(4):
            x = M + (q % 2) * (bw + gap)
            y = T - (q // 2 + 1) * bh - (q // 2) * gap
            self.box(x, y, bw, bh, fill="bg")
            self.box(x, y + bh - 24, bw, 24, fill="soft", stroke=None, r=6)
            self.txt(x + 10, y + bh - 17, f"Q{q + 1}", 12, "Helvetica-Bold", "main")
            x0 = x + bw - 148
            for k in range(3):
                mm = q * 3 + k + 1
                self.box(x0 + k * 48, y + bh - 21, 44, 16, fill="accent", stroke=None, r=5)
                self.txt(x0 + k * 48 + 22, y + bh - 16, MON_ABBR[mm - 1], 7.5, "Helvetica-Bold", "text", "c")
                self.link(x0 + k * 48, y + bh - 21, 44, 16, f"m{mm:02d}")
            self.field(x + 10, y + bh - 46, bw - 20, "THEME")
            self.txt(x + 10, y + bh - 66, "TOP 3 GOALS", 8, "Helvetica-Bold", "main")
            self.check_lines(x + 10, y + bh - 86, bw - 20, 3, 20)
            self.txt(x + 10, y + bh - 148, "KEY DATES AND MILESTONES", 8, "Helvetica-Bold", "main")
            self.lines(x + 10, y + bh - 166, bw - 20, 2, 18)
            self.txt(x + 10, y + 34, "REVIEW: what worked?", 8, "Helvetica-Bold", "main")
            self.lines(x + 10, y + 16, bw - 20, 1, 18)
        self.end()

    def tpl_smart(self):
        self.x_page("tpl_smart", "SMART GOAL", "Specific, Measurable, Achievable, Relevant, Time-bound", "hub_prod")
        self.field(M, T - 4, W - 2 * M, "MY GOAL", 10)
        rows = [("S", "SPECIFIC", "What exactly do I want to achieve?"),
                ("M", "MEASURABLE", "How will I measure progress?"),
                ("A", "ACHIEVABLE", "Is it realistic with my time and resources?"),
                ("R", "RELEVANT", "Why does this goal matter to me?"),
                ("T", "TIME-BOUND", "What is my deadline and what are the checkpoints?")]
        for i, (letter, name, q) in enumerate(rows):
            yt = T - 24 - i * 72
            self.box(M, yt - 66, W - 2 * M, 66, fill="bg")
            self.c.setFillColor(self.t["main"])
            self.c.circle(M + 36, yt - 33, 20, stroke=0, fill=1)
            self.txt(M + 36, yt - 41, letter, 22, "Helvetica-Bold", "bg", "c")
            self.txt(M + 70, yt - 24, name, 11, "Helvetica-Bold", "main")
            for k, ln in enumerate(simpleSplit(q, "Helvetica", 8.5, 170)):
                self.txt(M + 70, yt - 40 - k * 11, ln, 8.5)
            self.lines(M + 260, yt - 24, W - 2 * M - 276, 3, 18)
        yb = T - 24 - 5 * 72 - 20
        for k, lab in enumerate(["Deadline", "First step", "Review date"]):
            self.field(M + k * 250, yb, 236, lab)
        self.field(M, yb - 28, W - 2 * M, "Reward when done")
        self.end()

    def tpl_appt(self):
        self.x_page("tpl_appt", "APPOINTMENT TRACKER", "Dates, people and follow-ups", "hub_prod")
        widths = [70, 60, 150, 190, 110, 46, 110]
        self.table(M, T, widths, ["Date", "Time", "With whom", "Subject / place", "Contact", "Done", "Notes"], 20, 21)
        self.col_checks(M, T, widths, 5, 20, 21)
        self.end()

    def tpl_meeting(self):
        self.x_page("tpl_meeting", "MEETING MINUTES", "Agenda, decisions and action items", "hub_prod")
        self.field(M, T - 4, 400, "MEETING")
        self.field(M + 416, T - 4, 160, "DATE")
        self.field(M + 592, T - 4, 144, "TIME")
        self.field(M, T - 30, 400, "LOCATION / LINK")
        self.field(M + 416, T - 30, 320, "FACILITATOR")
        self.field(M, T - 56, W - 2 * M, "ATTENDEES")
        lw, rx = 360, M + 376
        y = self.section(M, T - 74, lw, "AGENDA")
        for k in range(5):
            self.txt(M + 4, y - 20 - k * 20 + 2, str(k + 1), 8, "Helvetica-Bold", "muted")
            self.hline(M + 18, y - 20 - k * 20, lw - 18)
        y = self.section(M, T - 214, lw, "DISCUSSION NOTES")
        self.lines(M + 4, y - 20, lw - 8, 11, 20)
        y = self.section(rx, T - 74, lw, "DECISIONS")
        self.lines(rx + 4, y - 20, lw - 8, 4, 20)
        widths = [180, 80, 70, 30]
        ty = T - 196
        self.table(rx, ty, widths, ["Action item", "Owner", "Due", "Done"], 7, 22)
        self.col_checks(rx, ty, widths, 3, 7, 22, 8)
        self.field(rx + 4, 128, lw - 8, "Next meeting")
        self.field(rx + 4, 100, lw - 8, "Prepare for next")
        self.end()

    def tpl_pomo(self):
        self.x_page("tpl_pomo", "POMODORO PLANNER", "25 minutes of focus, 5 minutes of rest", "hub_prod")
        self.field(M, 500, 200, "Date")
        self.field(M + 216, 500, W - 2 * M - 216, "Main goal today")
        w = [26, 230, 150, 64]
        top = 482
        self.table(M, top, w, ["#", "Task", "Sessions (25 min)", "Done"], 10, 28)
        self.row_numbers(M, top, 10, 28)
        for r in range(10):
            yy = top - 16 - (r + 1) * 28
            for k in range(5):
                self.circle(M + 270 + k * 26, yy + 14, 8)
        self.col_checks(M, top, w, 3, 10, 28, 10)
        self.box(M, 150, 470, 28, fill="soft", stroke=None, r=6)
        self.txt(M + 10, 160, "Focus 25 min   |   Short break 5 min   |   Long break 20 min after 4 sessions", 8.5, "Helvetica-Bold", "main")
        self.txt(M, 134, "REFLECTION", 8.5, "Helvetica-Bold", "main")
        self.lines(M, 116, 470, 4, 20)
        rx, rw = M + 486, 250
        y = self.section(rx, 482, rw, "DISTRACTION LOG")
        self.lines(rx, y - 20, rw, 6, 22)
        y = self.section(rx, 322, rw, "SESSIONS TODAY")
        for k in range(12):
            self.circle(rx + 22 + (k % 6) * 40, y - 24 - (k // 6) * 32, 10)
        self.field(rx, 216, rw, "Total focus time")
        self.txt(rx, 190, "Focus rating", 8, "Helvetica-Bold", "main")
        for k in range(5):
            self.circle(rx + 88 + k * 28, 193, 8)
        y = self.section(rx, 166, rw, "WIN OF THE DAY")
        self.lines(rx, y - 20, rw, 4, 22)
        self.end()

    def tpl_contacts(self):
        self.x_page("tpl_contacts", "CONTACT LIST", "People you need to reach", "hub_prod")
        self.table(M, T, [150, 105, 175, 150, 70, 86], ["Name", "Phone", "Email", "Company / relation", "Birthday", "Notes"], 20, 21)
        self.end()

    def tpl_pass(self):
        self.x_page("tpl_pass", "PASSWORD TRACKER", "Accounts, hints and two-factor status", "hub_prod")
        self.box(M, T - 26, W - 2 * M, 22, fill="accent", stroke=None, r=6)
        self.txt(M + 10, T - 19, "TIP: write a hint, never the full password. Use a password manager and lock this file.",
                 8.5, "Helvetica-Bold", "text")
        widths = [170, 190, 170, 80, 36, 90]
        top = T - 34
        self.table(M, top, widths, ["Website / app", "Username / email", "Password hint", "Updated", "2FA", "Notes"], 18, 21)
        self.col_checks(M, top, widths, 4, 18, 21)
        self.end()

    def tpl_orders(self):
        self.x_page("tpl_orders", "ORDER TRACKER", "Orders, payments and shipping", "hub_prod")
        bw = (W - 2 * M - 30) / 4
        for i, lab in enumerate(["ORDERS", "REVENUE", "PENDING", "SHIPPED"]):
            x = M + i * (bw + 10)
            self.box(x, T - 44, bw, 40, fill="bg")
            self.txt(x + 8, T - 17, lab, 7.5, "Helvetica-Bold", "main")
        widths = [64, 62, 120, 150, 36, 80, 36, 46, 142]
        top = T - 54
        self.table(M, top, widths, ["Order #", "Date", "Customer", "Item / product", "Qty", "Total", "Paid", "Sent", "Tracking / notes"], 18, 21)
        self.col_checks(M, top, widths, 6, 18, 21)
        self.col_checks(M, top, widths, 7, 18, 21)
        self.end()

    # ---------- lifestyle ----------
    def tpl_bday(self):
        self.x_page("tpl_bday", "BIRTHDAY TRACKER", "Never miss a special date", "hub_life")
        gap = 10
        bw, bh = (W - 2 * M - 2 * gap) / 3, 112
        for m in range(12):
            x = M + (m % 3) * (bw + gap)
            y = T - (m // 3 + 1) * bh - (m // 3) * 8
            self.box(x, y, bw, bh, fill="bg")
            self.box(x, y + bh - 18, bw, 18, fill="soft", stroke=None, r=5)
            self.txt(x + 8, y + bh - 13, MONTHS[m].upper(), 8.5, "Helvetica-Bold", "main")
            self.link(x, y + bh - 18, bw, 18, f"m{m + 1:02d}")
            for k in range(5):
                yy = y + bh - 34 - k * 16
                self.hline(x + 8, yy, 26)
                self.hline(x + 42, yy, bw - 50)
        self.end()

    def tpl_chores(self):
        self.x_page("tpl_chores", "CHORE CHART", "Who does what, and when", "hub_life")
        widths = [205, 90] + [63] * 7
        self.table(M, T, widths, ["Chore", "Who"] + self.dow, 16, 24)
        for col in range(2, 9):
            self.col_checks(M, T, widths, col, 16, 24, 10)
        self.field(M, 84, 360, "Weekly reward")
        self.field(M + 376, 84, 360, "Notes")
        self.end()

    def tpl_clean(self):
        self.x_page("tpl_clean", "CLEANING CHECKLIST", "Daily, weekly, monthly and seasonal routines", "hub_life")
        lists = [
            ("DAILY", ["Make the bed", "Wash the dishes", "Wipe kitchen counters", "Sweep high-traffic floors",
                       "Take out the trash", "Tidy living areas", "Quick bathroom wipe-down", "Put away laundry"]),
            ("WEEKLY", ["Vacuum all floors", "Mop hard floors", "Clean bathrooms", "Change bed linen", "Dust surfaces",
                        "Wash towels", "Clean mirrors and glass", "Clean out the fridge", "Clean the kitchen sink"]),
            ("MONTHLY", ["Wipe inside the microwave", "Clean oven and stovetop", "Vacuum upholstery", "Wash windows",
                         "Clean the washing machine", "Wipe baseboards", "Declutter one drawer", "Check expiry dates",
                         "Clean light fixtures"]),
            ("SEASONAL", ["Deep clean the fridge", "Wash curtains", "Rotate your wardrobe", "Rotate the mattress",
                          "Clean AC filters", "Declutter storage", "Wash pillows and duvets", "Clean behind appliances",
                          "Clean balcony or gutters"]),
        ]
        gap = 12
        bw, bh = (W - 2 * M - gap) / 2, 230
        for i, (name, items) in enumerate(lists):
            x = M + (i % 2) * (bw + gap)
            y = T - (i // 2 + 1) * bh - (i // 2) * gap
            self.box(x, y, bw, bh, fill="bg")
            self.box(x, y + bh - 24, bw, 24, fill="soft", stroke=None, r=6)
            self.txt(x + 10, y + bh - 17, name, 10, "Helvetica-Bold", "main")
            self.check_lines(x + 10, y + bh - 42, bw - 20, 10, 19, items)
        self.end()

    def tpl_outfit(self):
        self.x_page("tpl_outfit", "OUTFIT PLANNER", "Seven looks for the week", "hub_life")
        gap = 8
        bw, bh = (W - 2 * M - 6 * gap) / 7, 340
        for i in range(7):
            x = M + i * (bw + gap)
            y = T - bh
            self.box(x, y, bw, bh, fill="bg")
            self.box(x, y + bh - 22, bw, 22, fill="soft", stroke=None, r=6)
            self.txt(x + 8, y + bh - 15, self.dow[i], 9, "Helvetica-Bold", "main")
            self.hline(x + 40, y + bh - 17, bw - 48)
            cy = y + bh - 30
            for lab in ["TOP", "BOTTOM", "SHOES", "EXTRAS"]:
                self.txt(x + 6, cy - 8, lab, 7.5, "Helvetica-Bold", "main")
                self.box(x + 6, cy - 52, bw - 12, 40, fill=None, stroke="line", r=4)
                cy -= 58
            self.txt(x + 6, y + 66, "OCCASION", 7.5, "Helvetica-Bold", "main")
            self.hline(x + 6, y + 54, bw - 12)
            for k, lab in enumerate(["SUN", "CLOUD", "RAIN"]):
                cx = x + 16 + k * 33
                self.circle(cx, y + 30, 6)
                self.txt(cx, y + 14, lab, 6.5, "Helvetica-Bold", "muted", "c")
        yb = T - bh - 22
        self.txt(M, yb, "SHOPPING LIST", 8.5, "Helvetica-Bold", "main")
        self.check_lines(M, yb - 22, 360, 4, 20)
        self.txt(M + 376, yb, "NOTES", 8.5, "Helvetica-Bold", "main")
        self.lines(M + 376, yb - 20, 360, 4, 20)
        self.end()

    def tpl_bucket(self):
        self.x_page("tpl_bucket", "BUCKET LIST", "Forty things to do, and the day you did them", "hub_life")
        cw = 360
        for col in range(2):
            x = M + col * (cw + 16)
            self.box(x, T - 18, cw, 18, fill="soft", stroke=None, r=5)
            self.txt(x + 8, T - 13, "I WANT TO...", 8.5, "Helvetica-Bold", "main")
            self.txt(x + cw - 8, T - 13, "DONE ON", 8.5, "Helvetica-Bold", "main", "r")
            for k in range(20):
                yy = T - 18 - (k + 1) * 22
                self.txt(x + 2, yy + 5, str(col * 20 + k + 1), 7.5, "Helvetica-Bold", "muted")
                self.checkbox(x + 22, yy + 4, 9)
                self.hline(x + 38, yy, cw - 108)
                self.hline(x + cw - 62, yy, 62)
        self.end()

    # ---------- urutan halaman ----------
    def extra_templates(self):
        for hub in HUBS:
            self.hub_page(hub)
            if hub[0] == "hub_well":
                for m in range(1, 13):
                    self.wlog_page(m)
            for _, _, target in hub[3]:
                if target.startswith("tpl_"):
                    getattr(self, target)()
