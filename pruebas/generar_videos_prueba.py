"""Genera videos sintéticos de prueba (MP4 H.264 a 30 cuadros por segundo exactos) con física conocida.

Cada video trae un JSON con la verdad de cada cuadro (instante, posición del balón, si se ve) y el área real,
para comprobar que el análisis cubre el video completo, no inventa posiciones donde el balón no se ve y mide bien.

Uso:  python pruebas/generar_videos_prueba.py            (escribe en "videos prueba/sinteticos/")
Requiere: pip install numpy pillow imageio-ffmpeg
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import imageio_ffmpeg

W, H, FPS = 1280, 720, 30
SUELO, K, RB = 650, 100.0, 11          # línea del césped (px), píxeles por metro, radio del balón (px) → 22 cm = 22 px
G = 9.81

CASOS = {
    # balón visible desde el inicio, quieto; disparo, vuelo, bote, rodamiento y parada
    "completo": dict(dur=3.0, aparece=0.0, disparo=0.5),
    # cancha vacía: el balón aparece (quieto) a los 0,8 s y el disparo llega a los 1,2 s
    "aparece_tarde": dict(dur=3.4, aparece=0.8, disparo=1.2),
    # un jugador fijo tapa el balón en pleno vuelo entre 0,95 s y 1,20 s
    "tapado": dict(dur=3.0, aparece=0.0, disparo=0.5, tapado=(0.95, 1.20)),
    # las dos cosas: aparece tarde y luego queda tapado un momento
    "tarde_y_tapado": dict(dur=3.6, aparece=0.7, disparo=1.1, tapado=(1.55, 1.80)),
}


def posicion(u, vx0=7.0, vy0=6.5, y0=RB / K, x0=140.0, tau=0.15):
    """Centro del balón (px) a u segundos del disparo: parábola, y al tocar el césped rueda frenando hasta parar."""
    ul = 2 * vy0 / G  # vuelve a la altura de salida: el centro queda otra vez a un radio del césped (toca el suelo)
    if u <= 0:
        return x0, SUELO - y0 * K
    if u <= ul:
        y = y0 + vy0 * u - G * u * u / 2
        return x0 + vx0 * u * K, SUELO - y * K
    xl = x0 + vx0 * ul * K
    return xl + vx0 * K * tau * (1 - math.exp(-(u - ul) / tau)), SUELO - y0 * K


def area_real(vx0=7.0, vy0=6.5, y0=RB / K):
    """Área bajo la altura del centro, y(x) = y0 + (vy0/vx0)x − g x²/(2vx0²), de x = 0 hasta donde y = 0 (como el ajuste)."""
    a, b = -G / (2 * vx0 ** 2), vy0 / vx0
    d = (-b - math.sqrt(b * b - 4 * a * y0)) / (2 * a)
    return a * d ** 3 / 3 + b * d ** 2 / 2 + y0 * d, d


def fondo():
    rng = np.random.default_rng(7)
    im = Image.new("RGB", (W, H), (27, 43, 85))
    g = ImageDraw.Draw(im)
    # público: puntos de colores al azar (sin patrón periódico)
    for _ in range(900):
        x, y = rng.uniform(0, W), rng.uniform(40, SUELO - 140)
        h = rng.uniform(0, 1)
        col = tuple(int(c) for c in (np.array([0.35 + 0.3 * math.sin(6.28 * h), 0.35 + 0.3 * math.sin(6.28 * h + 2), 0.35 + 0.3 * math.sin(6.28 * h + 4)]) * 255))
        g.ellipse([x - 5, y - 5, x + 5, y + 5], fill=col)
    g.rectangle([0, SUELO - 110, W, H], fill=(30, 122, 62))      # césped
    for i in range(0, W, 160):                                     # franjas del césped
        g.rectangle([i, SUELO - 110, i + 80, H], fill=(34, 132, 68))
    g.line([(1220, SUELO), (1220, SUELO - 244)], fill=(221, 221, 221), width=8)  # poste
    return im


def generar(nombre, dur, aparece, disparo, tapado=None, carpeta=Path("videos prueba/sinteticos")):
    carpeta.mkdir(parents=True, exist_ok=True)
    base = fondo()
    caja = None
    if tapado:
        (xa, ya), (xb, yb) = posicion(tapado[0] - disparo), posicion(tapado[1] - disparo)
        m = RB + 4
        caja = (min(xa, xb) - m, min(ya, yb) - m - 30, max(xa, xb) + m, max(ya, yb) + m + 30)
    n = int(round(dur * FPS))
    verdad = []
    ruta = carpeta / f"prueba_{nombre}.mp4"
    w = imageio_ffmpeg.write_frames(str(ruta), (W, H), fps=FPS, codec="libx264", pix_fmt_out="yuv420p", quality=8, macro_block_size=16, output_params=["-g", "30"])
    w.send(None)
    for i in range(n):
        t = i / FPS
        im = base.copy()
        g = ImageDraw.Draw(im)
        x, y = posicion(t - disparo)
        presente = t >= aparece - 1e-9
        if presente:
            g.ellipse([x - RB, y - RB, x + RB, y + RB], fill=(255, 255, 255))
            g.ellipse([x - 7, y - 6, x + 1, y + 2], fill=(34, 34, 34))
        tapa = False
        if caja:
            g.rectangle(caja, fill=(58, 42, 26))
            g.rectangle([caja[0] + 8, caja[1] + 10, caja[2] - 8, caja[1] + 50], fill=(90, 26, 34))
            tapa = presente and x - RB >= caja[0] and x + RB <= caja[2] and y - RB >= caja[1] and y + RB <= caja[3]
        verdad.append({"t": round(t, 6), "x": round(x, 2), "y": round(y, 2), "visible": bool(presente and not tapa)})
        w.send(np.asarray(im, dtype=np.uint8).tobytes())
    w.close()
    area, d = area_real()
    info = {"video": ruta.name, "fps": FPS, "duracion": n / FPS, "aparece": aparece, "disparo": disparo, "tapado": tapado,
            "escala_px_por_m": K, "radio_px": RB, "area_real_m2": round(area, 4), "alcance_m": round(d, 4), "cuadros": verdad}
    (carpeta / f"prueba_{nombre}.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    print(f"{ruta}  {n} cuadros  {ruta.stat().st_size / 1e3:.0f} kB  área real {area:.3f} m²")


if __name__ == "__main__":
    nombres = sys.argv[1:] or list(CASOS)
    for k in nombres:
        generar(k, **CASOS[k])
