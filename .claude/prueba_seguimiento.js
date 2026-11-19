// Prueba automática del seguimiento: genera un video sintético con física conocida,
// lo carga en la página, calibra con el poste, siembra el balón y mide el resultado.
// Uso: pegar en la consola de pagina_interactiva.html y ejecutar  await probar({ fluido: true })
window.probar = async function ({ fluido = true, vx0 = 7, vy0 = 6.5, y0 = 0.2, rate = 0.5, ruido = 0, rb = 11, calibrar = true, tIni = 0.1 } = {}) {
  const W = 1280, H = 720, suelo = 650, k = 100, T = 1.4;
  const cv = document.createElement("canvas"); cv.width = W; cv.height = H; const gx = cv.getContext("2d");
  const fondo = document.createElement("canvas"); fondo.width = W; fondo.height = H; const fg = fondo.getContext("2d");
  fg.fillStyle = "#1b2b55"; fg.fillRect(0, 0, W, suelo);
  for (let i = 0; i < 400; i++) { fg.fillStyle = `hsl(${(i * 47) % 360},40%,${30 + (i % 5) * 7}%)`; fg.beginPath(); fg.arc((i * 97) % W, 60 + (i * 31) % 400, 7, 0, 7); fg.fill(); }
  fg.fillStyle = "#1e7a3e"; fg.fillRect(0, suelo, W, H);
  fg.strokeStyle = "#ddd"; fg.lineWidth = 8; fg.beginPath(); fg.moveTo(1220, suelo); fg.lineTo(1220, suelo - 244); fg.stroke();
  const real = t => ({ x: 120 + vx0 * t * k, y: suelo - (y0 + vy0 * t - 9.81 * t * t / 2) * k });
  let tStart = null;
  const draw = () => {
    const now = performance.now(); if (tStart == null) tStart = now;
    const t = Math.min((now - tStart) / 1000, T), p = real(t);
    gx.drawImage(fondo, 0, 0);
    if (ruido) { gx.globalAlpha = ruido; gx.fillStyle = Math.random() > .5 ? "#fff" : "#000"; gx.fillRect(0, 0, W, H); gx.globalAlpha = 1; }
    gx.fillStyle = "#fff"; gx.beginPath(); gx.arc(p.x, p.y, rb, 0, 7); gx.fill();
    if (rb > 6) { gx.fillStyle = "#222"; gx.beginPath(); gx.arc(p.x - 3, p.y - 2, 4, 0, 7); gx.fill(); }
  };
  draw();
  const rec = new MediaRecorder(cv.captureStream(30), { mimeType: "video/webm" }), chunks = [];
  rec.ondataavailable = e => chunks.push(e.data);
  rec.start(100); tStart = null; const iv = setInterval(draw, 16);
  await new Promise(r => setTimeout(r, 2000)); clearInterval(iv);
  await new Promise(r => { rec.onstop = r; rec.stop(); });
  abrirArchivo(new File([new Blob(chunks, { type: "video/webm" })], "tiro_sintetico.webm", { type: "video/webm" }), tiro);
  await new Promise(r => setTimeout(r, 2500));
  const clic = (x, y) => { const r = canvas.getBoundingClientRect(), dpr = devicePixelRatio || 1; canvas.dispatchEvent(new MouseEvent("click", { clientX: r.left + (vista.ox + x * vista.s) / dpr, clientY: r.top + (vista.oy + y * vista.s) / dpr, bubbles: true })); };
  const bola = () => { const c2 = document.createElement("canvas"); c2.width = W; c2.height = H; const g2 = c2.getContext("2d"); g2.drawImage(tiro.video, 0, 0); const d = g2.getImageData(0, 0, 1180, 640).data; let sx = 0, sy = 0, n = 0; for (let y = 0; y < 640; y++) for (let x = 0; x < 1180; x++) { const i = (y * 1180 + x) * 4; if (d[i] > 235 && d[i + 1] > 235 && d[i + 2] > 235) { sx += x; sy += y; n++; } } return { x: sx / n, y: sy / n }; };
  if (fluido && document.hidden !== false) { /* la prueba asume pestaña visible para rVFC real */ }
  tiro.video.pause(); if (calibrar) { clic(1220, 650); clic(1220, 406); }
  await seekA(tiro.video, tIni);
  tiro.seg.rate = rate;
  if (!fluido) { const orig = HTMLVideoElement.prototype.requestVideoFrameCallback; delete HTMLVideoElement.prototype.requestVideoFrameCallback; setTimeout(() => { if (orig) HTMLVideoElement.prototype.requestVideoFrameCallback = orig; }, 100); }
  tiro.modoSeg = "auto"; render();
  document.getElementById("vseg").click();
  // el modo automático busca el balón (asíncrono); si no está seguro, pide un clic sobre él
  for (let i = 0; i < 150 && !tiro.seg.activo && fase !== "semilla"; i++) await new Promise(r => setTimeout(r, 100));
  if (fase === "semilla" && !tiro.seg.activo) { const b = bola(); clic(b.x, b.y); }
  for (let i = 0; i < 50 && !tiro.seg.activo; i++) await new Promise(r => setTimeout(r, 100));
  for (let i = 0; i < 60 && tiro.seg.activo; i++) await new Promise(r => setTimeout(r, 500));
  const r = tiro.res;
  const tAt = (-vy0 - Math.sqrt(vy0 * vy0 + 4 * 4.905 * y0)) / (-2 * 4.905), dReal = vx0 * tAt;
  const aReal = (() => { const a = -4.905 / vx0 ** 2, bb = vy0 / vx0; return a * dReal ** 3 / 3 + bb * dReal ** 2 / 2 + y0 * dReal; })();
  return { modo: tiro.seg.fluido ? "fluido" : "cuadro a cuadro", fin: tiro.seg.msg, posiciones: tiro.puntos.length, repetidos: tiro.seg.repetidos, area: r && +r.area.toFixed(3), areaReal: +aReal.toFixed(3), errArea: r && +(Math.abs(r.area - aReal) / aReal * 100).toFixed(2), vx: r && r.tiempo && +Math.abs(r.tiempo.vx).toFixed(3), g: r && r.tiempo && r.tiempo.g && +r.tiempo.g.toFixed(2), r2: r && r.r2 && +r.r2.toFixed(5) };
};
