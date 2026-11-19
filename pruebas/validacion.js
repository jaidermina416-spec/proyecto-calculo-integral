const { chromium } = require("playwright"); const fs = require("fs");
const PROY = "C:/Users/Usuario/Documents/proyeto calculo integral";
const casos = new Function("return " + (process.argv[2] || "[{}]"))();
(async () => {
  const b = await chromium.launch({ args: ["--autoplay-policy=no-user-gesture-required"] });
  for (const c of casos) {
    const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
    p.on("pageerror", e => console.log("PAGEERR", e.message));
    await p.goto("file:///" + PROY + "/pagina_interactiva.html");
    await p.addScriptTag({ content: fs.readFileSync(PROY + "/pruebas/prueba_seguimiento.js", "utf8") });
    await p.evaluate(() => { document.querySelectorAll("[data-modo]").forEach(x => x.dataset.modo === "tiro" && x.click()); });
    const r = await p.evaluate(a => window.probar(a), c);
    console.log(JSON.stringify(c), "=>", JSON.stringify(r));
    await p.close();
  }
  await b.close();
})();
