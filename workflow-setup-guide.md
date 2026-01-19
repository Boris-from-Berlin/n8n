# Chromatic Archetypes Workflow - Setup Guide

## Übersicht
Dieser Workflow automatisiert die Erstellung personalisierter Archetyp-Berichte basierend auf Umfrageantworten.

## Architektur

```
Airtable Trigger
    ↓
AI Agent (OpenAI GPT-4o-mini)
    ↓
Airtable Update (Tag-Label speichern)
    ↓
Switch (4 Wege basierend auf Archetyp)
    ↓
┌─────────┬─────────┬─────────┬─────────┐
│ Krieger │Schöpfer │ Heiler  │ Weiser  │
└─────────┴─────────┴─────────┴─────────┘
    ↓ (für jeden Archetyp)
Google Docs Vorlage kopieren
    ↓
[NAME] Platzhalter ersetzen
    ↓
Als PDF konvertieren
    ↓
Zu Google Drive hochladen
    ↓
Mit User teilen + E-Mail senden
```

## Voraussetzungen

### 1. Server-Setup
- Node.js 18+ oder Docker
- n8n installiert und laufend
- Öffentliche URL (für Webhooks) oder Polling-Trigger

### 2. API-Accounts

#### OpenAI
```
Service: OpenAI API
Model: gpt-4o-mini
Kosten: ~$0.15/1M tokens
```
Erstelle API-Key: https://platform.openai.com/api-keys

#### Airtable
```
Base: DE - Dominant Archetype - Free
Table: Table 1
Trigger: Zeitpunkt der Erstellung
Filter: Gesendet = FALSE() AND Dominante Tag - Label leer
```
Benötigte Felder:
- Name (text)
- E-Mail (email)
- Frage 1-16 (number 1-5)
- Dominante Tag - Label (text)
- Gesendet (checkbox)

#### Google Workspace
Benötigte APIs:
- Google Drive API v3
- Google Docs API v1
- Gmail API v1

OAuth2 Scopes:
```
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/gmail.send
```

### 3. Google Drive Vorlagen

Erstelle 4 Google Docs Vorlagen mit Platzhalter `[NAME]`:

1. **Krieger-Dominanz-Template** (ID: 1ZwdenAmhFfritqRwhXx6thtzB6v5Vn3M)
2. **Schöpfer-Dominanz-Template** (ID: 1S3upJoKqKUelIQcAPfCGT3wLUjrggzXd)
3. **Heiler-Dominanz-Template** (ID: 1d4SZfk4qsiQ9cP1JrtPuoppquulFHgXoqAZfUa93vPY)
4. **Weisen-Dominanz-Template** (ID: 1IhjW71NpbYdSK8S_o0lacpuVxw79Cam5AkssnJ6zpuM)

Ordner-Struktur:
```
Google Drive
├── Chromatic Archetypes - Vorlagen (ID: 1zVCmN8um9jq0maF7rk21fHWIx51FFO-G)
└── Chromatic Archetypes - User PDF (ID: 1Lrcmd5IN6zkee9pmSE54rxARNLspFh4Z)
```

## Installation

### Schritt 1: n8n starten

**Docker (empfohlen):**
```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=changeme \
  -e WEBHOOK_URL=https://your-domain.com \
  -v ~/.n8n:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

**npm:**
```bash
npm install n8n -g
export N8N_BASIC_AUTH_ACTIVE=true
export N8N_BASIC_AUTH_USER=admin
export N8N_BASIC_AUTH_PASSWORD=changeme
n8n start
```

### Schritt 2: Credentials einrichten

1. Öffne n8n: `http://localhost:5678` oder `https://your-domain.com`
2. Navigiere zu **Credentials** → **New Credential**

#### OpenAI API
```
Type: OpenAI API
API Key: sk-...
```

#### Airtable Token API
```
Type: Airtable Token API
Access Token: pat...
```

#### Google Drive OAuth2
```
Type: Google Drive OAuth2 API
Auth URI: https://accounts.google.com/o/oauth2/auth
Token URI: https://oauth2.googleapis.com/token
Client ID: [aus Google Cloud Console]
Client Secret: [aus Google Cloud Console]
Scopes: https://www.googleapis.com/auth/drive
```

Wiederhole für Google Docs und Gmail OAuth2.

### Schritt 3: Workflow importieren

1. Kopiere den Workflow-JSON (aus deiner Anfrage)
2. In n8n: **Workflows** → **Import from File/URL**
3. JSON einfügen
4. **Import** klicken

### Schritt 4: Workflow anpassen

Ersetze folgende IDs mit deinen eigenen:

#### Airtable
```javascript
// Airtable Trigger Node
baseId: "appmyLE5hAoLqobel" → deine Base ID
tableId: "tblGubdWjV7UEZa8A" → deine Table ID
```

#### Google Drive Template-IDs
```javascript
// Make a copy4 (Krieger)
fileId: "1ZwdenAmhFfritqRwhXx6thtzB6v5Vn3M" → deine Vorlage

// Make a copy (Schöpfer)
fileId: "1S3upJoKqKUelIQcAPfCGT3wLUjrggzXd" → deine Vorlage

// Make a copy1 (Heiler)
fileId: "1d4SZfk4qsiQ9cP1JrtPuoppquulFHgXoqAZfUa93vPY" → deine Vorlage

// Drive - DE Works (Weiser)
fileId: "1IhjW71NpbYdSK8S_o0lacpuVxw79Cam5AkssnJ6zpuM" → deine Vorlage
```

#### Google Drive Ordner-IDs
```javascript
// Alle "Upload file" Nodes
folderId: "1Lrcmd5IN6zkee9pmSE54rxARNLspFh4Z" → dein PDF-Ordner
```

#### E-Mail-Anpassungen
```javascript
// Alle "Send a message" Nodes
bccList: "boris.dittberner@gmail.com" → deine E-Mail
```

### Schritt 5: Credentials zuweisen

Für jeden Node:
1. Node öffnen
2. Credential dropdown
3. Wähle deine erstellten Credentials

### Schritt 6: Testen

1. **Test-Eintrag in Airtable** erstellen:
   - Name: "Test User"
   - E-Mail: deine E-Mail
   - Frage 1-4: 5 (für Krieger)
   - Frage 5-16: 1
   - Gesendet: FALSE
   - Dominante Tag - Label: leer

2. **Workflow aktivieren**: Toggle oben rechts

3. **Warten**: Trigger prüft jede Minute

4. **Logs prüfen**: Executions Tab

## Troubleshooting

### Workflow startet nicht
- Prüfe Airtable Trigger Filter
- Stelle sicher dass `Gesendet = FALSE()` und Label leer
- Aktiviere Workflow

### AI Agent Fehler
- Prüfe OpenAI API Key
- Kontrolliere API-Limits/Quota
- Teste mit einfacherem Prompt

### Google Drive Fehler
```
Error: Insufficient permissions
```
→ OAuth2 Scopes prüfen, Re-autorisieren

```
Error: File not found
```
→ Template IDs prüfen, Sharing-Einstellungen

### E-Mail wird nicht gesendet
- Gmail API aktiviert?
- OAuth2 Scopes korrekt?
- Prüfe Gmail-Kontingent (500/Tag für free)

## Optimierungen

### 1. Kosten reduzieren
- Verwende `gpt-4o-mini` (bereits eingestellt ✓)
- Kürze den Prompt
- Cache häufige Anfragen

### 2. Performance
- Parallel-Verarbeitung nutzen (bereits vorhanden ✓)
- PDF-Konvertierung optimieren
- Batch-Processing für mehrere Einträge

### 3. Fehlerbehandlung
- Error Workflow bereits konfiguriert (ID: mDbYXUmu62K5m6WN)
- Retry-Logik:
  - Switch: 1 retry, 5s wait
  - AI Agent: 1 retry, 3-5s wait
- Slack-Benachrichtigung bei Fallback

### 4. Sicherheit
- n8n Basic Auth aktivieren
- HTTPS verwenden (Let's Encrypt)
- API-Keys als Environment Variables
- Firewall: nur Port 5678 (oder Reverse Proxy)

## Alternativen

### Cloud-Hosting
Statt Self-Hosting:
- **n8n Cloud**: https://n8n.io/cloud
- **Railway**: https://railway.app
- **DigitalOcean**: App Platform

### Workflow als Code
Alternative: Python-Skript mit:
```python
# requirements.txt
openai
pyairtable
google-api-python-client
```

Siehe separate `automation_script.py` für Beispiel.

## Wartung

### Monitoring
```bash
# Docker Logs
docker logs -f n8n

# Executions in n8n UI prüfen
# Airtable "Gesendet" Status überwachen
```

### Backup
```bash
# n8n Daten sichern
tar -czf n8n-backup-$(date +%Y%m%d).tar.gz ~/.n8n

# Workflow exportieren (in UI)
# Credentials separat sichern
```

### Updates
```bash
# Docker
docker pull docker.n8n.io/n8nio/n8n
docker restart n8n

# npm
npm update n8n -g
```

## Support

- n8n Docs: https://docs.n8n.io
- Community: https://community.n8n.io
- GitHub Issues: https://github.com/n8n-io/n8n/issues
