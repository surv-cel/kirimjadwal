import os, sys, requests
from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright

# ================= KONFIG (dari Secrets GitHub) =================
FONNTE_TOKEN = os.environ["HwHb4ACdg4TRmVGxS57t"]
TARGET       = os.environ["TARGET"]
COOKIE_STR   = os.environ["COOKIE_STRING"]
UNIT_ID      = "19"   # RAC

SHIFT_LIBUR = ["L", "C", "S", "CM"]
URUTAN      = ["P7", "P8", "P10", "S4", "M"]
HARI = ["Minggu","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"]
BULAN = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus",
         "September","Oktober","November","Desember"]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")

EXTRACT_JS = """
() => {
  for (const t of document.querySelectorAll("table")) {
    let dateCols = null; const out = [];
    for (const tr of t.querySelectorAll("tr")) {
      const cells = [...tr.querySelectorAll("th,td")].map(c => c.innerText.trim());
      if (!cells.length) continue;
      if (!dateCols) {
        if (cells[0].toUpperCase().includes("NAMA") && parseInt(cells[1]) === 1)
          dateCols = cells.slice(1).map(x => parseInt(x));
        continue;
      }
      const nama = cells[0];
      if (!nama || nama === "NAMA" || !isNaN(parseInt(nama))) continue;
      const shifts = {};
      cells.slice(1).forEach((txt,i) => { const d = dateCols[i]; if (d>=1 && d<=31 && txt) shifts[d]=txt; });
      if (Object.keys(shifts).length) out.push({nama, shifts});
    }
    if (out.length) return out;
  }
  return null;
}
"""

def parse_cookies(s):
    out = []
    for part in s.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            out.append({"name": k.strip(), "value": v.strip(),
                        "domain": ".absensi.tif3.net", "path": "/"})
    return out

def ambil_roster(bulan, tahun
