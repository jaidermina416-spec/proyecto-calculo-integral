// Prueba automática del seguimiento: genera un video sintético con física conocida,
// lo carga en la página, calibra con el poste, siembra el balón y mide el resultado.
// Uso: pegar en la consola de pagina_interactiva.html y ejecutar  await probar({ fluido: true })
window.probar = async function ({ fluido = true, vx0 = 7, vy0 = 6.5, y0 = 0.2, rate = 0.5, ruido = 0, rb = 11, calibrar = true, tIni = 0.1, pan = 0, zoom = 0, color = "#fff", cesped = true } = {}) {
  const W = 1280, H = 720, suelo = 650, k = 100, T = 1.4;
  const cv = document.createElement("canvas"); cv.width = W; cv.height = H; const gx = cv.getContext("2d");
  const fondo = document.createElement("canvas"); fondo.width = W; fondo.height = H; const fg = fondo.getContext("2d");
  fg.fillStyle = "#1b2b55"; fg.fillRect(0, 0, W, suelo);
  for (let i = 0; i < 400; i++) { fg.fillStyle = `hsl(${(i * 47) % 360},40%,${30 + (i % 5) * 7}%)`; fg.beginPath(); fg.arc((i * 97) % W, 60 + (i * 31) % 400, 7, 0, 7); fg.fill(); }
  fg.fillStyle = cesped ? "#1e7a3e" : "#6b5a44"; fg.fillRect(0, suelo, W, H);
  fg.strokeStyle = "#ddd"; fg.lineWidth = 8; fg.beginPath(); fg.moveTo(1220, suelo); fg.lineTo(1220, suelo - 244); fg.stroke();
  const real = t => ({ x: 120 + vx0 * t * k, y: suelo - (y0 + vy0 * t - 9.81 * t * t / 2) * k });
  let tStart = null, semillaManual = false;
  const cam = t => { const Z = 1 + zoom * t, ox = pan * t; return { Z, ox, a: Z, e: W / 2 - Z * (ox + W / 2), f: H / 2 - Z * H / 2 }; };
  const aImg = (p, t) => { const c = cam(t); return { x: c.a * p.x + c.e, y: c.a * p.y + c.f }; };
  const draw = (tt = 0) => {
    const t = Math.min(tt, T), p = real(t);
    const c = cam(t); gx.setTransform(1, 0, 0, 1, 0, 0); gx.fillStyle = "#000"; gx.fillRect(0, 0, W, H); gx.setTransform(c.a, 0, 0, c.a, c.e, c.f); gx.drawImage(fondo, 0, 0);
    gx.setTransform(1, 0, 0, 1, 0, 0);
    if (ruido) { gx.globalAlpha = ruido; gx.fillStyle = Math.random() > .5 ? "#fff" : "#000"; gx.fillRect(0, 0, W, H); gx.globalAlpha = 1; }
    const q = aImg(p, t), rr = rb * c.a;
    gx.fillStyle = "#ff00ff"; gx.fillRect(0, 0, Math.round(t * 200), 4); // reloj incrustado: permite saber el instante físico exacto de cada cuadro
    gx.fillStyle = color; gx.beginPath(); gx.arc(q.x, q.y, rr, 0, 7); gx.fill();
    if (rb > 6) { gx.fillStyle = "#222"; gx.beginPath(); gx.arc(q.x - 3 * c.a, q.y - 2 * c.a, 4 * c.a, 0, 7); gx.fill(); }
  };
  draw();
  // un cuadro por paso, con el instante exacto n/30: la grabación es reproducible (sin depender del reloj)
  const fps = 30, stream = cv.captureStream(0), track = stream.getVideoTracks()[0];
  const rec = new MediaRecorder(stream, { mimeType: "video/webm", videoBitsPerSecond: 8e6 }), chunks = [];
  rec.ondataavailable = e => chunks.push(e.data);
  draw(0); rec.start(); await new Promise(r => setTimeout(r, 100));
  // el instante dibujado es el real de cada cuadro (el del archivo webm): así el tiempo del video coincide con la física dibujada
  const t00 = performance.now();
  while ((performance.now() - t00) / 1000 < T + 0.4) { draw((performance.now() - t00) / 1000); track.requestFrame(); await new Promise(r => setTimeout(r, 30)); }
  await new Promise(r => { rec.onstop = r; rec.stop(); });
  abrirArchivo(new File([new Blob(chunks, { type: "video/webm" })], "tiro_sintetico.webm", { type: "video/webm" }), tiro);
  await new Promise(r => setTimeout(r, 2500));
  const clic = (x, y) => { const r = canvas.getBoundingClientRect(), dpr = devicePixelRatio || 1; canvas.dispatchEvent(new MouseEvent("click", { clientX: r.left + (vista.ox + x * vista.s) / dpr, clientY: r.top + (vista.oy + y * vista.s) / dpr, bubbles: true })); };
  // posición exacta del balón en el cuadro actual: se lee el reloj incrustado (barra magenta) y se aplica la física conocida
  const bola = () => { const c2 = document.createElement("canvas"); c2.width = W; c2.height = 8; const g2 = c2.getContext("2d"); g2.drawImage(tiro.video, 0, 0, W, H, 0, 0, W, H); const d = g2.getImageData(0, 2, W, 1).data; let n = 0; while (n < W && d[n * 4] > 200 && d[n * 4 + 1] < 80 && d[n * 4 + 2] > 200) n++; const tf = n / 200; return aImg(real(tf), tf); };
  if (fluido && document.hidden !== false) { /* la prueba asume pestaña visible para rVFC real */ }
  tiro.video.pause(); await seekA(tiro.video, tIni); if (calibrar) { const a = aImg({ x: 1220, y: 650 }, tIni), b = aImg({ x: 1220, y: 406 }, tIni); clic(a.x, a.y); clic(b.x, b.y); }
  await seekA(tiro.video, tIni);
  tiro.seg.rate = rate;
  if (!fluido) { const orig = HTMLVideoElement.prototype.requestVideoFrameCallback; delete HTMLVideoElement.prototype.requestVideoFrameCallback; setTimeout(() => { if (orig) HTMLVideoElement.prototype.requestVideoFrameCallback = orig; }, 100); }
  tiro.modoSeg = "auto"; render();
  document.getElementById("vseg").click();
  // el modo automático busca el balón (asíncrono); si no está seguro, pide un clic sobre él
  for (let i = 0; i < 150 && !tiro.seg.activo && fase !== "semilla"; i++) await new Promise(r => setTimeout(r, 100));
  if (fase === "semilla" && !tiro.seg.activo) { const b = bola(); semillaManual = true; clic(b.x, b.y); }
  for (let i = 0; i < 50 && !tiro.seg.activo; i++) await new Promise(r => setTimeout(r, 100));
  for (let i = 0; i < 60 && tiro.seg.activo; i++) await new Promise(r => setTimeout(r, 500));
  const r = tiro.res;
  const tAt = (-vy0 - Math.sqrt(vy0 * vy0 + 4 * 4.905 * y0)) / (-2 * 4.905), dReal = vx0 * tAt;
  const aReal = (() => { const a = -4.905 / vx0 ** 2, bb = vy0 / vx0; return a * dReal ** 3 / 3 + bb * dReal ** 2 / 2 + y0 * dReal; })();
  return { clic: semillaManual, modo: tiro.seg.fluido ? "fluido" : "cuadro a cuadro", fin: tiro.seg.msg, posiciones: tiro.puntos.length, repetidos: tiro.seg.repetidos, area: r && +r.area.toFixed(3), areaReal: +aReal.toFixed(3), errArea: r && +(Math.abs(r.area - aReal) / aReal * 100).toFixed(2), vx: r && r.tiempo && +Math.abs(r.tiempo.vx).toFixed(3), g: r && r.tiempo && r.tiempo.g && +r.tiempo.g.toFixed(2), r2: r && r.r2 && +r.r2.toFixed(5) };
};
