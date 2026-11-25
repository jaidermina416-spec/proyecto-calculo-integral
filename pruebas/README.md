# Pruebas de validación del seguimiento

Requisitos: `npm i playwright` y Google Chrome instalado (las pruebas abren Chrome sin ventana).

## 1. Análisis del video completo (videos con la verdad conocida)

`generar_videos_prueba.py` crea cuatro videos MP4 (H.264, 30 cuadros por segundo exactos) con física conocida y un JSON
con la posición real del balón en cada cuadro y si se ve o no:

| Video | Qué prueba |
| --- | --- |
| `prueba_completo.mp4` | balón visible desde el inicio: disparo, vuelo, bote, rodamiento y parada |
| `prueba_aparece_tarde.mp4` | cancha vacía hasta 0,8 s; el balón aparece tarde |
| `prueba_tapado.mp4` | un jugador fijo tapa el balón en pleno vuelo (0,95–1,20 s) |
| `prueba_tarde_y_tapado.mp4` | las dos cosas a la vez |

    python pruebas/generar_videos_prueba.py        # escribe en "videos prueba/sinteticos/" (pip install numpy pillow imageio-ffmpeg)
    node pruebas/prueba_video_completo.js          # o solo algunos: node pruebas/prueba_video_completo.js tapado

La prueba pulsa «Analizar el video completo» y comprueba que se recorre el video entero, que **no hay posiciones
inventadas** en cuadros donde el balón no se ve, que los intervalos sin detección coinciden con la verdad, que las
posiciones caen a pocos píxeles de la real y que el área se parece a la real. `DET=1` imprime el error de cada posición.

## 2. Seguimiento con cámara en movimiento (videos generados en el navegador)

Generan videos sintéticos con física conocida (tiro parabólico, g = 9,81 m/s²), los cargan en la página y comparan el
área, vₓ y g medidas con las reales:

    node pruebas/validacion.js "[{}, {pan:80}, {zoom:0.25}, {pan:60,zoom:0.2}, {rb:6}, {color:'#000000'}]"

Opciones de cada caso: `pan` (px/s), `zoom` (1/s), `rb` (radio del balón en px), `color`, `cesped`, `ruido`.
`prueba_completa.js` es la versión en el navegador de la prueba 1 (aparición tardía y balón tapado); sus videos salen
de MediaRecorder, cuyos tiempos no son regulares, así que para medir errores conviene la prueba 1.

## 3. Videos reales

    node pruebas/video_real.js "roberto carlos.mp4" 0 100

analiza un video de `videos prueba/` con Chrome (H.264) e imprime la bitácora.
