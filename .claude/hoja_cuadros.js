// Ayuda de pruebas: muestra varios cuadros de un video en una hoja de contacto superpuesta.
window.hoja2 = async (src, times, cols = 2, tw = 800) => {
  const v = document.createElement("video"); v.muted = true; v.src = src; v.preload = "auto";
  await new Promise(r => v.addEventListener("loadeddata", r, { once: true }));
  const th = Math.round(tw * v.videoHeight / v.videoWidth);
  const sh = document.createElement("canvas"); sh.width = cols * tw; sh.height = Math.ceil(times.length / cols) * th;
  const g = sh.getContext("2d");
  for (let i = 0; i < times.length; i++) {
    await new Promise(r => { v.addEventListener("seeked", r, { once: true }); v.currentTime = times[i]; });
    g.drawImage(v, (i % cols) * tw, Math.floor(i / cols) * th, tw, th);
    g.fillStyle = "#ff0"; g.font = "bold 22px sans-serif"; g.fillText(times[i].toFixed(2) + "s", (i % cols) * tw + 8, Math.floor(i / cols) * th + 28);
  }
  document.getElementById("hoja")?.remove(); sh.id = "hoja";
  sh.style.cssText = "position:fixed;left:0;top:0;z-index:9999;width:100vw;height:auto;background:#000";
  sh.onclick = () => sh.remove();
  document.body.appendChild(sh);
  return "ok";
};
