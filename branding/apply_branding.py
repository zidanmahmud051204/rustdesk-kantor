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

print("Branding selesai diterapkan.")
