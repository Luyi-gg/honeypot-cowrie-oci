"""
monitor.py
----------
Script principal del honeypot. Monitorea el archivo de logs de Cowrie
en tiempo real y coordina las alertas de Telegram y los reportes a AbuseIPDB.

Uso:
    python3 src/monitor.py

Recomendado: ejecutar dentro de un screen o tmux para que persista
en segundo plano aunque se cierre la sesion SSH.

    screen -S honeypot
    python3 src/monitor.py
    (Ctrl+A, D para desconectar el screen sin detener el proceso)
"""

import os
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

from log_parser import parse_line, is_login_event, is_command_event, is_successful_login
from telegram_alert import send_alert
from abuseipdb_report import report_ip, get_reported_count

# Cargar variables de entorno desde .env
load_dotenv()

# Ruta al archivo de logs de Cowrie definida en .env
COWRIE_LOG_PATH = os.getenv(
    "COWRIE_LOG_PATH",
    # Valor por defecto si no esta definido en .env
    "/home/cowrie/cowrie/var/log/cowrie/cowrie.json"
)


class CowrieLogHandler(FileSystemEventHandler):
    """
    Manejador de eventos del sistema de archivos.
    Watchdog llama a on_modified() cada vez que el archivo de logs cambia,
    es decir, cada vez que Cowrie escribe un nuevo evento.
    """

    def __init__(self, log_path: str):
        self.log_path = log_path

        # Abrir el archivo y moverse al final para leer solo eventos nuevos
        # Si abriéramos desde el principio procesariamos todos los logs historicos
        self._file = open(self.log_path, "r", encoding="utf-8")
        self._file.seek(0, 2)  # 0 bytes desde el final del archivo

        print(f"[MONITOR] Escuchando eventos en: {self.log_path}")
        print(f"[MONITOR] Honeypot activo. En espera de conexiones...")

    def on_modified(self, event):
        """
        Se ejecuta automaticamente cuando Cowrie escribe nuevas lineas al log.
        Lee solo las lineas nuevas desde donde se quedo la ultima vez.
        """
        # Ignorar eventos de otros archivos en el mismo directorio
        if event.src_path != self.log_path:
            return

        # Leer todas las lineas nuevas escritas desde la ultima lectura
        new_lines = self._file.readlines()

        for line in new_lines:
            self._process_line(line)

    def _process_line(self, line: str):
        """
        Procesa una linea nueva del log de Cowrie.
        Decide si debe enviar alerta y/o reportar la IP segun el tipo de evento.
        """
        # Parsear la linea JSON en un diccionario estructurado
        event = parse_line(line)

        # Si la linea no es un evento relevante, ignorarla
        if event is None:
            return

        src_ip = event.get("src_ip", "N/A")
        event_type = event.get("event_type", "N/A")
        dst_port = event.get("dst_port", "N/A")

        print(f"[EVENTO] {event_type} | IP: {src_ip} | Puerto: {dst_port}")

        # Solo reportar a AbuseIPDB en eventos de login (no en cada comando)
        # Esto evita spam a la API por sesiones largas del mismo atacante
        reported = False
        if is_login_event(event):
            reported = report_ip(event)

        # Enviar alerta de Telegram para:
        # - Todos los intentos de login (exitosos o fallidos)
        # - Logins exitosos: el atacante entro al honeypot (evento critico)
        # - Comandos ejecutados: solo si el login fue exitoso
        if is_login_event(event) or is_successful_login(event) or is_command_event(event):
            send_alert(event, reported_to_abuseipdb=reported)

        # Mostrar estadisticas de la sesion actual en consola
        print(f"[STATS] IPs reportadas a AbuseIPDB esta sesion: {get_reported_count()}")


def main():
    """
    Punto de entrada principal. Configura el observador de archivos
    y mantiene el proceso corriendo indefinidamente.
    """
    # Verificar que el archivo de logs existe antes de iniciar
    if not os.path.exists(COWRIE_LOG_PATH):
        print(f"[ERROR] No se encontro el archivo de logs en: {COWRIE_LOG_PATH}")
        print("[ERROR] Verifica que Cowrie este corriendo y la ruta en .env sea correcta")
        return

    # Crear el manejador que procesara los eventos del log
    handler = CowrieLogHandler(COWRIE_LOG_PATH)

    # Watchdog observa el directorio que contiene el archivo de logs
    # Es mas eficiente que leer el archivo repetidamente con un loop (polling)
    observer = Observer()
    observer.schedule(
        handler,
        path=os.path.dirname(COWRIE_LOG_PATH),
        recursive=False  # No necesitamos monitorear subdirectorios
    )

    observer.start()
    print("[MONITOR] Observador iniciado. Presiona Ctrl+C para detener.")

    try:
        # Mantener el proceso vivo mientras el observador trabaja en segundo plano
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Detener limpiamente al presionar Ctrl+C
        print("\n[MONITOR] Deteniendo observador...")
        observer.stop()

    # Esperar a que el hilo del observador termine completamente
    observer.join()
    print("[MONITOR] Monitor detenido correctamente.")


if __name__ == "__main__":
    main()
