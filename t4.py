# v2.2 checks: ease-in card/suggestion, rest day between sessions, Tips tab, optional heat, chin-nod dose
from playwright.sync_api import sync_playwright
import json
out="/workspace/shoulder-app/shots/"
def L(*dates): return [{"ts":i+1,"date":d,"type":"core","pb":None,"pa":None,"done":3,"total":3} for i,d in enumerate(dates)]
def st(log): return {"start":"2026-10-25","override":"auto","log":log,"strap":{}}
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    def page(now,state):
        ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2)
        init=f"window.__NOW='{now}';" + (f"localStorage.setItem('shoulderRoutine.v2', {json.dumps(json.dumps(state))});" if state is not None else "")
        ctx.add_init_script(init); pg=ctx.new_page()
        pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m: m.type=="error" and errs.append(m.text))
        pg.on("dialog",lambda d: d.accept()); pg.goto("http://localhost:8765/"); return ctx,pg
    def hero(pg): return pg.locator(".hero .big").inner_text()
    def ease(pg): return pg.locator(".ease").count()
    # 1 fresh device, Tue 27 Oct: 25 Oct counts as #1 -> core suggested, ease card
    c,pg=page("2026-10-27T11:00:00",None)
    print("1 fresh Tue 27:", hero(pg), "| ease card:", ease(pg), "|", pg.locator(".ease .pill").inner_text())
    assert hero(pg).startswith("Core only") and ease(pg)==1
    pg.screenshot(path=out+"v22_home_ease.png",full_page=True)
    pg.click("text=Start today's session"); print("  pain0 ease card:", ease(pg)); assert ease(pg)==1
    pg.screenshot(path=out+"v22_pain0.png"); c.close()
    # 2 trained Tue 27 -> Wed 28 rest day between sessions
    c,pg=page("2026-10-28T11:00:00",st(L("2026-10-25","2026-10-27")))
    print("2 Wed 28 after Tue:", hero(pg), "| rest note:", "leave a rest day" in pg.content()); assert "strap" in hero(pg).lower() and "leave a rest day" in pg.content(); c.close()
    # 3 three sessions logged -> still easing (session 4 of 4)
    c,pg=page("2026-11-01T11:00:00",st(L("2026-10-25","2026-10-27","2026-10-29")))
    print("3 Sun 1 Nov, 3 logged:", hero(pg), "| ease:", ease(pg)); assert hero(pg).startswith("Core only") and ease(pg)==1; c.close()
    # 4 four sessions -> ease-in over, main suggested, no card
    c,pg=page("2026-11-03T11:00:00",st(L("2026-10-25","2026-10-27","2026-10-29","2026-11-01")))
    print("4 Tue 3 Nov, 4 logged:", hero(pg), "| ease:", ease(pg)); assert hero(pg).startswith("Main") and ease(pg)==0
    pg.click("text=Start today's session"); print("  pain0 ease card:", ease(pg)); assert ease(pg)==0; c.close()
    # 4b 25 Oct not logged on this device but 3 later ones are -> counts 4, done
    c,pg=page("2026-11-03T11:00:00",st(L("2026-10-27","2026-10-29","2026-11-01")))
    print("4b without 25 Oct log:", hero(pg), "| ease:", ease(pg)); assert ease(pg)==0; c.close()
    # 5 Tips tab, flare heat, chin nod dose
    c,pg=page("2026-10-26T11:00:00",None)
    pg.click("[data-tab='tips']"); t=pg.locator(".wrap").inner_text()
    for k in ["24-hour rule","tolerable","stabbing","one fewer set","later that day or the next day","headrest","30–40 minutes","High pillow","Insoles","chin tuck","shoulder-blade squeezes","heat","Higher chair"]:
        assert k in t, k
    assert "Ya'akov" not in t and "reel" not in t.lower()
    print("5 tips ok"); pg.screenshot(path=out+"v22_tips.png",full_page=True)
    pg.click("[data-tab='home']"); pg.click("text=Pain rule & everyday tips"); assert pg.locator("h1").inner_text()=="Tips"
    pg.click("[data-tab='home']"); pg.click("[data-start='flare']"); pg.click("#pp [data-p='skip']")
    print("  flare step 1:", pg.locator(".exname").inner_text(), "|", pg.locator("#skip").inner_text()); assert pg.locator(".exname").inner_text()=="Heat, if you want it"
    c.close()
    def nodsets(now):
        c,pg=page(now,None); pg.click("[data-start='strap']")
        while not pg.locator(".exname").inner_text().startswith("Chin nod"): pg.locator("#go").click()
        n=pg.locator(".setrow i").count(); c.close(); return n
    a,bb=nodsets("2026-10-26T11:00:00"),nodsets("2026-11-05T11:00:00")
    print("6 chin nod sets early/later:", a, bb); assert (a,bb)==(5,10)
    print("errors:",errs); assert not errs
    b.close()
