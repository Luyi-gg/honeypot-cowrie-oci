"""
abuseipdb_report.py
-------------------
Reporta IPs maliciosas a AbuseIPDB usando su API v2.
AbuseIPDB es una base de datos colaborativa donde la comunidad de seguridad
reporta IPs involucradas en actividad maliciosa. Los reportes de este honeypot
contribuyen a proteger a otros sistemas en Internet.

Documentacion oficial de la API: https://docs.abuseipdb.com/#report-endpoint
"""

import requests
import os
from dotenv import load_dotenv

# Cargar las variables definidas en el archivo .env
load_dotenv()

# API Key de AbuseIPDB desde variables de entorno
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")

# Endpoint oficial de reporte de AbuseIPDB v2
ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/report"

# Categoria de AbuseIPDB para ataques SSH/Telnet de fuerza bruta
# Categoria 18 = Brute-Force (intentos repetidos de autenticacion)
# Categoria 22 = SSH (especifico para ataques sobre protocolo SSH)
# Referencia completa: https://www.abuseipdb.com/categories
CATEGORY_BRUTE_FORCE = 18
CATEGORY_SSH = 22

# Conjunto en memoria para evitar reportar la misma IP multiples veces por sesion
# Esto respeta las politicas de uso de AbuseIPDB y evita spam a su API
_already_reported: set = set()


def build_comment(event: dict) -> str:
    """
    Construye el comentario que se envia junto al reporte.
    AbuseIPDB muestra este comentario publicamente para dar contexto del ataque.

    Args:
        event: Diccionario con los campos del evento (output de log_parser.py)

    Returns:
        String con la descripcion del ataque para el reporte publico
    """
    port = event.get("dst_port", "unknown")
    username = event.get("username", "unknown")

    # El comentario es publico en AbuseIPDB, no incluir informacion sensible
    # Solo describir el comportamiento observado de forma objetiva
    return (
        f"SSH/Telnet brute-force attack detected by Cowrie honeypot. "
        f"Port: {port}. "
        f"Attempted username: {username}. "
        f"Captured via honeypot deployed on Oracle Cloud Infrastructure."
    )


def report_ip(event: dict) -> bool:
    """
    Reporta la IP del evento a AbuseIPDB si no ha sido reportada antes en esta sesion.

    Args:
        event: Diccionario con los campos del evento

    Returns:
        True si se reporto correctamente o ya estaba reportada,
        False si hubo un error en la API
    """
    if not ABUSEIPDB_API_KEY:
        print("[ERROR] Falta ABUSEIPDB_API_KEY en el archivo .env")
        return False

    src_ip = event.get("src_ip", "")

    if not src_ip:
        print("[ABUSEIPDB] No se encontro IP en el evento, se omite el reporte")
        return False

    # Verificar si esta IP ya fue reportada en esta sesion
    # para no enviar reportes duplicados a la API
    if src_ip in _already_reported:
        print(f"[ABUSEIPDB] IP {src_ip} ya fue reportada en esta sesion, se omite")
        return True

    # Headers requeridos por la API de AbuseIPDB v2
    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json",
    }

    # Payload del reporte segun la documentacion de AbuseIPDB
    payload = {
        "ip": src_ip,
        # Multiples categorias separadas por coma
        "categories": f"{CATEGORY_BRUTE_FORCE},{CATEGORY_SSH}",
        "comment": build_comment(event),
    }

    try:
        response = requests.post(
            ABUSEIPDB_URL,
            headers=headers,
            data=payload,
            timeout=10
        )

        if response.status_code == 200:
            # Reporte enviado exitosamente
            # La API retorna el confidence score acumulado de esa IP
            data = response.json().get("data", {})
            abuse_score = data.get("abuseConfidenceScore", "N/A")
            print(f"[ABUSEIPDB] IP {src_ip} reportada. Confidence score: {abuse_score}%")

            # Registrar la IP como ya reportada para esta sesion
            _already_reported.add(src_ip)
            return True

        elif response.status_code == 422:
            # Error de validacion: puede ser una IP privada o mal formateada
            print(f"[ABUSEIPDB] IP {src_ip} no valida para reporte: {response.text}")
            return False

        elif response.status_code == 429:
            # Rate limit excedido: demasiados reportes en poco tiempo
            print(f"[ABUSEIPDB] Rate limit alcanzado, reintenta mas tarde")
            return False

        else:
            print(f"[ABUSEIPDB] Error inesperado {response.status_code}: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        # Error de red: sin conexion, timeout, etc.
        print(f"[ABUSEIPDB] Error de conexion: {e}")
        return False


def get_reported_count() -> int:
    """Retorna cuantas IPs unicas han sido reportadas en la sesion actual."""
    return len(_already_reported)
