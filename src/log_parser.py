"""
log_parser.py
-------------
Lee y estructura los eventos del archivo de logs JSON de Cowrie.
Cowrie genera una linea JSON por cada evento (conexion, login, comando, etc.)
Este modulo filtra solo los eventos relevantes y los convierte en diccionarios
limpios que el resto del sistema puede procesar facilmente.
"""

import json


# Eventos de Cowrie que nos interesan monitorear
# cowrie.login.failed -> intento de login con credenciales incorrectas
# cowrie.login.success -> login exitoso (el atacante entro con credenciales del userdb)
# cowrie.command.input -> comando ejecutado dentro de la sesion
# cowrie.session.connect -> nueva conexion establecida al honeypot
RELEVANT_EVENTS = {
    "cowrie.login.failed",
    "cowrie.login.success",
    "cowrie.command.input",
    "cowrie.session.connect",
}


def parse_line(line: str) -> dict | None:
    """
    Parsea una linea del archivo de logs de Cowrie.

    Cowrie escribe cada evento como un objeto JSON en una sola linea.
    Si la linea no es JSON valido o no es un evento relevante, retorna None.

    Args:
        line: Una linea cruda del archivo cowrie.json

    Returns:
        Diccionario con los campos del evento, o None si no es relevante.
    """
    line = line.strip()

    # Ignorar lineas vacias
    if not line:
        return None

    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        # Si la linea no es JSON valido, la ignoramos silenciosamente
        return None

    # Filtrar solo los tipos de eventos que nos interesan
    event_id = event.get("eventid", "")
    if event_id not in RELEVANT_EVENTS:
        return None

    # Construir un diccionario limpio con solo los campos que necesitamos
    return {
        # Momento exacto en que ocurrio el evento (formato ISO 8601)
        "timestamp": event.get("timestamp", ""),

        # Tipo de evento (login fallido, comando ejecutado, etc.)
        "event_type": event_id,

        # IP de origen del atacante
        "src_ip": event.get("src_ip", ""),

        # Puerto de destino: nos indica si el ataque fue por SSH (22), Telnet (23) u otro
        "dst_port": event.get("dst_port", ""),

        # Credenciales usadas en el intento de login
        "username": event.get("username", ""),
        "password": event.get("password", ""),

        # Comando ejecutado (solo presente en eventos cowrie.command.input)
        "input": event.get("input", ""),

        # ID unico de la sesion - permite agrupar todos los eventos de un mismo atacante
        "session": event.get("session", ""),
    }


def is_login_event(event: dict) -> bool:
    """Retorna True si el evento es un intento de login (exitoso o fallido)."""
    return event.get("event_type") in {
        "cowrie.login.failed",
        "cowrie.login.success",
    }


def is_successful_login(event: dict) -> bool:
    """
    Retorna True si el atacante logro entrar al honeypot.
    Esto ocurre cuando usa alguna de las credenciales definidas en userdb.txt
    """
    return event.get("event_type") == "cowrie.login.success"


def is_command_event(event: dict) -> bool:
    """Retorna True si el evento contiene un comando ejecutado por el atacante."""
    return event.get("event_type") == "cowrie.command.input"
