// Prueba del análisis de video completo con los videos sintéticos de pruebas/generar_videos_prueba.py.
// Carga cada video, pulsa «Analizar el video completo» desde el cuadro 0 y compara con la verdad (JSON):
// cobertura del video, posiciones inventadas (donde el balón no se ve), intervalos sin detección, error de posición y área.
// Requisitos: npm i playwright (y Chrome instalado).  Uso:  node pruebas/prueba_video_completo.js [completo tapado ...]
const { chromium } = require(process.env.PLAYWRIGHT || "playwright");
const fs = require("fs"), path = require("path");
const PROY = path.resolve(__dirname, "..");
const CARP = path.join(PROY, "videos prueba", "sinteticos");
const nombres = process.argv.slice(2).length ? process.argv.slice(2) : ["completo", "aparece_tarde", "tapado", "tarde_y_tapado", "oscuro_tapado"];
(async () => {
  const b = await chromium.launch({ channel: "chrome", args: ["--autoplay-policy=no-user-gesture-required"] });
  let fallos = 0;
  for (const n of nombres) {
    const verdad = JSON.parse(fs.readFileSync(path.join(CARP, `prueba_${n}.json`), "utf8"));
    const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
    const errores = []; p.on("pageerror", e => errores.push(e.message));
    await p.goto("file:///" + PROY.split(path.sep).join("/") + "/pagina_interactiva.html");
    await p.evaluate(() => { document.querySelectorAll("[data-modo]").forEach(x => x.dataset.modo === "tiro" && x.click()); });
    const [fc] = await Promise.all([p.waitForEvent("filechooser"), p.click("#cargar")]);
    await fc.setFiles(path.join(CARP, verdad.video));
    await p.waitForFunction(() => tiro.video && tiro.vAna && tiro.vAna._listo && tiro.fpsFuente, null, { timeout: 30000 });
    await p.waitForTimeout(2200);
    const t0 = Date.now();
    await p.evaluate(() => { tiro.video.pause(); tiro.video.currentTime = 0.5; document.getElementById("vseg").click(); });
    // espera: empieza (buscando o analizando) y termina (o pide un clic)
    await p.waitForFunction(() => tiro.seg.activo || tiro.seg.buscando || tiro.seg.analizando || fase === "semilla", null, { timeout: 20000 });
    await p.waitForFunction(() => !tiro.seg.activo && !tiro.seg.buscando && !tiro.seg.analizando, null, { timeout: 240000, polling: 500 });
    // si la página no encontró el balón sola (p. ej. un balón oscuro), pide un clic: se hace como lo haría el usuario,
    // sobre la posición real del balón en el cuadro que muestra el video
    let clic = false;
    if (await p.evaluate(() => fase === "semilla" && !tiro.seg.activo)) {
      clic = true;
      const c = await p.evaluate(V => { const t = tiro.video.currentTime; let k = Math.round(t * V.fps); while (k < V.cuadros.length - 1 && !V.cuadros[k].visible) k++; return { k, t: V.cuadros[k].t }; }, verdad);
      await p.evaluate(async t => { await seekA(tiro.video, t + 0.5 / tiro.fps); }, c.t);
      const v = verdad.cuadros[c.k];
      await p.evaluate(({ x, y }) => { const r = canvas.getBoundingClientRect(), d = devicePixelRatio || 1; canvas.dispatchEvent(new MouseEvent("click", { clientX: r.left + (vista.ox + x * vista.s) / d, clientY: r.top + (vista.oy + y * vista.s) / d, bubbles: true })); }, v);
      await p.waitForFunction(() => tiro.seg.activo, null, { timeout: 20000 });
      await p.waitForFunction(() => !tiro.seg.activo && !tiro.seg.buscando && !tiro.seg.analizando, null, { timeout: 240000, polling: 500 });
    }
    const r = await p.evaluate(() => ({
      fps: tiro.fps, fuente: tiro.fpsFuente, fase, msg: tiro.seg.msg,
      linea: tiro.linea.map(q => [q.t, q.e]), sin: intervalosSin().map(s => [s.a, s.b]),
      puntos: tiro.puntos.filter(q => q.auto && q.t != null).map(q => ({ t: q.t, x: q.x, y: q.y, fuera: !!q.fuera, at: !!q.atipico, dud: esDudoso(q) })),
      cam: tiro.cam.slice(0, 1), tramo: tiro.tramo, area: tiro.res && tiro.res.area, d: tiro.res && tiro.res.d, g: tiro.res && tiro.res.tiempo && tiro.res.tiempo.g,
      calidad: tiro.res && calidadMedicion(tiro.res).nivel, dur: tiro.video.duration
    }));
    const seg = (Date.now() - t0) / 1000, dt = 1 / verdad.fps;
    const enCuadro = t => verdad.cuadros[Math.min(verdad.cuadros.length - 1, Math.max(0, Math.round(t * verdad.fps)))];
    // la primera posición (mundo) coincide con la imagen del primer cuadro analizado: la cámara está fija en estos videos
    const inventados = r.puntos.filter(q => !enCuadro(q.t).visible).map(q => +q.t.toFixed(3));
    const errPx = r.puntos.filter(q => enCuadro(q.t).visible).map(q => Math.hypot(q.x - enCuadro(q.t).x, q.y - enCuadro(q.t).y));
    const lejos = errPx.filter(e => e > 6).length;
    const cubre = r.linea.length ? [r.linea[0][0], r.linea[r.linea.length - 1][0] + dt] : [null, null];
    const sinVerdad = []; let ini = null; verdad.cuadros.forEach((c, i) => { if (!c.visible && ini == null) ini = c.t; if (ini != null && (c.visible || i === verdad.cuadros.length - 1)) { sinVerdad.push([ini, c.visible ? c.t : c.t + dt]); ini = null; } });
    const errArea = r.area != null ? Math.abs(r.area - verdad.area_real_m2) / verdad.area_real_m2 * 100 : null;
    const ok = !errores.length && cubre[0] != null && cubre[0] <= (clic ? 0.6 : 0.05) && cubre[1] >= r.dur - 0.15 && inventados.length === 0 && lejos <= 2 && r.fase !== "semilla" && errArea != null && errArea < 15;
    if (!ok) fallos++;
    console.log(`${ok ? "OK   " : "FALLA"} ${n.padEnd(15)} ${seg.toFixed(1)} s${clic ? " · balón indicado con clic" : ""} · FPS ${r.fps} (${r.fuente}) · analizado ${cubre.map(x => x == null ? "—" : x.toFixed(2)).join("–")} de ${r.dur.toFixed(2)} s · ${r.puntos.length} posiciones (${r.puntos.filter(q => !q.fuera && !q.at).length} en el ajuste, ${r.puntos.filter(q => q.dud).length} dudosas) · inventadas ${inventados.length}${inventados.length ? " " + JSON.stringify(inventados.slice(0, 6)) : ""} · error de posición mediana ${errPx.length ? errPx.sort((a, b) => a - b)[errPx.length >> 1].toFixed(2) : "—"} px (>6 px: ${lejos})`);
    console.log(`      sin detección: ${JSON.stringify(r.sin.map(s => s.map(x => +x.toFixed(2))))} · verdad sin balón: ${JSON.stringify(sinVerdad.map(s => s.map(x => +x.toFixed(2))))}`);
    console.log(`      tramo ${r.tramo ? r.tramo.a.toFixed(2) + "–" + r.tramo.b.toFixed(2) + " s (" + r.tramo.motivo + ")" : "—"} · área ${r.area != null ? r.area.toFixed(3) : "—"} m² (real ${verdad.area_real_m2}, error ${errArea != null ? errArea.toFixed(1) : "—"} %) · g ${r.g != null ? r.g.toFixed(2) : "—"} · calidad ${r.calidad || "—"}${r.msg ? " · " + r.msg : ""}${errores.length ? " · ERRORES: " + errores.join(" | ") : ""}`);
    if (process.env.DET) console.log("      " + r.puntos.map(q => { const v = enCuadro(q.t); return `${q.t.toFixed(2)}:${v.visible ? Math.hypot(q.x - v.x, q.y - v.y).toFixed(0) : "X"}${q.fuera ? "f" : ""}`; }).join(" "));
    if (process.env.BIT) console.log((await p.evaluate(() => [...document.querySelectorAll("#bit-lista li")].reverse().map(l => l.innerText.replace(/\s+/g, " ").slice(0, 170)).filter(x => !/ #\d+ /.test(x)))).join("\n"));
    await p.close();
  }
  await b.close();
  process.exit(fallos ? 1 : 0);
})();
