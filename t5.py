# PWA checks: manifest valid, icons load, service worker registers and controls, offline reload works
from playwright.sync_api import sync_playwright
import json, urllib.request
base="http://localhost:8765/"
m=json.load(urllib.request.urlopen(base+"manifest.webmanifest"))
for k in ["name","short_name","start_url","scope","display","icons","theme_color","background_color"]: assert k in m,k
assert m["start_url"]=="./" and m["scope"]=="./" and m["display"]=="standalone"
sizes={(i["sizes"],i.get("purpose","any")) for i in m["icons"]}
assert ("192x192","any") in sizes and ("512x512","any") in sizes and ("512x512","maskable") in sizes
from PIL import Image; import io
for i in m["icons"]+[{"src":"icons/apple-touch-icon.png","sizes":"180x180"}]:
    im=Image.open(io.BytesIO(urllib.request.urlopen(base+i["src"]).read())); assert "%dx%d"%im.size==i["sizes"], i
print("manifest + icons ok")
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx=b.new_context(viewport={"width":390,"height":844}); errs=[]
    ctx.add_init_script("window.__NOW='2026-10-27T11:00:00'")
    pg=ctx.new_page(); pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m_: m_.type=="error" and errs.append(m_.text))
    pg.goto(base)
    pg.evaluate("localStorage.setItem('shoulderRoutine.v2', JSON.stringify({start:'2026-10-25',override:'auto',log:[{ts:1,date:'2026-10-25',type:'core',done:3,total:3}],strap:{}}))")
    scope=pg.evaluate("navigator.serviceWorker.ready.then(r=>r.scope)"); print("sw scope:", scope)
    pg.reload(); pg.wait_for_function("navigator.serviceWorker.controller!==null")
    keys=pg.evaluate("caches.keys()"); n=pg.evaluate(f"caches.open({json.dumps(keys[0])}).then(c=>c.keys()).then(k=>k.length)"); print("caches:", keys, "entries:", n)
    print("manifest link:", pg.evaluate("document.querySelector('link[rel=manifest]').href"))
    ctx.set_offline(True); pg.reload(); print("offline reload title:", pg.title(), "| hero:", pg.locator(".hero .big").inner_text())
    pg.click("[data-tab='progress']"); print("offline log kept:", pg.locator(".log li").count())
    pg.click("[data-tab='settings']"); assert "Add to Home Screen" in pg.content() and "Paste backup" in pg.content()
    ctx.set_offline(False)
    print("errors:", errs); assert not errs
    b.close()
