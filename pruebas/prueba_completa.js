// Prueba de análisis completo: genera un video sintético con física conocida en el que el balón
// aparece tarde y queda tapado un momento, lo carga en la página y lo analiza desde el cuadro 0.
// Comprueba que el análisis recorre el video entero, que los cuadros sin balón quedan como «sin detección»
// (sin posiciones inventadas) y que el área del vuelo se parece a la real.
// Uso: se inyecta en pagina_interactiva.html y se llama  await probarCompleto({ aparece: 0.8, tapado: [1.5, 1.7] })
window.probarCompleto = async function ({ aparece = 0.8, tapado = null, dur = 3.2, vx0 = 7, vy0 = 6.5, y0 = 0.2, tDisparo = null, rb = 11, nombre = "tiro_sintetico.webm" } = {}) {
  const W = 1280, H = 720, suelo = 650, k = 100;
  const cv = document.createElement("canvas"); cv.width = W; cv.height = H; const gx = cv.getContext("2d");
  const fondo = document.createElement("canvas"); fondo.width = W; fondo.height = H; const fg = fondo.getContext("2d");
  fg.fillStyle = "#1b2b55"; fg.fillRect(0, 0, W, suelo);
  for (let i = 0; i < 400; i++) { fg.fillStyle = `hsl(${(i * 47) % 360},40%,${30 + (i % 5) * 7}%)`; fg.beginPath(); fg.arc((i * 97) % W, 60 + (i * 31) % 400, 7, 0, 7); fg.fill(); }
  fg.fillStyle = "#1e7a3e"; fg.fillRect(0, suelo - 110, W, H); // césped amplio: el balón quieto queda rodeado de verde
  fg.strokeStyle = "#ddd"; fg.lineWidth = 8; fg.beginPath(); fg.moveTo(1220, suelo); fg.lineTo(1220, suelo - 244); fg.stroke();
  // el disparo ocurre en tDisparo (por defecto, cuando aparece el balón): antes de eso el balón no está o está quieto
  const t0 = tDisparo == null ? aparece : tDisparo, g = 9.81;
  // vuelo parabólico; al tocar el suelo el balón rueda frenando y se detiene (no llega al poste)
  const uL = (vy0 + Math.sqrt(vy0 * vy0 + 2 * g * y0)) / g, tau = 0.15;
  const real = t => {
    const u = Math.max(0, t - t0);
    if (u <= uL) { const y = y0 + vy0 * u - g * u * u / 2; return { x: 120 + vx0 * u * k, y: suelo - Math.max(y, 0.11) * k, u }; }
    return { x: 120 + vx0 * uL * k + vx0 * k * tau * (1 - Math.exp(-(u - uL) / tau)), y: suelo - 0.11 * k, u };
  };
  // tapa fija (un jugador que pasa por delante): cubre la trayectoria entre tapado[0] y tapado[1]
  let caja = null;
  if (tapado) { const A = real(tapado[0]), B = real(tapado[1]), m = rb + 4; caja = { x0: Math.min(A.x, B.x) - m, x1: Math.max(A.x, B.x) + m, y0: Math.min(A.y, B.y) - m - 30, y1: Math.max(A.y, B.y) + m + 30 }; }
  const tapadoEn = t => { if (!caja) return false; const p = real(t); return p.x - rb >= caja.x0 && p.x + rb <= caja.x1 && p.y - rb >= caja.y0 && p.y + rb <= caja.y1; };
  const visible = t => t >= aparece && !tapadoEn(t);
  const draw = t => {
    gx.drawImage(fondo, 0, 0);
    gx.fillStyle = "#ff00ff"; gx.fillRect(0, 0, Math.round(t * 200), 4);
    if (t >= aparece) {
      const q = real(t);
      gx.fillStyle = "#fff"; gx.beginPath(); gx.arc(q.x, q.y, rb, 0, 7); gx.fill();
      gx.fillStyle = "#222"; gx.beginPath(); gx.arc(q.x - 3, q.y - 2, 4, 0, 7); gx.fill();
    }
    if (caja) { gx.fillStyle = "#3a2a1a"; gx.fillRect(caja.x0, caja.y0, caja.x1 - caja.x0, caja.y1 - caja.y0); gx.fillStyle = "#5a1a22"; gx.fillRect(caja.x0 + 8, caja.y0 + 10, caja.x1 - caja.x0 - 16, 40); }
  };
  const stream = cv.captureStream(0), track = stream.getVideoTracks()[0];
  const rec = new MediaRecorder(stream, { mimeType: "video/webm", videoBitsPerSecond: 8e6 }), chunks = [];
  rec.ondataavailable = e => chunks.push(e.data);
  draw(0); rec.start(); await new Promise(r => setTimeout(r, 100));
  const tt0 = performance.now();
  while ((performance.now() - tt0) / 1000 < dur) { draw((performance.now() - tt0) / 1000); track.requestFrame(); await new Promise(r => setTimeout(r, 30)); }
  await new Promise(r => { rec.onstop = r; rec.stop(); });
  const blob = new Blob(chunks, { type: "video/webm" });
  window.__ultimoVideo = blob;
  abrirArchivo(new File([blob], nombre, { type: "video/webm" }), tiro);
  for (let i = 0; i < 100 && !(tiro.video && tiro.vAna && tiro.vAna._listo); i++) await new Promise(r => setTimeout(r, 100));
  await new Promise(r => setTimeout(r, 2500));
  tiro.video.pause(); await seekA(tiro.video, 0);
  tiro.modoSeg = "auto"; render();
  const tIni = performance.now();
  document.getElementById("vseg").click();
  // se espera a que termine (o a que pida un clic, que es el comportamiento que se quiere evitar)
  let pidioClic = false, empezo = false;
  for (let i = 0; i < 480; i++) {
    await new Promise(r => setTimeout(r, 250));
    const ocupado = tiro.seg.activo || tiro.seg.analizando || tiro.seg.buscando;
    if (ocupado) empezo = true;
    if (!ocupado && fase === "semilla") { pidioClic = true; break; }
    if (!ocupado && (empezo || i > 40)) break;
  }
  // reloj incrustado (barra magenta): el tiempo del archivo webm no coincide exactamente con el instante dibujado
  const relojEn = async t => { await seekA(tiro.video, t); const c2 = document.createElement("canvas"); c2.width = W; c2.height = 8; const g2 = c2.getContext("2d"); g2.drawImage(tiro.video, 0, 0, W, H, 0, 0, W, H); const d = g2.getImageData(0, 2, W, 1).data; let n = 0; while (n < W && d[n * 4] > 200 && d[n * 4 + 1] < 80 && d[n * 4 + 2] > 200) n++; return n / 200; };
  const offs = []; for (const tv of [0.5, 1.0, 1.5, 2.0]) offs.push(tv - await relojEn(tv)); offs.sort((a, b) => a - b);
  const off = (offs[1] + offs[2]) / 2, visibleV = tv => visible(tv - off);
  const r = tiro.res, P = tiro.puntos.filter(q => q.auto);
  const tAt = (-vy0 - Math.sqrt(vy0 * vy0 + 4 * 4.905 * y0)) / (-2 * 4.905), dReal = vx0 * tAt;
  const aReal = (() => { const a = -4.905 / vx0 ** 2, bb = vy0 / vx0; return a * dReal ** 3 / 3 + bb * dReal ** 2 / 2 + y0 * dReal; })();
  // posiciones inventadas: puntos automáticos en instantes en que el balón no se veía
  const inventados = P.filter(q => !q.manual && !visibleV(q.t)).map(q => +q.t.toFixed(2));
  const L = tiro.linea || [], sin = typeof intervalosSin === "function" ? intervalosSin() : [];
  return {
    pidioClic, off: +off.toFixed(3), msg: tiro.seg.msg, segundos: +((performance.now() - tIni) / 1000).toFixed(1),
    cubierto: L.length ? [+L[0].t.toFixed(2), +L[L.length - 1].t.toFixed(2)] : null, dur: +tiro.video.duration.toFixed(2),
    cuadros: L.length, conBalon: L.filter(e => e.e === "ok" || e.e === "dudoso").length, sinDeteccion: sin.map(s => [+s.a.toFixed(2), +s.b.toFixed(2)]),
    posiciones: P.length, enAjuste: P.filter(q => !q.fuera && !q.atipico).length, inventados,
    primera: P.length ? +P[0].t.toFixed(2) : null, ultima: P.length ? +P[P.length - 1].t.toFixed(2) : null,
    tramo: tiro.tramo ? [+tiro.tramo.a.toFixed(2), +tiro.tramo.b.toFixed(2)] : null,
    area: r && +r.area.toFixed(3), areaReal: +aReal.toFixed(3), errArea: r && +(Math.abs(r.area - aReal) / aReal * 100).toFixed(2),
    vx: r && r.tiempo && +Math.abs(r.tiempo.vx).toFixed(2), g: r && r.tiempo && r.tiempo.g && +r.tiempo.g.toFixed(2), calidad: r && typeof calidadMedicion === "function" ? calidadMedicion(r).nivel : null
  };
};
