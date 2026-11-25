"""Figuras en fondo blanco para el informe final (APA 7). Salida: figuras/informe/."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SALIDA = os.path.join(os.path.dirname(__file__), "informe")
os.makedirs(SALIDA, exist_ok=True)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 12, "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL, ROJO, GRIS = "#1f4e9c", "#b3261e", "#555555"
G = 9.81

c_m = np.polyfit([0, 9.15, 27.4], [0, 2.40, 2.30], 2)
A2 = -G / (2 * 20 ** 2)
B2 = (0.60 - 2.38 - A2 * 11 ** 2) / 11
c_r = np.array([A2, B2, 2.38])


def guardar(nombre):
    coma = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    for eje in plt.gcf().axes:
        if eje.name != "3d":
            eje.xaxis.set_major_formatter(coma)
            eje.yaxis.set_major_formatter(coma)
    plt.tight_layout()
    plt.savefig(os.path.join(SALIDA, nombre), dpi=200)
    plt.close()


# 1. Región bajo la trayectoria de Messi
x = np.linspace(0, 27.4, 400)
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.fill_between(x, np.polyval(c_m, x), color=AZUL, alpha=0.18, label="Región R: A = 65,02 m²")
ax.plot(x, np.polyval(c_m, x), color=AZUL, lw=2.2, label="y(x) = −0,00977x² + 0,35172x")
ax.plot([0, 9.15, 27.4], [0, 2.40, 2.30], "o", color="black", label="Puntos medidos")
ax.plot([9.15, 9.15], [0, 1.85], color=GRIS, lw=6, alpha=0.6, label="Barrera (9,15 m)")
ax.plot([27.4, 27.4], [0, 2.44], color="black", lw=3, label="Arco (2,44 m)")
ax.set_xlabel("Distancia horizontal x (m)")
ax.set_ylabel("Altura y (m)")
ax.set_xlim(0, 28.5)
ax.set_ylim(0, 3.8)
ax.legend(loc="upper left", fontsize=9, ncol=2, frameon=False)
guardar("fig1_region_messi.png")

# 2. Suma de Riemann (punto medio, n = 14)
n = 14
dx = 27.4 / n
xm = np.arange(n) * dx + dx / 2
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.bar(xm, np.polyval(c_m, xm), width=dx, color=AZUL, alpha=0.25, edgecolor=AZUL, label=f"Suma de Riemann, n = {n}: 65,10 m²")
ax.plot(x, np.polyval(c_m, x), color=AZUL, lw=2.2, label="Integral exacta (TFC): 65,02 m²")
ax.set_xlabel("Distancia horizontal x (m)")
ax.set_ylabel("Altura y (m)")
ax.set_ylim(0, 3.8)
ax.legend(loc="upper left", fontsize=9, frameon=False)
guardar("fig2_riemann.png")

# 3. Área entre las dos trayectorias (últimos 11 m antes del arco)
s = np.linspace(0, 11, 300)
yM = np.polyval(c_m, 27.4 - s)
yR = np.polyval(c_r, 11 - s)
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.fill_between(s, yR, yM, color=GRIS, alpha=0.18, label="Área entre curvas: 12,98 m²")
ax.plot(s, yM, color=AZUL, lw=2.2, label="Messi, tiro libre (2019)")
ax.plot(s, yR, color=ROJO, lw=2.2, ls="--", label="Cristiano, chilena (2018)")
ax.set_xlabel("Distancia al arco s (m)")
ax.set_ylabel("Altura (m)")
ax.invert_xaxis()
ax.set_ylim(0, 3.2)
ax.legend(loc="lower left", fontsize=9, frameon=False)
guardar("fig3_entre_curvas.png")

# 4. Balón de fútbol por el método de discos (3D)
r = 69 / (2 * np.pi)
fig = plt.figure(figsize=(6, 5))
ax = fig.add_subplot(111, projection="3d")
th = np.linspace(0, 2 * np.pi, 50)
nd = 10
d = 2 * r / nd
for i in range(nd):
    x0, x1 = -r + i * d + d * 0.06, -r + (i + 1) * d - d * 0.06
    ri = np.sqrt(max(r ** 2 - ((x0 + x1) / 2) ** 2, 0))
    X, T = np.meshgrid([x0, x1], th)
    col = "#9ec3ec" if i % 2 else "#d6e6f7"
    ax.plot_surface(X, ri * np.cos(T), ri * np.sin(T), color=col, alpha=1, shade=True, lightsource=matplotlib.colors.LightSource(315, 45), edgecolor="none")
    for xx in (x0, x1):
        P, T2 = np.meshgrid(np.linspace(0, ri, 2), th)
        ax.plot_surface(np.full_like(P, xx), P * np.cos(T2), P * np.sin(T2), color=col, alpha=1, shade=False, edgecolor="none")
        ax.plot(np.full_like(th, xx), ri * np.cos(th), ri * np.sin(th), color=AZUL, lw=0.8)
u = np.linspace(-r, r, 40)
U, V = np.meshgrid(u, th)
R = np.sqrt(np.clip(r ** 2 - U ** 2, 0, None))
ax.plot_wireframe(U, R * np.cos(V), R * np.sin(V), color=GRIS, linewidth=0.3, alpha=0.35, rstride=4, cstride=4)
ax.plot([-r * 1.4, r * 1.4], [0, 0], [0, 0], color="black", lw=1.2)
ax.text(r * 1.45, 0, 0, "x", fontsize=13)
ax.view_init(elev=18, azim=-55)
ax.set_box_aspect((1.3, 1, 1))
ax.set_axis_off()
ruta = os.path.join(SALIDA, "fig4_discos_balon.png")
plt.savefig(ruta, dpi=200, bbox_inches="tight", pad_inches=0.05)
plt.close()
from PIL import Image, ImageChops
im = Image.open(ruta).convert("RGB")
caja = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
im.crop((caja[0] - 20, caja[1] - 20, caja[2] + 20, caja[3] + 20)).save(ruta)

# 5. Perfil del balón de rugby: elipse frente a parábola
a, b = 14.5, 60 / (2 * np.pi)
xx = np.linspace(-a, a, 400)
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot(xx, b * np.sqrt(1 - xx ** 2 / a ** 2), color=AZUL, lw=2.2, label="Elipse: V = 5 538,59 cm³")
ax.plot(xx, -b * np.sqrt(1 - xx ** 2 / a ** 2), color=AZUL, lw=2.2)
ax.plot(xx, b * (1 - xx ** 2 / a ** 2), color=ROJO, lw=2.2, ls="--", label="Parábola: V = 4 430,87 cm³")
ax.plot(xx, -b * (1 - xx ** 2 / a ** 2), color=ROJO, lw=2.2, ls="--")
ax.axhline(0, color="black", lw=0.8)
ax.set_aspect("equal")
ax.set_xlabel("x (cm), eje de giro")
ax.set_ylabel("y (cm)")
ax.legend(loc="upper right", fontsize=9, frameon=False)
guardar("fig5_perfil_rugby.png")

# 6. Crecimiento del volumen al inflar el balón
rr = np.linspace(0, r, 200)
fig, ax1 = plt.subplots(figsize=(8, 3.8))
ax1.plot(rr, 4 / 3 * np.pi * rr ** 3 / 1000, color=AZUL, lw=2.2, label="V(r) = ∫₀ʳ 4πs² ds (L)")
m = rr >= 0.9 * r
ax1.fill_between(rr[m], 4 / 3 * np.pi * rr[m] ** 3 / 1000, color=AZUL, alpha=0.18, label="Último 10 % del radio: 27,1 % del aire")
ax1.set_xlabel("Radio r (cm)")
ax1.set_ylabel("Volumen (L)")
ax2 = ax1.twinx()
ax2.plot(rr, 4 * np.pi * rr ** 2, color=ROJO, lw=1.8, ls="--", label="dV/dr = 4πr² (cm²)")
ax2.set_ylabel("dV/dr (cm²)")
ax2.grid(False)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=9, frameon=False)
guardar("fig6_crecimiento.png")
print("Figuras en", SALIDA)
