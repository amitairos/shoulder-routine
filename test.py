from playwright.sync_api import sync_playwright
import json
out="/workspace/shoulder-app/shots/"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    ctx.add_init_script("window.__NOW='2026-10-25T13:00:00'")
    pg=ctx.new_page(); errs=[]
    pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m: m.type=="error" and errs.append(m.text))
    pg.on("dialog",lambda d: d.accept())
    pg.goto("http://localhost:8765/"); pg.screenshot(path=out+"1_home.png")
    pg.click("text=Start today's session"); pg.screenshot(path=out+"2_pain.png")
    pg.click("#pp [data-p='4']"); pg.screenshot(path=out+"3_ex1.png")
    pg.click("#showVid"); pg.wait_for_timeout(1500); pg.screenshot(path=out+"4_video.png")
    pg.click("#go"); pg.wait_for_timeout(1200); pg.screenshot(path=out+"5_rest.png")
    pg.click("#go")  # skip rest
    # run through rest of session quickly
    for k in range(200):
        if pg.locator("#saveEnd").count(): break
        if pg.locator("#skip").count() and k>5:
            # complete sets via go, timers: click go twice (start then finish early)
            pass
        g=pg.locator("#go"); txt=g.inner_text()
        if k==30: pg.screenshot(path=out+"6_mid.png")
        g.click(); pg.wait_for_timeout(60)
        if "Start" in txt: 
            pg.wait_for_timeout(300)
            if k==40 or 'shot7' not in globals(): pg.screenshot(path=out+"7_timer.png"); globals()['shot7']=1
    pg.click("#pa [data-p='3']"); pg.screenshot(path=out+"8_end.png")
    pg.click("#saveEnd"); pg.wait_for_timeout(300); pg.screenshot(path=out+"9_progress.png",full_page=True)
    pg.click("[data-tab='home']"); pg.click("#strapTick"); pg.screenshot(path=out+"10_home_after.png")
    pg.click("[data-tab='settings']"); pg.screenshot(path=out+"11_settings.png")
    print("storage:", pg.evaluate("localStorage.getItem('shoulderRoutine.v2')"))
    pg.reload(); pg.click("[data-tab='progress']"); print("log after reload:", pg.locator(".log li").count())
    # dark mode + flare
    pg.emulate_media(color_scheme="dark"); pg.click("[data-tab='home']"); pg.click("[data-start='flare']"); pg.click("#pp [data-p='skip']"); pg.screenshot(path=out+"12_flare_dark.png")
    print("errors:",errs)
    b.close()
