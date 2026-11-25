"""Imágenes de «Cómo funciona» (portada de pagina_interactiva.html).

Cada una toma una foto real del proyecto (img/) y le dibuja encima el paso del análisis
que explica: escala, detección, seguimiento, ajuste, integral, velocidades, resultado y confianza.
Uso:  python figuras/generar_como_funciona.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
IMG = RAIZ / "img"
W, H = 960, 540
VERDE, CIAN, ROJO, BLANCO, NOCHE = (184, 255, 74), (40, 169, 255), (255, 77, 94), (242, 245, 250), (8, 13, 22)


def fuente(nombre, t):
    for n in (nombre, "segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{n}", t)
        except OSError:
            pass
    return ImageFont.load_default()


MONO, TIT, TXT = fuente("consolab.ttf", 22), fuente("segoeuib.ttf", 30), fuente("segoeui.ttf", 20)


def encajar(nombre, oscuro=0.35):
    """La foto completa a lo alto, centrada, sobre una versión desenfocada de sí misma."""
    im = Image.open(IMG / nombre).convert("RGB")
    fondo, _ = base(nombre, (im.width / 2, im.height / 2), 1.0, 0.7)
    fondo = fondo.filter(ImageFilter.GaussianBlur(18))
    esc = H / im.height
    fr = Image.blend(im.resize((round(im.width * esc), H), Image.LANCZOS), Image.new("RGB", (round(im.width * esc), H), NOCHE), oscuro)
    ox = (W - fr.width) // 2
    fondo.paste(fr, (ox, 0))
    return fondo, (lambda px, py: (ox + px * esc, py * esc))


def base(nombre, foco, zoom=1.0, oscuro=0.45):
    """Recorta la foto a 16:9 centrando el punto `foco` (en píxeles de la foto original)."""
    im = Image.open(IMG / nombre).convert("RGB")
    esc = max(W / im.width, H / im.height) * zoom
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    fx, fy = foco[0] * esc, foco[1] * esc
    x = min(max(0, fx - W / 2), im.width - W)
    y = min(max(0, fy - H / 2), im.height - H)
    im = im.crop((round(x), round(y), round(x) + W, round(y) + H))
    velo = Image.new("RGB", (W, H), NOCHE)
    im = Image.blend(im, velo, oscuro)
    return im, (lambda px, py: (px * esc - x, py * esc - y))


def etiqueta(d, xy, texto, color=VERDE, f=MONO):
    x, y = xy
    caja = d.textbbox((x, y), texto, font=f)
    d.rounded_rectangle((caja[0] - 8, caja[1] - 6, caja[2] + 8, caja[3] + 6), 6, fill=NOCHE + (215,))
    d.text((x, y), texto, font=f, fill=color)


def titulo(d, n, texto):
    etiqueta(d, (28, H - 64), f"{n:02d}  {texto}", BLANCO, TIT)


def circulo(d, c, r, color, w=4):
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), outline=color, width=w)


def parabola(x0, x1, ysuelo, alto):
    xm = (x0 + x1) / 2
    return lambda x: ysuelo - alto * (1 - ((x - xm) / ((x1 - x0) / 2)) ** 2)


def guardar(im, nombre):
    im.save(IMG / nombre, quality=84, optimize=True, progressive=True)
    print("ok", nombre)


# 1 · calibrar: el balón mide 22 cm y eso fija la escala
im, P = base("messi-disparo.jpg", (282, 160), 1.0, 0.35)
d = ImageDraw.Draw(im, "RGBA")
b = P(282, 207); r = 26
circulo(d, b, r, VERDE)
d.line((b[0] - r, b[1] + r + 18, b[0] + r, b[1] + r + 18), fill=VERDE, width=3)
for xx in (b[0] - r, b[0] + r):
    d.line((xx, b[1] + r + 10, xx, b[1] + r + 26), fill=VERDE, width=3)
etiqueta(d, (b[0] - 180, b[1] + r + 40), "diámetro = 22 cm  →  m = 0,22 / d_px")
titulo(d, 1, "Calibrar la escala")
guardar(im, "como-1-calibrar.jpg")

# 2 · detectar: candidatos redondos; gana el que está quieto sobre el césped
im, P = base("cr7-chilena.jpg", (700, 300), 1.0, 0.4)
d = ImageDraw.Draw(im, "RGBA")
b = P(334, 83)
circulo(d, b, 34, VERDE, 5); etiqueta(d, (b[0] + 44, b[1] - 14), "1  balón · redondo y aislado")
for k, (px, py) in enumerate([(520, 420), (930, 640)], start=2):
    q = P(px, py); circulo(d, q, 30, ROJO, 3); etiqueta(d, (q[0] + 38, q[1] - 12), f"{k}  descartado", ROJO)
titulo(d, 2, "Detectar el balón")
guardar(im, "como-2-detectar.jpg")

# 3 · seguir: ventana de búsqueda alrededor de la posición prevista
im, P = base("cr7-chilena-2.jpg", (300, 0), 1.0, 0.4)
d = ImageDraw.Draw(im, "RGBA")
b = P(246, 51); s = 92
d.rectangle((b[0] - s, b[1] - s * .7, b[0] + s, b[1] + s * .7), outline=CIAN, width=3)
for i in range(1, 6):
    gx = b[0] - s + i * 2 * s / 6; d.line((gx, b[1] - s * .7, gx, b[1] + s * .7), fill=CIAN + (70,), width=1)
    gy = b[1] - s * .7 + i * 1.4 * s / 6; d.line((b[0] - s, gy, b[0] + s, gy), fill=CIAN + (70,), width=1)
circulo(d, b, 24, VERDE, 4)
etiqueta(d, (b[0] + s + 14, b[1] - 40), "ventana de búsqueda", CIAN)
etiqueta(d, (b[0] + s + 14, b[1] - 4), "mínimo ZSSD → posición subpíxel")
titulo(d, 3, "Seguir cuadro a cuadro")
guardar(im, "como-3-seguir.jpg")

# 4 · ajustar: las posiciones de la toma aérea (la línea punteada real) y su parábola de mínimos cuadrados
im, P = encajar("messi-aerea.jpg", 0.3)
d = ImageDraw.Draw(im, "RGBA")
med = [(140, 252), (110, 238), (80, 215), (58, 185), (42, 150), (38, 115), (42, 80), (55, 50)]
n = len(med); ys = [p[1] for p in med]; xs = [p[0] for p in med]
# x = a·y² + b·y + c por ecuaciones normales
S = lambda k: sum(y ** k for y in ys); T = lambda k: sum(x * y ** k for x, y in zip(xs, ys))
A = [[S(4), S(3), S(2)], [S(3), S(2), S(1)], [S(2), S(1), n]]; B = [T(2), T(1), T(0)]
for i in range(3):
    for j in range(i + 1, 3):
        f = A[j][i] / A[i][i]; A[j] = [u - f * v for u, v in zip(A[j], A[i])]; B[j] -= f * B[i]
c = B[2] / A[2][2]; b = (B[1] - A[1][2] * c) / A[1][1]; a = (B[0] - A[0][1] * b - A[0][2] * c) / A[0][0]
d.line([P(a * y * y + b * y + c, y) for y in range(46, 256, 3)], fill=VERDE, width=5, joint="curve")
for x, y in med:
    q = P(x, y); circulo(d, q, 9, BLANCO, 3); d.ellipse((q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3), fill=ROJO)
etiqueta(d, (W - 300, 40), "8 posiciones medidas")
etiqueta(d, (W - 300, 80), "x = ay² + by + c")
etiqueta(d, (W - 300, 120), "mínimos cuadrados")
titulo(d, 4, "Ajustar la parábola")
guardar(im, "como-4-ajustar.jpg")

# 5 · integrar: área bajo la trayectoria como suma de Riemann → TFC
im, P = base("hero-chilena.jpg", (1100, 700), 1.0, 0.5)
d = ImageDraw.Draw(im, "RGBA")
x0, x1, ys = 90, W - 90, H - 70
f = parabola(x0, x1, ys, 300)
n = 14; dx = (x1 - x0) / n
for i in range(n):
    xm = x0 + (i + .5) * dx
    d.rectangle((x0 + i * dx + 2, f(xm), x0 + (i + 1) * dx - 2, ys), fill=VERDE + (45,), outline=VERDE + (150,), width=1)
d.line([(x, f(x)) for x in range(x0, x1 + 1, 6)], fill=VERDE, width=5)
d.line((x0 - 20, ys, x1 + 20, ys), fill=BLANCO + (160,), width=2)
etiqueta(d, (x0 + 40, ys - 120), "A = ∫ y dx = F(d) − F(0)")
titulo(d, 5, "Calcular la integral")
guardar(im, "como-5-integral.jpg")

# 6 · velocidades: derivadas de x(t) y y(t)
im, P = base("messi-gol.jpg", (213, 120), 1.0, 0.45)
d = ImageDraw.Draw(im, "RGBA")
x0, x1, ys = 120, W - 140, H - 90
f = parabola(x0, x1, ys, 280)
d.line([(x, f(x)) for x in range(x0, x1 + 1, 6)], fill=BLANCO + (180,), width=3)
for x in (x0 + 90, (x0 + x1) / 2, x1 - 120):
    h = 0.0001; pend = (f(x + h) - f(x - h)) / (2 * h); y = f(x)
    d.line((x, y, x + 90, y), fill=CIAN, width=4)                 # vx
    d.line((x, y, x, y + pend * 90), fill=ROJO, width=4)          # vy
    d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=BLANCO)
etiqueta(d, (W - 360, 90), "vₓ = dx/dt", CIAN); etiqueta(d, (W - 360, 130), "v_y = dy/dt", ROJO)
etiqueta(d, (W - 360, 170), "g = −2c₂")
titulo(d, 6, "Velocidad y gravedad")
guardar(im, "como-6-velocidad.jpg")

# 7 · en vivo: la estela del balón hasta el ángulo del arco y la integral acumulada
im, P = encajar("messi-gol-2.jpg", 0.3)
d = ImageDraw.Draw(im, "RGBA")
tray = [(0, 200), (20, 168), (40, 143), (60, 125), (80, 113), (100, 108), (120, 110), (140, 118), (152, 127)]
q = [P(*p) for p in tray]
d.polygon(q + [P(152, 262), P(0, 262)], fill=VERDE + (40,))
d.line(q, fill=VERDE, width=4, joint="curve")
for k, p in enumerate(q):
    d.ellipse((p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8), fill=VERDE + (90 + 20 * k,))
etiqueta(d, (W - 330, 40), "estela del balón")
etiqueta(d, (W - 330, 80), "A(t) crece con cada cuadro")
titulo(d, 7, "Ver el resultado en vivo")
guardar(im, "como-7-en-vivo.jpg")

# 8 · confianza: los criterios que califican la medición
im, P = base("metodo-formulas.jpg", (700, 420), 1.0, 0.55)
d = ImageDraw.Draw(im, "RGBA")
crit = ["Tamaño del balón en píxeles", "R² del ajuste", "Número de posiciones", "Movimiento de la cámara", "Toma lateral o de frente"]
for i, c in enumerate(crit):
    y = 130 + i * 62
    d.rounded_rectangle((60, y, 560, y + 46), 10, fill=NOCHE + (220,), outline=(34, 50, 75), width=2)
    d.text((80, y + 10), c, font=TXT, fill=BLANCO)
etiqueta(d, (620, 230), "alta · media · baja", VERDE, TIT)
titulo(d, 8, "Qué tan confiable es")
guardar(im, "como-8-confianza.jpg")
