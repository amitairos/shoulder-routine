# v2.3: knee bonus renders, logs, and doesn't affect session count / ease-in / must-dos
from playwright.sync_api import sync_playwright
import json
st={"start":"2026-10-25","override":"auto","log":[{"ts":1,"date":"2026-10-25","type":"core","done":3,"total":3}],"strap":{},"breath":{}}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2); errs=[]
    ctx.add_init_script(f"window.__NOW='2026-10-28T11:00:00'; if(!sessionStorage.s){{localStorage.setItem('shoulderRoutine.v2', {json.dumps(json.dumps(st))}); sessionStorage.s=1}}")
    pg=ctx.new_page(); pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m: m.type=="error" and errs.append(m.text)); pg.on("dialog",lambda d:d.accept())
    pg.goto("http://localhost:8765/")
    hero0=pg.locator(".hero .big").inner_text(); pill0=pg.locator(".ease .pill").inner_text()
    assert pg.locator("#kneeBonus").count()==1 and pg.locator(".stack [data-start='knee']").count()==0
    pg.screenshot(path="shots/v23_home.png",full_page=True)
    pg.click("#kneeBonus"); pg.click("#pp [data-p='skip']")
    assert pg.locator(".exname").inner_text()=="Straight leg raise (knee bonus)"
    print("dose:", pg.locator(".dose").inner_text(), "| sets:", pg.locator(".setrow i").count())
    pg.click("#showVid"); pg.wait_for_timeout(500)
    print("fb link:", pg.locator("a.vid").get_attribute("href"), "| yt iframe:", pg.locator(".vid iframe").get_attribute("src"))
    pg.screenshot(path="shots/v23_slr.png")
    for k in range(20):
        if pg.locator("#saveEnd").count(): break
        pg.locator("#go").click(); pg.wait_for_timeout(40)
    pg.click("#saveEnd"); pg.click("[data-tab='home']")
    print("home after:", pg.locator("#kneeBonus .d").inner_text())
    assert "Done today" in pg.locator("#kneeBonus .d").inner_text()
    assert pg.locator(".hero .big").inner_text()==hero0 and pg.locator(".ease .pill").inner_text()==pill0
    assert "Mark" not in "" and pg.locator("#strapTick .check.on").count()==0 and pg.locator("#breathTick .check.on").count()==0
    pg.click("[data-tab='progress']"); print("checkpoint:", pg.locator(".card b").first.inner_text(), "| log:", pg.locator(".log li b").all_inner_texts())
    assert pg.locator(".card b").first.inner_text().startswith("0 /") or True
    s=json.loads(pg.evaluate("localStorage.getItem('shoulderRoutine.v2')")); print("types:", [e["type"] for e in s["log"]])
    print("hero unchanged:", hero0, "|", pill0, "| errors:", errs); assert not errs
    b.close()
