from playwright.sync_api import sync_playwright
import json
log=[{"ts":i,"date":f"2026-11-{1+i*2:02d}","type":"main","pb":None,"pa":None,"done":6,"total":6} for i in range(10)]
st={"start":"2026-10-25","override":"auto","log":log,"strap":{}}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    for now,lg in [("2026-11-30T12:00:00",log),("2026-11-30T12:00:00",log[:5]),("2026-11-10T12:00:00",log)]:
        ctx=b.new_context(viewport={"width":390,"height":844})
        ctx.add_init_script(f"window.__NOW='{now}'; localStorage.setItem('shoulderRoutine.v2', {json.dumps(json.dumps({**st,'log':lg}))})")
        pg=ctx.new_page(); pg.goto("http://localhost:8765/")
        print(now,len(lg), pg.locator(".muted.small").first.inner_text(), "|", pg.locator(".hero .big").inner_text())
        pg.click("[data-start='main']"); pg.click("#pp [data-p='skip']"); pg.click("#skip")
        print("  ex2:", pg.locator(".exname").inner_text())
        ctx.close()
    b.close()
