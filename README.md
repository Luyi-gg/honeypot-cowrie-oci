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

Este honeypot simula un servidor SSH/Telnet vulnerable expuesto deliberadamente en Internet para atraer atacantes reales. A diferencia de un sistema de defensa tradicional que bloquea intrusiones, un honeypot las **invita** para estudiarlas.

Cada intento de conexion es registrado con detalle: la IP de origen, las credenciales probadas, los comandos ejecutados y la duracion de la sesion. Con esa informacion el sistema envia alertas instantaneas via Telegram y reporta automaticamente las IPs maliciosas a **AbuseIPDB**, contribuyendo a una base de datos global de amenazas utilizada por miles de organizaciones en el mundo.

El resultado es inteligencia real sobre como operan los atacantes: que usuarios y contrasenas prueban, que herramientas usan, de donde vienen y que buscan dentro de un servidor comprometido.

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

## Objetivos del Proyecto

- **Recoleccion de Inteligencia:** Capturar TTPs (Tacticas, Tecnicas y Procedimientos) de atacantes reales — que credenciales usan, que comandos ejecutan y que herramientas descargan
- **Contribucion Comunitaria:** Reportar IPs maliciosas a AbuseIPDB para que otros sistemas en el mundo puedan bloquearlas proactivamente
- **Alertas en Tiempo Real:** Notificacion instantanea via Telegram de cada intento de intrusion con geolocalizacion de la IP
- **Analisis de Patrones:** Identificar tendencias de ataque, paises de origen y comportamiento de los atacantes dentro de la jaula

---

## Stack Tecnologico

| Componente | Tecnologia | Funcion |
|---|---|---|
| Honeypot | Cowrie | Simula servidor SSH/Telnet vulnerable con jaula interactiva |
| Infraestructura | Oracle Cloud (OCI) | Instancia publica expuesta en Internet 24/7 |
| Alertas | Python + Telegram API | Notificaciones en tiempo real con geolocalizacion |
| Reporte | Python + AbuseIPDB API | Reporte automatico y comunitario de IPs maliciosas |
| SO | Ubuntu 24 LTS | Sistema operativo base del servidor |
| Logs | JSON + Cowrie logs | Almacenamiento estructurado de todos los eventos |

---

## Arquitectura de Infraestructura

La instancia corre en Oracle Cloud Free Tier con una IP publica expuesta directamente a Internet. El trafico entrante en los puertos de trampa es redirigido por iptables hacia Cowrie, que corre como usuario sin privilegios por seguridad. Los puertos reales de administracion del servidor estan en puertos no estandar y protegidos por fail2ban.

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

## Honeypot en Ejecucion

Vista de Cowrie ejecutandose en la instancia OCI monitoreando conexiones SSH/Telnet en tiempo real.

<p align="center">
  <img src="./docs/screenshots/cowrie-running.png" width="500">
</p>

---

## Instalacion y Configuracion

### Prerrequisitos

- Cuenta en Oracle Cloud (Free Tier disponible sin costo)
- Python 3.8+
- Bot Token de Telegram (se obtiene gratis con @BotFather)
- API Key de AbuseIPDB (se obtiene gratis en abuseipdb.com/register)

---

### 1. Clonar el repositorio

```bash
git clone https://github.com/Luyi-gg/honeypot-cowrie-oci.git
cd honeypot-cowrie-oci
```

---

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 3. Instalar y configurar Cowrie

```bash
# Dependencias del sistema necesarias para compilar Cowrie
sudo apt-get install git python3-virtualenv libssl-dev libffi-dev build-essential python3-dev

# Crear usuario dedicado — buena practica: nunca correr el honeypot como root
sudo adduser --disabled-password cowrie

# Clonar Cowrie en el directorio del usuario
sudo -u cowrie git clone https://github.com/cowrie/cowrie /home/cowrie/cowrie

cd /home/cowrie/cowrie

# Entorno virtual aislado para evitar conflictos de dependencias
sudo -u cowrie virtualenv cowrie-env

sudo -u cowrie cowrie-env/bin/pip install -r requirements.txt
```

---

### 4. Configurar variables de entorno

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

### 5. Ejecutar el monitor

```bash
# Recomendado: correr dentro de screen o tmux para que persista al cerrar la sesion SSH
python3 src/monitor.py
```

---

## Estructura del Proyecto

```text
honeypot-cowrie-oci/
│
├── README.md
├── requirements.txt
├── .env.example
│
├── src/
│   ├── monitor.py            # Script principal: vigila logs en tiempo real
│   ├── telegram_alert.py     # Envia alertas via Telegram Bot API
│   ├── abuseipdb_report.py   # Reporta IPs a AbuseIPDB
│   └── log_parser.py         # Parsea y estructura los logs JSON de Cowrie
│
├── docs/
│   ├── setup_oci.md          # Guia para configurar instancia en Oracle Cloud
│   ├── setup_cowrie.md       # Guia de instalacion de Cowrie
│   ├── architecture.md       # Diagrama detallado de arquitectura
│   └── screenshots/
│       ├── cowrie-running.png
│       ├── telegram-alert.png
│       ├── abuseipdb-profile.png
│       └── sample-log.png
│
└── data/
    └── sample_logs/          # Logs de ejemplo con IPs anonimizadas
```

---

## Datos Recolectados (Muestra)

Cowrie registra cada evento como una linea JSON. Esto permite analizar los datos con cualquier herramienta de procesamiento de texto o construir dashboards personalizados. Ejemplo de un evento real anonimizado:

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

Los comandos mas frecuentes observados son intentos de descargar malware con `wget` o `curl`, lectura de archivos del sistema como `/etc/passwd` y `/etc/shadow`, y creacion de usuarios o modificacion de claves SSH para mantener acceso persistente.

---

### Ejemplo visual de eventos capturados

<p align="center">
  <img src="./docs/screenshots/sample-log.png" width="450">
</p>

---

## Estadisticas del Honeypot

> Ultima actualizacion: 2026-05-21

| Metrica | Valor |
|---|---|
| IPs unicas detectadas | 2,970 |
| IPs bloqueadas | 2,702 |
| Intentos totales | 182,013 |
| Logins fallidos | 6,095 |
| Logins exitosos | 13,815 |
| Comandos ejecutados | 13,616 |

El alto numero de logins exitosos (13,815) se explica porque Cowrie esta configurado deliberadamente para aceptar credenciales comunes. Esto es intencional: al dejar entrar al atacante se captura informacion mucho mas valiosa, como los comandos que ejecuta y las herramientas que intenta descargar.

---

## Top 10 IPs con Mayor Actividad Maliciosa

| # | IP | Intentos | Pais |
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

## Top 8 Paises de Origen de Ataques

| # | Pais | IPs unicas | % del total |
|---|---|---|---|
| 1 | United States | 657 | 19.6% |
| 2 | China | 390 | 11.6% |
| 3 | Dominican Republic | 193 | 5.7% |
| 4 | United Kingdom | 133 | 4.0% |
| 5 | Brazil | 95 | 2.8% |
| 6 | Singapore | 86 | 2.6% |
| 7 | Hong Kong | 62 | 1.8% |
| 8 | India | 62 | 1.8% |

Vale la pena destacar que la IP mas agresiva del registro (45.85.180.143, Republica Dominicana) genero por si sola 59,568 intentos — mas que los paises #2, #3 y #4 combinados. Este patron es tipico de bots de fuerza bruta automatizados corriendo sin interrupcion desde un servidor comprometido o rentado.

---

## Contribucion a la Comunidad

Cada IP detectada atacando el honeypot es reportada automaticamente a **AbuseIPDB** con la categoria SSH Brute-Force. AbuseIPDB es una plataforma colaborativa donde administradores de sistemas, empresas de hosting y proveedores de firewall consultan reputacion de IPs antes de permitirles conexion.

Al reportar desde este honeypot, cada ataque capturado contribuye directamente a proteger otros sistemas en Internet que consultan esa base de datos.

La plataforma es utilizada por:

- Empresas de seguridad
- Firewalls y sistemas IDS/IPS
- Proveedores de hosting
- Administradores de sistemas independientes

---

### Perfil de reportes en AbuseIPDB

<p align="center">
  <img src="./docs/screenshots/abuseipdb-profile.png" width="650">
</p>

---

## Ejemplo de Alerta en Telegram

El bot envia una alerta inmediata por cada evento relevante, incluyendo la geolocalizacion de la IP y el puerto atacado para identificar rapidamente el tipo de ataque.

```text
[ALERTA] INTENTO DE INTRUSION DETECTADO

IP: XX.XX.XX.XX
Pais: Russia (RU)
Usuario: root
Contrasena: toor123
Puerto atacado: 22

Comandos ejecutados:
 -- uname -a
 -- cat /etc/shadow
 -- wget http://[redacted]/payload.sh

Duracion sesion: 1m 47s
Reportado a AbuseIPDB: SI
```

---

### Captura real de alerta enviada por el bot

<p align="center">
  <img src="./docs/screenshots/telegram-alert.png" width="600">
</p>

---

## Configuracion Avanzada del Honeypot

### Multiples puertos de escucha

Cowrie fue configurado para escuchar en multiples puertos comunmente atacados. Cada evento registra el puerto de destino, lo que permite identificar si el atacante uso SSH estandar, Telnet, o un puerto alternativo:

```ini
[ssh]
listen_port = 2222

[telnet]
listen_port = 2323
enabled = true
```

El trafico de los puertos reales se redirige a Cowrie con iptables:

```bash
# Puerto 22 real -> Cowrie interno en 2222
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222

# Puerto 23 real -> Cowrie interno en 2323
sudo iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2323
```

---

## Camuflaje del Honeypot (Deception)

Una parte clave del diseno es hacer que el servidor parezca un sistema real en produccion. Cuanto mas convincente se vea, mas tiempo permanece el atacante dentro de la jaula y mas informacion se recolecta sobre sus tecnicas.

Se modificaron tres capas de identidad:

**1. Hostname y banner de bienvenida** — el servidor se presenta como `web-prod-01` con un banner corporativo generico que imita un servidor Ubuntu real:

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

**2. Version de kernel simulada** — cuando el atacante ejecuta `uname -a`, recibe informacion de un sistema ligeramente desactualizado, que es exactamente lo que un atacante busca al escanear servidores vulnerables:

```ini
[shell]
kernel_version = 5.15.0-75-generic
kernel_build_string = #82-Ubuntu SMP Tue Jun 27 15:25:03 UTC 2023
```

**3. Credenciales aceptadas intencionalmente** — el archivo `userdb.txt` define las combinaciones de usuario y contrasena que Cowrie acepta para dejar entrar al atacante. Esto es deliberado: al creer que obtuvo acceso real, el atacante ejecuta sus herramientas y revela sus TTPs completos.

---

## Lo que aprendi

- Despliegue y administracion de instancias en Oracle Cloud Infrastructure (OCI)
- Configuracion y operacion de honeypots SSH/Telnet con Cowrie, incluyendo personalizacion del entorno simulado
- Tecnicas de Deception: como hacer que un sistema falso sea convincente para un atacante real
- Integracion de APIs externas con Python (Telegram Bot API, AbuseIPDB API, ip-api)
- Analisis de logs JSON en tiempo real con watchdog y procesamiento de eventos
- Conceptos practicos de Threat Intelligence: TTPs, IOCs y contribucion comunitaria
- Administracion de reglas iptables y ipset para bloqueo automatico de IPs maliciosas
- Hardening basico de servidores Linux: usuarios sin privilegios, puertos no estandar, fail2ban

---

## ⚠️ Disclaimer

> Este proyecto fue desarrollado unicamente con fines educativos y de investigacion en ciberseguridad. El honeypot opera en una instancia aislada sin conexion a sistemas de produccion ni datos sensibles. Todos los datos de IPs publicados en este repositorio estan anonimizados. El autor no se hace responsable del uso indebido de las tecnicas aqui documentadas.

---

## Contacto

**Luis SC**

- LinkedIn: https://linkedin.com/in/luis-angel-sc
- GitHub: https://github.com/Luyi-gg

---

Si este proyecto te fue util o aprendiste algo, considera darle una estrella al repositorio. Ayuda a que mas personas lo encuentren.
