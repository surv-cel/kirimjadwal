import os, json, sys, requests
from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright

FONNTE_TOKEN = os.environ["FONNTE_TOKEN"]
TARGET       = os.environ["TARGET"]
COOKIES      = json.loads(os.environ["COOKIES_JSON"])
UNIT_ID      = "19"

SHIFT_LIBUR = ["L","C","S","CM"]
URUTAN      = ["P7","P8","P10","S4","M"]
HARI = ["Minggu","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"]
BULAN = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus",
         "September","Oktober","November","Desember"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"

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

def ambil_roster(bulan, tahun):
    url = f"https://absensi.tif3.net/portal/dashboard/roster?unit_id={UNIT_ID}&bulan={bulan}&tahun={tahun}&mode=web"
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(user_agent=UA, viewport={"width":1400,"height":900})
        ctx.add_cookies(COOKIES)
        pg = ctx.new_page()
        pg.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        pg.goto(url, wait_until="domcontentloaded", timeout=90000)
        try:
            pg.wait_for_selector("table", timeout=60000)
        except Exception:
            pg.screenshot(path="debug.png")
            print("GAGAL MUAT HALAMAN:", pg.content()[:500]); sys.exit(1)
        pg.wait_for_timeout(3000)
        data = pg.evaluate(EXTRACT_JS)
        b.close()
    return data

def pasangan(nama, sb_baru, asalnya, key, orig, baru):
    cands = [n for n in orig if n != nama and orig[n].get(key) == sb_baru and baru.get(n,{}).get(key) != sb_baru]
    perf  = [n for n in cands if baru[n].get(key) == asalnya]
    return (perf or cands or [None])[0]

def main
