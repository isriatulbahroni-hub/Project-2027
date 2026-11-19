"""Buat ikon PNG PWA (192, 512, maskable 512, apple-touch 180) dari desain public/icon.svg.
Murni Python standar (tanpa dependensi), supaya jalan di build Vercel. Hasil: public/icons/ (tidak di-commit)."""
import os
import struct
import zlib

OUT = os.path.join("public", "icons")
NAVY, WHITE, RED = (0x1C, 0x24, 0x38), (255, 255, 255), (0xC4, 0x30, 0x2B)
DASHES = [(22, 34, 28, 34), (30, 34, 36, 34), (38, 34, 44, 34), (22, 42, 28, 42), (30, 42, 36, 42)]


def rrect(u, v, x, y, w, h, r):
    if not (x <= u <= x + w and y <= v <= y + h):
        return False
    cx = min(max(u, x + r), x + w - r)
    cy = min(max(v, y + r), y + h - r)
    return (u - cx) ** 2 + (v - cy) ** 2 <= r * r


def capsule(u, v, x0, y0, x1, y1, r):
    t = 0 if x0 == x1 else min(max((u - x0) / (x1 - x0), 0), 1)
    return (u - (x0 + t * (x1 - x0))) ** 2 + (v - y0) ** 2 <= r * r


def pixel(u, v, maskable):
    """Warna (r, g, b, a) di koordinat desain 0..64."""
    if maskable:  # latar penuh, isi diperkecil ke zona aman
        s = 0.7
        u, v = 32 + (u - 32) / s, 32 + (v - 32) / s
        base = NAVY
    else:
        if not rrect(u, v, 0, 0, 64, 64, 14):
            return (0, 0, 0, 0)
        base = NAVY
    if rrect(u, v, 14, 16, 36, 34, 4):
        if v < 25:
            return RED + (255,)
        for d in DASHES:
            if capsule(u, v, *d, 1.5):
                return NAVY + (255,)
        return WHITE + (255,)
    return base + (255,)


def png(size, maskable=False, ss=2):
    rows = []
    for py in range(size):
        row = bytearray([0])
        for px in range(size):
            acc = [0, 0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    r, g, b, a = pixel((px + (sx + .5) / ss) * 64 / size, (py + (sy + .5) / ss) * 64 / size, maskable)
                    acc[0] += r * a; acc[1] += g * a; acc[2] += b * a; acc[3] += a
            if acc[3]:
                row += bytes([round(acc[0] / acc[3]), round(acc[1] / acc[3]), round(acc[2] / acc[3]), round(acc[3] / (ss * ss))])
            else:
                row += bytes(4)
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, size, mask in [("icon-192.png", 192, False), ("icon-512.png", 512, False),
                             ("icon-maskable-512.png", 512, True), ("apple-touch-icon.png", 180, True)]:
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(png(size, mask))
        print("OK", name)
