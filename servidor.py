import http.server
import os
import socketserver
import threading
import webbrowser

PUERTO = 8000
PAGINA = "pagina_interactiva.html"

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Servidor(socketserver.TCPServer):
    allow_reuse_address = True


class Manejador(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


with Servidor(("", PUERTO), Manejador) as servidor:
    url = f"http://localhost:{PUERTO}/{PAGINA}"
    print("Presiona Ctrl + C para detenerlo")
    print(f"Servidor activo en {url}")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido")
