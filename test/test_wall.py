
import json, sys, time
from playwright.sync_api import sync_playwright
url = sys.argv[1]; out = sys.argv[2]
src = sys.argv[3] if len(sys.argv) > 3 else None
errors = []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    dev = p.devices["Pixel 7"]
    ctx = b.new_context(**dev)
    pg = ctx.new_page()
    pg.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type in ("error","warning") else None)
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pg.goto(url, wait_until="networkidle")
    if src:
        pg.fill("#url", src); pg.click("button.go")
    else:
        pg.click("#sampleBtn")
    pg.wait_for_function("window.__wall.mode==='canvas' || window.__wall.mode==='idle'", timeout=30000)
    pg.click('.chip[data-n="1000"]')
    pg.wait_for_timeout(3500)
    st = pg.evaluate("""() => { const S = window.__wall; const cv = document.getElementById('cv');
      const r = { mode: S.mode, n: S.n, drawn: S.drawn, g: S.g, fps: S.fps, cors: S.cors, cw: cv.width, ch: cv.height,
                  playedText: document.getElementById('played').textContent, meta: document.getElementById('meta').textContent };
      try { const ctx = cv.getContext('2d'); const d = ctx.getImageData(0,0,cv.width,cv.height).data; const t = S.g.tile;
        let lit = 0, blank = 0;
        for (let i = 0; i < S.g.cols*S.g.rows; i++) { const cx = (i % S.g.cols)*t + (t>>1), cy = Math.floor(i / S.g.cols)*t + (t>>1);
          const k = (cy*cv.width + cx)*4; const v = d[k]+d[k+1]+d[k+2]; const bg = (d[k]===7 && d[k+1]===1 && d[k+2]===15);
          if (i < S.n) { if (!bg) lit++; } else if (bg) blank++; }
        r.litTiles = lit; r.blankExtra = blank; } catch (e) { r.pixelErr = String(e); }
      return r; }""")
    pg.screenshot(path=out, full_page=False)
    # wait for a loop to be counted
    pg.wait_for_timeout(6000)
    st["playedAfter"] = pg.evaluate("document.getElementById('played').textContent")
    st["fpsAfter"] = pg.evaluate("window.__wall.fps")
    # platform link check
    pg.fill("#url", "https://www.youtube.com/watch?v=abc"); pg.click("button.go")
    st["ytMsg"] = pg.inner_text("#msg")
    pg.fill("#url", "https://www.instagram.com/reel/xyz/"); pg.click("button.go")
    st["igMsg"] = pg.inner_text("#msg").split("\n")[0]
    st["iframes"] = pg.evaluate("document.querySelectorAll('iframe').length")
    st["errors"] = errors
    print(json.dumps(st, indent=1))
    b.close()
