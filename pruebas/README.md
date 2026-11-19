# Pruebas de validación del seguimiento

Generan videos sintéticos con física conocida (tiro parabólico, g = 9,81 m/s²), los cargan en la página y comparan el
área, vₓ y g medidas con las reales. Requisitos: `npm i playwright` y `npx playwright install chromium`.

    node pruebas/validacion.js "[{}, {pan:80}, {zoom:0.25}, {pan:60,zoom:0.2}, {rb:6}, {color:'#000000'}]"

Opciones de cada caso: `pan` (px/s), `zoom` (1/s), `rb` (radio del balón en px), `color`, `cesped`, `ruido`.
`node pruebas/video_real.js "roberto carlos.mp4" 0 100` analiza un video de `videos prueba/` con Chrome (H.264).
