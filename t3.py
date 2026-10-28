# v2.1 checks: old v2 saved state survives, strap+nod session, breathing tick, flare list, 12 kg texts
from playwright.sync_api import sync_playwright
import json
out="/workspace/shoulder-app/shots/"
old={"start":"2026-10-25","override":"auto","log":[{"ts":1,"date":"2026-10-25","type":"core","pb":None,"pa":None,"done":3,"total":3}],"strap":{"2026-10-24":True}}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2)
    ctx.add_init_script("window.__NOW='2026-10-26T11:00:00'; if(!sessionStorage.getItem('seeded')){localStorage.setItem('shoulderRoutine.v2', %s); sessionStorage.setItem('seeded','1');}" % json.dumps(json.dumps(old)))
    pg=ctx.new_page(); errs=[]
    pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m: m.type=="error" and errs.append(m.text))
    pg.on("dialog",lambda d: d.accept())
    pg.goto("http://localhost:8765/"); pg.screenshot(path=out+"v21_home.png",full_page=True)
    print("hero:", pg.locator(".hero .big").inner_text())
    assert "Every day: two must-dos" in pg.content()
    pg.click("[data-tab='progress']"); print("log kept:", pg.locator(".log li").count(), "|", pg.locator(".card p.muted.small").first.inner_text())
    pg.click("[data-tab='home']")
    pg.click("[data-start='strap']"); names=[]
    for k in range(200):
        if pg.locator("#saveEnd").count(): break
        n=pg.locator(".exname").inner_text()
        if not names or names[-1]!=n: names.append(n)
        if n.startswith("Chin nod") and 'nodshot' not in globals(): pg.screenshot(path=out+"v21_nod.png"); globals()['nodshot']=1
        pg.locator("#go").click(); pg.wait_for_timeout(40)
    print("strap session:", names)
    pg.click("#saveEnd"); pg.click("[data-tab='home']")
    print("strap tick:", pg.locator("#strapTick b").inner_text())
    pg.click("#breathTick"); print("breath tick:", pg.locator("#breathTick b").inner_text())
    pg.click("[data-start='flare']"); pg.click("#pp [data-p='skip']"); fl=[]
    for k in range(200):
        if pg.locator("#saveEnd").count(): break
        n=pg.locator(".exname").inner_text()
        if not fl or fl[-1]!=n: fl.append(n)
        pg.locator("#go").click(); pg.wait_for_timeout(40)
    print("flare session:", fl)
    print("end note has flare text:", "especially after sitting or driving" in pg.content())
    pg.click("#saveEnd")
    pg.reload(); st=json.loads(pg.evaluate("localStorage.getItem('shoulderRoutine.v2')"))
    print("stored keys:", sorted(st), "log:", [e["type"] for e in st["log"]], "breath:", st["breath"], "strap:", st["strap"])
    pg.click("[data-tab='settings']"); print("settings note ok:", "12 kg kettlebell" in pg.content())
    print("errors:",errs)
    b.close()
