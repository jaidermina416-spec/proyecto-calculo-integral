const { chromium } = require("playwright");
const PROY = "C:/Users/Usuario/Documents/proyeto calculo integral";
const [, , video, t0s, maxs] = process.argv;
(async () => {
  const b = await chromium.launch({ channel: "chrome", args: ["--autoplay-policy=no-user-gesture-required"] });
  const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  p.on("pageerror", e => console.log("PAGEERR", e.message));
  await p.goto("file:///" + PROY + "/pagina_interactiva.html");
  await p.evaluate(() => { document.querySelectorAll("[data-modo]").forEach(x => x.dataset.modo === "tiro" && x.click()); window.__dbg = null; });
  const [fc] = await Promise.all([p.waitForEvent("filechooser"), p.click("#cargar")]); await fc.setFiles(PROY + "/videos prueba/" + video);
  await p.waitForFunction(() => tiro.video && Number.isFinite(tiro.video.duration) && tiro.vAna && tiro.vAna._listo, null, { timeout: 30000 });
  await p.waitForTimeout(2500);
  const info = await p.evaluate(async t0 => { const v = tiro.video; await seekA(v, t0); return { dur: v.duration, w: v.videoWidth, h: v.videoHeight, fps: tiro.fps }; }, +t0s || 0);
  console.log("video", JSON.stringify(info));
  await p.evaluate(() => document.getElementById("vseg").click());
  const t = Date.now(), max = (+maxs || 90) * 1000;
  let ult = "";
  while (Date.now() - t < max) {
    await p.waitForTimeout(3000);
    const st = await p.evaluate(() => ({ act: tiro.seg.activo, n: tiro.puntos.length, t: +tiempoVista().toFixed(2), z: tiro.cam.length ? +(tiro.cam[tiro.cam.length - 1].z || 1).toFixed(3) : 1, fase, msg: tiro.seg.msg }));
    const s = JSON.stringify(st); if (s !== ult) { console.log(Math.round((Date.now() - t) / 1000) + "s", s); ult = s; }
    if (!st.act && st.fase !== "semilla" && st.n > 0 && (await p.evaluate(() => !tiro.seg.analizando))) break;
    if (st.fase === "semilla" && !st.act && Date.now() - t > 20000) break;
  }
  const r = await p.evaluate(() => {
    const R = tiro.res; const bit = [...document.querySelectorAll("#bit-lista li")].reverse().map(l => l.innerText.replace(/\s+/g, " ").slice(0, 190)).filter(x => !/ #\d+ /.test(x));
    return { res: R && { area: +R.area.toFixed(2), d: +R.d.toFixed(1), ymax: +R.ymax.toFixed(2), r2: R.r2 && +R.r2.toFixed(4), vx: R.tiempo && +R.tiempo.vx.toFixed(2), g: R.tiempo && R.tiempo.g && +R.tiempo.g.toFixed(2), usados: R.usados.length }, nP: tiro.puntos.length, fuera: tiro.puntos.filter(q => q.fuera).length, ev: (tiro.eventos || []).map(e => [+e.t.toFixed(2), e.tipo]), bit: bit.slice(-14), dur: tiro.video.duration, tmax: Math.max(...tiro.puntos.map(q => q.t)) };
  });
  console.log(JSON.stringify(r.res), "puntos", r.nP, "fuera", r.fuera, "t_ultimo", r.tmax, "de", r.dur);
  console.log("EVENTOS", JSON.stringify(r.ev)); console.log(r.bit.join("\n"));
  await b.close();
})();
