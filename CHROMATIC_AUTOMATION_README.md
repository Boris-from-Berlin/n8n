# Chromatic Archetypes Automation

Automatisierte Erstellung und Versand personalisierter Archetyp-Analysen basierend auf Umfrageantworten.

## Quick Start

### Option 1: n8n Workflow (empfohlen für Non-Developer)

```bash
# 1. n8n starten
docker run -d --name n8n -p 5678:5678 docker.n8n.io/n8nio/n8n

# 2. Browser öffnen
open http://localhost:5678

# 3. Workflow importieren
# - Workflows → Import from File
# - workflow.json aus dieser Anfrage einfügen

# 4. Credentials einrichten (siehe workflow-setup-guide.md)
```

📖 **Detaillierte Anleitung**: `workflow-setup-guide.md`

### Option 2: Python Script (empfohlen für Developer)

```bash
# 1. Dependencies installieren
pip install openai pyairtable google-api-python-client google-auth-httplib2 google-auth-oauthlib

# 2. Umgebungsvariablen setzen
export OPENAI_API_KEY="sk-..."
export AIRTABLE_API_KEY="pat..."
export AIRTABLE_BASE_ID="app..."
export GOOGLE_SERVICE_ACCOUNT_FILE="service-account.json"
export GOOGLE_DRIVE_PDF_FOLDER_ID="1Lrcmd5..."
export BCC_EMAIL="your-email@example.com"

# 3. Einmalig ausführen
python automation_alternative.py

# 4. Kontinuierlich laufen (wie n8n)
python automation_alternative.py --continuous --interval 60
```

📖 **Code-Dokumentation**: `automation_alternative.py`

## Was macht diese Automation?

```
┌─────────────┐
│  Airtable   │  Neue Umfrageantworten (16 Fragen)
│   Trigger   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   OpenAI    │  Analysiert Antworten → Dominanter Archetyp
│  GPT-4o-mini│  (Krieger/Schöpfer/Heiler/Weiser)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Google Docs  │  Kopiert passende Vorlage
│  Template   │  Ersetzt [NAME] Platzhalter
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ PDF Export  │  Konvertiert zu PDF
│   & Upload  │  Lädt zu Google Drive hoch
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Gmail     │  Sendet PDF per E-Mail an User
│   + Share   │  + Google Drive Link
└─────────────┘
```

## Benötigte API-Accounts

| Service | Zweck | Kosten | Setup-Link |
|---------|-------|--------|------------|
| **OpenAI** | AI-Archetyp-Analyse | ~$0.15/1M tokens | [API Keys](https://platform.openai.com/api-keys) |
| **Airtable** | Umfrage-Datenbank | Kostenlos (bis 1,200 records) | [Create Token](https://airtable.com/create/tokens) |
| **Google Drive** | Dokument-Templates & PDFs | Kostenlos (15GB) | [Cloud Console](https://console.cloud.google.com) |
| **Google Docs** | PDF-Generierung | Kostenlos | (siehe Drive) |
| **Gmail** | E-Mail-Versand | Kostenlos (500/Tag) | (siehe Drive) |

## Vergleich: n8n vs. Python

| Kriterium | n8n Workflow | Python Script |
|-----------|--------------|---------------|
| **Setup** | UI-basiert, visuell | Code-basiert |
| **Wartung** | Nodes anklicken | Code editieren |
| **Debugging** | Execution Logs | Python Debugger |
| **Anpassungen** | Drag & Drop | Vollständige Kontrolle |
| **Hosting** | Docker Container | Cronjob / Systemd |
| **Skills** | Kein Coding nötig | Python-Kenntnisse |
| **Kosten** | n8n Cloud: $20/Monat<br>Self-hosted: Kostenlos | Kostenlos |

## Deployment-Optionen

### 1. Lokaler Server (Development)
```bash
# n8n
docker run -p 5678:5678 docker.n8n.io/n8nio/n8n

# Python
python automation_alternative.py --continuous
```

### 2. Linux Server (Production)
```bash
# Als Systemd Service
sudo nano /etc/systemd/system/chromatic-automation.service

[Unit]
Description=Chromatic Archetypes Automation
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/automation
ExecStart=/usr/bin/python3 automation_alternative.py --continuous
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Aktivieren
sudo systemctl enable chromatic-automation
sudo systemctl start chromatic-automation
```

### 3. Cronjob (Simple)
```bash
# Jede Stunde ausführen
crontab -e

0 * * * * cd /path/to/automation && /usr/bin/python3 automation_alternative.py >> /var/log/chromatic.log 2>&1
```

### 4. Cloud Hosting

#### n8n Cloud
- **URL**: https://n8n.io/cloud
- **Preis**: $20/Monat
- **Vorteil**: Managed, kein Server nötig

#### Railway.app (für Python)
```bash
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python automation_alternative.py --continuous"
```

#### DigitalOcean Droplet
```bash
# $6/Monat - Basic Droplet
# 1 GB RAM, 1 vCPU, 25 GB SSD

# n8n via Docker Compose
wget https://raw.githubusercontent.com/n8n-io/n8n/master/docker-compose.yml
docker-compose up -d
```

## Troubleshooting

### Problem: OpenAI API Rate Limit
```
Error: Rate limit exceeded
```
**Lösung**:
- Warte 60 Sekunden
- Oder: Upgrade auf Paid Plan

### Problem: Google Drive Permission Denied
```
Error: Insufficient permissions
```
**Lösung**:
- OAuth2 Scopes prüfen
- Re-autorisieren in n8n
- Service Account Berechtigungen prüfen

### Problem: Gmail Daily Limit
```
Error: User rate limit exceeded
```
**Lösung**:
- Gmail erlaubt nur 500 E-Mails/Tag
- Verwende SendGrid/Mailgun für höheres Volumen

### Problem: n8n Workflow startet nicht
```
Workflow inactive
```
**Lösung**:
- Toggle "Active" oben rechts
- Prüfe Airtable Trigger-Filter
- Logs in Executions Tab prüfen

## Monitoring

### n8n
```bash
# Logs ansehen
docker logs -f n8n

# Executions in UI
http://localhost:5678 → Executions Tab
```

### Python
```bash
# Systemd Logs
journalctl -u chromatic-automation -f

# Cronjob Logs
tail -f /var/log/chromatic.log

# Status prüfen
systemctl status chromatic-automation
```

## Sicherheit

### n8n
```bash
# Basic Auth aktivieren
docker run -d \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD='strong-password-here' \
  -p 5678:5678 \
  docker.n8n.io/n8nio/n8n

# Nginx Reverse Proxy mit HTTPS
# (siehe workflow-setup-guide.md)
```

### Python
```bash
# Umgebungsvariablen in .env File
pip install python-dotenv

# .env
OPENAI_API_KEY=sk-...
AIRTABLE_API_KEY=pat...

# Im Script
from dotenv import load_dotenv
load_dotenv()

# .env niemals committen!
echo ".env" >> .gitignore
```

## Kosten-Schätzung

Bei **100 Umfragen/Monat**:

| Service | Kosten |
|---------|--------|
| OpenAI (GPT-4o-mini) | ~$0.15 |
| Airtable | $0 (Free Tier) |
| Google Workspace | $0 (Free Tier) |
| n8n (self-hosted) | $0 |
| Server (DigitalOcean) | $6/Monat |
| **TOTAL** | **~$6.15/Monat** |

Mit n8n Cloud: **~$26.15/Monat**

## Support & Dokumentation

- 📘 **Vollständige Anleitung**: `workflow-setup-guide.md`
- 🐍 **Python Code**: `automation_alternative.py`
- 🔧 **n8n Docs**: https://docs.n8n.io
- 💬 **n8n Community**: https://community.n8n.io
- 🐛 **Issues**: https://github.com/n8n-io/n8n/issues

## Nächste Schritte

1. ✅ Entscheide: n8n oder Python?
2. ✅ API-Accounts erstellen (siehe Tabelle oben)
3. ✅ Setup-Anleitung folgen
4. ✅ Mit Test-Daten testen
5. ✅ Produktiv schalten
6. ✅ Monitoring einrichten

**Viel Erfolg mit deiner Automation! 🎨**
