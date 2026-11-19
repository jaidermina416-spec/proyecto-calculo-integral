import os
import numpy as np
from scipy.integrate import quad
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

G = 9.81
CARPETA = "figuras"
os.makedirs(CARPETA, exist_ok=True)

FONDO = "#0b1020"
TEXTO = "#e8ecf4"
COLOR_MESSI = "#4f8cff"
COLOR_CR7 = "#ff5a5f"
COLOR_EXTRA = "#f5c542"

plt.rcParams.update({
    "figure.facecolor": FONDO,
    "axes.facecolor": FONDO,
    "axes.edgecolor": "#3a4566",
    "axes.labelcolor": TEXTO,
    "xtick.color": TEXTO,
    "ytick.color": TEXTO,
    "text.color": TEXTO,
    "grid.color": "#26304d",
    "font.size": 11,
})

ESFERICOS = {
    "Fútbol (UEFA Champions League)": {"circunferencia": 69.0, "jugadores": "Messi y Cristiano"},
    "Baloncesto (NBA, Wilson)": {"circunferencia": 74.9, "jugadores": "LeBron James y Stephen Curry"},
    "Voleibol (FIVB, Mikasa V200W)": {"circunferencia": 66.0, "jugadores": "Earvin Ngapeth y Wilfredo León"},
}

OVALADOS = {
    "Fútbol americano (NFL, Wilson The Duke)": {"largo": 11.25 * 2.54, "circ_corta": 21.0 * 2.54, "circ_larga": (71.1, 72.4), "jugadores": "Patrick Mahomes y Tom Brady"},
    "Rugby (World Rugby)": {"largo": 29.0, "circ_corta": 60.0, "circ_larga": (74.0, 77.0), "jugadores": "Antoine Dupont y Jonah Lomu"},
}


def radio(c):
    return c / (2 * np.pi)


def volumen_esfera_formula(r):
    return 4 / 3 * np.pi * r ** 3


def volumen_esfera_discos(r):
    return quad(lambda x: np.pi * (r ** 2 - x ** 2), -r, r)[0]


def volumen_esfera_cascarones(r):
    return quad(lambda x: 2 * np.pi * x * 2 * np.sqrt(r ** 2 - x ** 2), 0, r)[0]


def area_seccion(r):
    return quad(lambda x: 2 * np.sqrt(r ** 2 - x ** 2), -r, r)[0]


def perfil_elipse(a, b):
    return lambda x: b * np.sqrt(np.clip(1 - x ** 2 / a ** 2, 0, None))


def perfil_parabola(a, b):
    return lambda x: b * (1 - x ** 2 / a ** 2)


def volumen_revolucion(f, a):
    return quad(lambda x: np.pi * f(x) ** 2, -a, a)[0]


def perimetro_elipse(a, b):
    return quad(lambda t: np.sqrt(a ** 2 * np.sin(t) ** 2 + b ** 2 * np.cos(t) ** 2), 0, 2 * np.pi)[0]


def perimetro_parabola(a, b):
    return 2 * quad(lambda x: np.sqrt(1 + (2 * b * x / a ** 2) ** 2), -a, a)[0]


def ajustar_parabola(puntos):
    x = np.array([p[0] for p in puntos])
    y = np.array([p[1] for p in puntos])
    return np.polyfit(x, y, 2)


def integral_polinomio(c, x0, x1):
    a, b, k = c
    F = lambda x: a * x ** 3 / 3 + b * x ** 2 / 2 + k * x
    return F(x1) - F(x0)


print("=" * 70)
print("PARTE 1. BALONES ESFÉRICOS")
print("=" * 70)
resultados_esfericos = {}
for nombre, d in ESFERICOS.items():
    r = radio(d["circunferencia"])
    v_formula = volumen_esfera_formula(r)
    v_discos = volumen_esfera_discos(r)
    v_casc = volumen_esfera_cascarones(r)
    a_sec = area_seccion(r)
    resultados_esfericos[nombre] = (r, v_formula)
    print(f"\n{nombre} | {d['jugadores']}")
    print(f"  Radio: {r:.3f} cm")
    print(f"  Volumen analítico (4/3)πr³: {v_formula:,.2f} cm³ = {v_formula / 1000:.3f} L")
    print(f"  Volumen por discos (SciPy): {v_discos:,.2f} cm³ | error {abs(v_discos - v_formula) / v_formula * 100:.2e} %")
    print(f"  Volumen por cascarones (SciPy): {v_casc:,.2f} cm³ | error {abs(v_casc - v_formula) / v_formula * 100:.2e} %")
    print(f"  Área de la sección máxima: {a_sec:,.2f} cm² (πr² = {np.pi * r ** 2:,.2f})")

print("\n" + "=" * 70)
print("PARTE 2. BALONES OVALADOS: ELIPSE VS PARÁBOLA")
print("=" * 70)
resultados_ovalados = {}
for nombre, d in OVALADOS.items():
    a = d["largo"] / 2
    b = radio(d["circ_corta"])
    fe = perfil_elipse(a, b)
    fp = perfil_parabola(a, b)
    ve = volumen_revolucion(fe, a)
    vp = volumen_revolucion(fp, a)
    le = perimetro_elipse(a, b)
    lp = perimetro_parabola(a, b)
    lo, hi = d["circ_larga"]
    real = (lo + hi) / 2
    resultados_ovalados[nombre] = (a, b, ve, vp, le, lp, real)
    print(f"\n{nombre} | {d['jugadores']}")
    print(f"  Semieje a = {a:.3f} cm, radio máximo b = {b:.3f} cm")
    print(f"  Elipse:   V analítico (4/3)πab² = {4 / 3 * np.pi * a * b ** 2:,.2f} | SciPy {ve:,.2f} cm³")
    print(f"  Parábola: V analítico (16/15)πab² = {16 / 15 * np.pi * a * b ** 2:,.2f} | SciPy {vp:,.2f} cm³")
    print(f"  Circunferencia larga reglamento: {lo}–{hi} cm")
    print(f"  Circunferencia larga modelo elipse:   {le:.2f} cm | error {abs(le - real) / real * 100:.2f} %")
    print(f"  Circunferencia larga modelo parábola: {lp:.2f} cm | error {abs(lp - real) / real * 100:.2f} %")

print("\n" + "=" * 70)
print("PARTE 3. CRECIMIENTO: dV/dr = 4πr²")
print("=" * 70)
r_f = resultados_esfericos["Fútbol (UEFA Champions League)"][0]
aire_ultimo_10 = quad(lambda s: 4 * np.pi * s ** 2, 0.9 * r_f, r_f)[0]
aire_total = volumen_esfera_formula(r_f)
print(f"  Aire total del balón de fútbol: {aire_total:,.2f} cm³")
print(f"  Aire para pasar del 90% al 100% del radio: {aire_ultimo_10:,.2f} cm³ ({aire_ultimo_10 / aire_total * 100:.1f} %)")

print("\n" + "=" * 70)
print("PARTE 4. TRAYECTORIAS: MESSI VS CRISTIANO")
print("=" * 70)
D_MESSI = 27.4
puntos_messi = [(0.0, 0.0), (9.15, 2.40), (D_MESSI, 2.30)]
c_messi = ajustar_parabola(puntos_messi)

D_CR7 = 11.0
H_CR7 = 2.38
VX_CR7 = 20.0
A_CR7 = -G / (2 * VX_CR7 ** 2)
Y_FINAL_CR7 = 0.60
B_CR7 = (Y_FINAL_CR7 - H_CR7 - A_CR7 * D_CR7 ** 2) / D_CR7
c_cr7 = np.array([A_CR7, B_CR7, H_CR7])

vx_messi = np.sqrt(G / (-2 * c_messi[0]))
for nombre, c, d in [("Messi (Barcelona vs Liverpool, 1/05/2019)", c_messi, D_MESSI), ("Cristiano (Juventus vs Real Madrid, 3/04/2018)", c_cr7, D_CR7)]:
    a, b, k = c
    area_an = integral_polinomio(c, 0, d)
    area_num = quad(lambda x: np.polyval(c, x), 0, d)[0]
    xv = -b / (2 * a)
    yv = np.polyval(c, xv) if 0 <= xv <= d else max(np.polyval(c, 0), np.polyval(c, d))
    print(f"\n{nombre}")
    print(f"  y(x) = {a:.5f}x² {b:+.5f}x {k:+.3f}")
    print(f"  Área bajo la trayectoria (TFC): {area_an:.3f} m² | SciPy {area_num:.3f} m²")
    print(f"  Altura promedio (1/d)∫y dx: {area_an / d:.3f} m")
    print(f"  Altura máxima: {yv:.3f} m")
print(f"\n  Velocidad horizontal implícita del tiro de Messi: {vx_messi:.1f} m/s ({vx_messi * 3.6:.0f} km/h)")

yM = lambda s: np.polyval(c_messi, D_MESSI - s)
yR = lambda s: np.polyval(c_cr7, D_CR7 - s)
area_entre = quad(lambda s: yM(s) - yR(s), 0, D_CR7)[0]
print(f"  Área entre trayectorias en los últimos {D_CR7:.0f} m antes del arco: {area_entre:.3f} m²")

fig, ax = plt.subplots(figsize=(10, 6))
nombres = list(resultados_esfericos) + [f"{n}\n(elipse)" for n in resultados_ovalados]
vols = [v / 1000 for _, v in resultados_esfericos.values()] + [o[2] / 1000 for o in resultados_ovalados.values()]
colores = [COLOR_MESSI, COLOR_CR7, COLOR_EXTRA, "#7bd389", "#c792ea"]
barras = ax.barh([n.split(" (")[0] for n in nombres], vols, color=colores)
for bar, v in zip(barras, vols):
    ax.text(v + 0.08, bar.get_y() + bar.get_height() / 2, f"{v:.2f} L", va="center")
ax.set_xlabel("Volumen de aire (litros)")
ax.set_title("Volumen de los balones oficiales", fontsize=15, fontweight="bold")
ax.grid(axis="x", alpha=0.4)
plt.tight_layout()
plt.savefig(f"{CARPETA}/01_volumenes_balones.png", dpi=180)
plt.close()

for nombre, (a, b, ve, vp, le, lp, real) in resultados_ovalados.items():
    x = np.linspace(-a, a, 400)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(x, perfil_elipse(a, b)(x), color=COLOR_MESSI, lw=2.5, label=f"Elipse: V = {ve / 1000:.2f} L")
    ax.plot(x, -perfil_elipse(a, b)(x), color=COLOR_MESSI, lw=2.5)
    ax.plot(x, perfil_parabola(a, b)(x), color=COLOR_CR7, lw=2.5, ls="--", label=f"Parábola: V = {vp / 1000:.2f} L")
    ax.plot(x, -perfil_parabola(a, b)(x), color=COLOR_CR7, lw=2.5, ls="--")
    ax.set_aspect("equal")
    ax.set_xlabel("x (cm)")
    ax.set_ylabel("y (cm)")
    ax.set_title(f"Perfil: {nombre.split(' (')[0]}", fontsize=14, fontweight="bold")
    ax.legend(facecolor=FONDO, edgecolor="#3a4566")
    ax.grid(alpha=0.4)
    plt.tight_layout()
    archivo = "02_perfil_nfl.png" if "NFL" in nombre else "03_perfil_rugby.png"
    plt.savefig(f"{CARPETA}/{archivo}", dpi=180)
    plt.close()

r = r_f
u = np.linspace(0, 2 * np.pi, 60)
fig = plt.figure(figsize=(8, 7))
ax = fig.add_subplot(111, projection="3d")
ax.set_facecolor(FONDO)
n = 10
dx = 2 * r / n
cmap = plt.get_cmap("plasma")
for i in range(n):
    x0 = -r + i * dx + dx * 0.08
    x1 = -r + (i + 1) * dx - dx * 0.08
    xm = (x0 + x1) / 2
    ri = np.sqrt(max(r ** 2 - xm ** 2, 0))
    th = np.linspace(0, 2 * np.pi, 50)
    Xc, Tc = np.meshgrid([x0, x1], th)
    col = cmap(0.15 + 0.7 * i / (n - 1))
    ax.plot_surface(Xc, ri * np.cos(Tc), ri * np.sin(Tc), color=col, alpha=0.95, edgecolor="none", shade=True)
    for xx in (x0, x1):
        P, T = np.meshgrid(np.linspace(0, ri, 2), th)
        ax.plot_surface(np.full_like(P, xx), P * np.cos(T), P * np.sin(T), color=col, alpha=0.95, edgecolor="none", shade=True)
xs = np.linspace(-r, r, 60)
X, U = np.meshgrid(xs, u)
R = np.sqrt(np.clip(r ** 2 - X ** 2, 0, None))
ax.plot_wireframe(X, R * np.cos(U), R * np.sin(U), color="#8fa3d9", linewidth=0.3, alpha=0.35, rstride=4, cstride=4)
ax.view_init(elev=15, azim=-65)
ax.set_title("Balón de fútbol por el método de discos (n = 10)", fontsize=14, fontweight="bold")
ax.set_box_aspect((1, 1, 1))
ax.axis("off")
plt.tight_layout()
plt.savefig(f"{CARPETA}/04_solido_futbol_discos.png", dpi=180)
plt.close()

a, b = resultados_ovalados["Rugby (World Rugby)"][:2]
xs = np.linspace(-a, a, 80)
X, U = np.meshgrid(xs, u)
R = perfil_elipse(a, b)(X)
fig = plt.figure(figsize=(9, 6))
ax = fig.add_subplot(111, projection="3d")
ax.set_facecolor(FONDO)
ax.plot_surface(X, R * np.cos(U), R * np.sin(U), cmap="Oranges", alpha=0.9, edgecolor="none")
ax.set_title("Balón de rugby como elipsoide de revolución", fontsize=14, fontweight="bold")
ax.set_box_aspect((2 * a, 2 * b, 2 * b))
ax.axis("off")
plt.tight_layout()
plt.savefig(f"{CARPETA}/05_solido_rugby.png", dpi=180)
plt.close()

fig, ax = plt.subplots(figsize=(11, 5.5))
xm = np.linspace(0, D_MESSI, 300)
xr = np.linspace(0, D_CR7, 300)
ax.fill_between(D_MESSI - xm, np.polyval(c_messi, xm), color=COLOR_MESSI, alpha=0.25)
ax.plot(D_MESSI - xm, np.polyval(c_messi, xm), color=COLOR_MESSI, lw=3, label="Messi: tiro libre vs Liverpool (2019)")
ax.fill_between(D_CR7 - xr, np.polyval(c_cr7, xr), color=COLOR_CR7, alpha=0.25)
ax.plot(D_CR7 - xr, np.polyval(c_cr7, xr), color=COLOR_CR7, lw=3, label="Cristiano: chilena vs Juventus (2018)")
ax.plot([0, 0], [0, 2.44], color="white", lw=4)
ax.plot([D_MESSI - 9.15] * 2, [0, 1.85], color="#9aa4bf", lw=8, alpha=0.7, label="Barrera (9.15 m)")
ax.invert_xaxis()
ax.set_xlabel("Distancia al arco (m)")
ax.set_ylabel("Altura (m)")
ax.set_title("Área bajo la trayectoria: Messi vs Cristiano", fontsize=15, fontweight="bold")
ax.legend(facecolor=FONDO, edgecolor="#3a4566", loc="upper left")
ax.grid(alpha=0.4)
plt.tight_layout()
plt.savefig(f"{CARPETA}/06_trayectorias_messi_cristiano.png", dpi=180)
plt.close()

rr = np.linspace(0, r_f, 200)
fig, ax1 = plt.subplots(figsize=(10, 5.5))
ax1.plot(rr, volumen_esfera_formula(rr) / 1000, color=COLOR_MESSI, lw=3, label="V(r) = ∫₀ʳ 4πs² ds")
ax1.fill_between(rr[rr >= 0.9 * r_f], volumen_esfera_formula(rr[rr >= 0.9 * r_f]) / 1000, color=COLOR_EXTRA, alpha=0.35, label=f"Último 10% del radio = {aire_ultimo_10 / aire_total * 100:.1f}% del aire")
ax1.set_xlabel("Radio del balón (cm)")
ax1.set_ylabel("Volumen (L)")
ax2 = ax1.twinx()
ax2.plot(rr, 4 * np.pi * rr ** 2, color=COLOR_CR7, lw=2, ls="--", label="dV/dr = 4πr²")
ax2.set_ylabel("dV/dr (cm²)", color=COLOR_CR7)
ax1.set_title("Crecimiento del volumen al inflar el balón (TFC)", fontsize=15, fontweight="bold")
l1, n1 = ax1.get_legend_handles_labels()
l2, n2 = ax2.get_legend_handles_labels()
ax1.legend(l1 + l2, n1 + n2, facecolor=FONDO, edgecolor="#3a4566", loc="upper left")
ax1.grid(alpha=0.4)
plt.tight_layout()
plt.savefig(f"{CARPETA}/07_crecimiento_volumen.png", dpi=180)
plt.close()

print(f"\nFiguras guardadas en la carpeta '{CARPETA}'.")
