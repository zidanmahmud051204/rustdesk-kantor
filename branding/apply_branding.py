#!/usr/bin/env python3
"""Terapkan branding kantor ke kode sumber RustDesk 1.5.3.

Dijalankan dari folder kode sumber RustDesk (cwd), contoh:
    python3 /path/ke/branding/apply_branding.py

Yang diubah (hanya tampilan, alur aplikasi tidak berubah):
  * ikon aplikasi (.exe, taskbar, tray)  -> logo kantor
  * logo di halaman utama + ikon kecil   -> logo kantor
  * teks "Dikustomisasi oleh Zidan Developer" di halaman utama dan halaman About

Skrip berhenti dengan error jika kode sumber tidak sesuai harapan, supaya tidak
menghasilkan build yang diam-diam tidak ter-branding.
"""
import re
import shutil
import sys
from pathlib import Path

CREDIT = "Dikustomisasi oleh Zidan Developer"

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd()


def fail(msg):
    print(f"[GAGAL] {msg}", file=sys.stderr)
    sys.exit(1)


def copy_asset(src_name, dest_rel, must_exist):
    src = HERE / src_name
    dest = ROOT / dest_rel
    if not src.is_file():
        fail(f"File branding tidak ditemukan: {src}")
    if must_exist and not dest.is_file():
        fail(f"Struktur kode berubah, file tujuan tidak ada: {dest_rel}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    print(f"[OK] {src_name} -> {dest_rel}")


def edit(rel, old, new, marker):
    path = ROOT / rel
    if not path.is_file():
        fail(f"File tidak ditemukan: {rel}")
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"[SKIP] {rel} sudah ter-branding")
        return
    count = text.count(old)
    if count != 1:
        fail(f"{rel}: bagian kode yang dicari ditemukan {count}x (seharusnya 1x). "
             "Versi RustDesk mungkin berubah.")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"[OK] teks ditambahkan di {rel}")


# 1) Ikon dan logo
copy_asset("icon.ico", "res/icon.ico", True)
copy_asset("icon.ico", "res/tray-icon.ico", True)
copy_asset("icon.ico", "flutter/windows/runner/resources/app_icon.ico", True)
copy_asset("icon.png", "flutter/assets/icon.png", False)
copy_asset("logo.png", "flutter/assets/logo.png", False)

# 2) Teks di halaman utama (di bawah logo)
edit(
    "flutter/lib/desktop/pages/desktop_home_page.dart",
    """      Align(
        alignment: Alignment.center,
        child: loadLogo(),
      ),
""",
    """      Align(
        alignment: Alignment.center,
        child: loadLogo(),
      ),
      Align(
        alignment: Alignment.center,
        child: Text(
          '%s',
          textAlign: TextAlign.center,
          style: TextStyle(
              fontSize: 11,
              color: Theme.of(context).textTheme.bodySmall?.color),
        ).marginOnly(left: 8, right: 8, top: 2, bottom: 4),
      ),
      Container(
        height: 1.5,
        margin: EdgeInsets.symmetric(horizontal: 24, vertical: 6),
        decoration: BoxDecoration(
            gradient: LinearGradient(colors: [
          Colors.transparent,
          Color(0xFFE2B66B),
          Colors.transparent
        ])),
      ),
""" % CREDIT,
    CREDIT,
)

# 3) Teks di halaman About (atribusi RustDesk/AGPL tetap dipertahankan)
edit(
    "flutter/lib/desktop/pages/desktop_setting_page.dart",
    """              Container(
                decoration: const BoxDecoration(color: Color(0xFF2c8cff)),
""",
    """              SelectionArea(
                  child: Text(
                '%s\\nBerbasis RustDesk (AGPL-3.0)',
              ).marginSymmetric(vertical: 4.0)),
              Container(
                decoration: const BoxDecoration(color: Color(0xFF2c8cff)),
""" % CREDIT,
    "Berbasis RustDesk (AGPL-3.0)",
)

# 4) Tema elegan: ivory-emas (terang) dan biru malam-emas champagne (gelap, default)
#    Palet diambil dari logo: emas #FCC682 dan biru langit #83E8FA.
LIB = ROOT / "flutter" / "lib"


def swap_hex(old, new, expected):
    """Ganti kode warna di semua file Dart agar konsisten di seluruh tampilan."""
    pat = re.compile(re.escape(old), re.I)
    total, pending = 0, []
    for p in sorted(LIB.rglob("*.dart")):
        text = p.read_text(encoding="utf-8")
        n = len(pat.findall(text))
        if n:
            total += n
            pending.append((p, pat.sub(new, text)))
    if total == 0:
        if any(re.search(re.escape(new), p.read_text(encoding="utf-8"), re.I)
               for p in LIB.rglob("*.dart")):
            print(f"[SKIP] warna {old} sudah diganti")
            return
        fail(f"warna {old} tidak ditemukan. Versi RustDesk mungkin berubah.")
    if total != expected:
        fail(f"warna {old} ditemukan {total}x (seharusnya {expected}x).")
    for p, text in pending:
        p.write_text(text, encoding="utf-8")
    print(f"[OK] warna {old} -> {new} ({total}x)")


swap_hex("0071FF", "9A6B1F", 4)   # aksen utama (biru -> emas antik)
swap_hex("2C8CFF", "9A6B1F", 3)   # tombol dan panel About
swap_hex("00B6F0", "1E9CC0", 1)   # warna angka ID (aqua dari logo)
swap_hex("EFEFF2", "F4F0E8", 1)   # latar kartu mode terang (ivory)
swap_hex("18191E", "0F1218", 2)   # latar mode gelap (biru malam)
swap_hex("24252B", "1A1F29", 5)   # permukaan kartu/input mode gelap

COMMON = "flutter/lib/common.dart"

edit(COMMON,
     "    scaffoldBackgroundColor: Colors.white,\n    dialogBackgroundColor: Colors.white,\n",
     "    scaffoldBackgroundColor: Color(0xFFFBF8F2),\n    dialogBackgroundColor: Color(0xFFFBF8F2),\n",
     "Color(0xFFFBF8F2)")
edit(COMMON,
     "    hoverColor: Color.fromARGB(255, 224, 224, 224),",
     "    hoverColor: Color.fromARGB(255, 236, 229, 214),",
     "Color.fromARGB(255, 236, 229, 214)")
edit(COMMON,
     "    colorScheme: ColorScheme.light(\n        primary: Colors.blue, secondary: accent, background: grayBg),",
     "    colorScheme: ColorScheme.light(\n        primary: accent, secondary: accent, background: grayBg),",
     "primary: accent, secondary: accent")
edit(COMMON,
     "    hoverColor: Color.fromARGB(255, 45, 46, 53),",
     "    hoverColor: Color.fromARGB(255, 33, 38, 49),",
     "Color.fromARGB(255, 33, 38, 49)")
edit(COMMON,
     "        fontWeight: FontWeight.bold,\n        color: accent80,",
     "        fontWeight: FontWeight.bold,\n        color: Color(0xFFE2B66B),",
     "color: Color(0xFFE2B66B),")
edit(COMMON,
     "    colorScheme: ColorScheme.dark(\n      primary: Colors.blue,",
     "    colorScheme: ColorScheme.dark(\n      primary: Color(0xFFE2B66B),",
     "primary: Color(0xFFE2B66B)")
edit(COMMON,
     "MaterialStatePropertyAll(Color(0xFF121212))",
     "MaterialStatePropertyAll(Color(0xFF0B0E13))",
     "Color(0xFF0B0E13)")

# Default tampilan = gelap. Pilihan Terang / Gelap / Ikuti Sistem di Settings tetap berfungsi.
edit(COMMON,
     "get defaultOptionTheme => isCustomClient ? 'system' : '';",
     "get defaultOptionTheme => 'system';",
     "get defaultOptionTheme => 'system';")
edit(COMMON,
     '      case "dark":\n        return ThemeMode.dark;\n      default:\n        return ThemeMode.system;',
     '      case "dark":\n        return ThemeMode.dark;\n      case "system":\n        return ThemeMode.system;\n      default:\n        return ThemeMode.dark;',
     'case "system":')

print("Branding selesai diterapkan.")
