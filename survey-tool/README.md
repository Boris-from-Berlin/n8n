# Chromatic Archetypes Survey Tool

Ein modernes, responsives Umfrage-Tool für Persönlichkeitstests mit 16 Fragen und direkter Integration zu n8n via Webhook.

## Features

- **Modernes Design**: Gradient-Hintergrund, smooth Animationen, responsive Layout
- **16 Fragen**: Organisiert in 4 Kapiteln (Handeln, Kreativität, Fürsorge, Weisheit)
- **1-5 Bewertungsskala**: Intuitives Rating-System für jede Frage
- **Fortschrittsanzeige**: Visueller Fortschrittsbalken während der Umfrage
- **Formular-Validierung**: Client-seitige Validierung für Name und E-Mail
- **Webhook-Integration**: Automatisches Senden der Daten an n8n
- **Erfolgsmeldung**: Bestätigung nach erfolgreicher Übermittlung

## Installation & Setup

### 1. Datei öffnen

Die `index.html` Datei kann direkt in einem Browser geöffnet werden. Keine Build-Schritte erforderlich.

### 2. n8n Webhook konfigurieren

#### In n8n:

1. Erstellen Sie einen neuen Workflow in n8n
2. Fügen Sie einen **Webhook**-Node hinzu
3. Konfigurieren Sie den Webhook:
   - **Method**: POST
   - **Path**: Wählen Sie einen eindeutigen Pfad (z.B. `chromatic-survey`)
   - **Response Mode**: Respond Immediately
   - **Response Code**: 200
4. Kopieren Sie die **Production URL** des Webhooks

#### In der Survey-Tool Datei:

1. Öffnen Sie `index.html` in einem Text-Editor
2. Finden Sie die Zeile mit `const WEBHOOK_URL = 'YOUR_N8N_WEBHOOK_URL';`
3. Ersetzen Sie `YOUR_N8N_WEBHOOK_URL` mit Ihrer n8n Webhook-URL:

```javascript
const WEBHOOK_URL = 'https://your-n8n-instance.com/webhook/chromatic-survey';
```

### 3. Hosting

Sie haben mehrere Optionen zum Hosten:

#### Option A: Lokales Testen
Öffnen Sie die `index.html` Datei direkt im Browser (funktioniert für Tests).

#### Option B: Einfacher Webserver
```bash
# Python 3
python -m http.server 8000

# Node.js (mit http-server)
npx http-server
```

Dann öffnen Sie `http://localhost:8000` im Browser.

#### Option C: Deployment
- Netlify (Drag & Drop)
- Vercel
- GitHub Pages
- Ihr eigener Webserver

## Datenformat

Die an n8n gesendeten Daten haben folgendes Format:

```json
{
  "name": "Max Mustermann",
  "email": "max@example.com",
  "timestamp": "2026-01-16T19:55:20.000Z",
  "answers": {
    "frage1": 4,
    "frage2": 2,
    "frage3": 5,
    "frage4": 4,
    "frage5": 1,
    "frage6": 2,
    "frage7": 4,
    "frage8": 4,
    "frage9": 5,
    "frage10": 3,
    "frage11": 4,
    "frage12": 5,
    "frage13": 2,
    "frage14": 4,
    "frage15": 5,
    "frage16": 2
  }
}
```

## n8n Workflow Beispiel

Hier ist ein einfaches Beispiel für einen n8n Workflow:

```
1. Webhook Trigger (empfängt die Daten)
   ↓
2. Set Node (bereitet Daten auf)
   ↓
3. Berechnung der dominanten Tags
   ↓
4. Email Node ODER
   Spreadsheet Node ODER
   Database Node
```

### Beispiel: Antworten in Google Sheets speichern

1. **Webhook Node** → Empfängt Daten
2. **Google Sheets Node**:
   - Operation: Append
   - Spreadsheet: Ihre Tabelle
   - Mapping:
     - Name → `{{ $json.name }}`
     - Email → `{{ $json.email }}`
     - Timestamp → `{{ $json.timestamp }}`
     - Frage 1 → `{{ $json.answers.frage1 }}`
     - ... (für alle 16 Fragen)

### Beispiel: E-Mail mit Ergebnissen senden

```javascript
// In einem Code Node oder Function Node
const answers = $json.answers;

// Berechne Scores für jeden Archetyp
const handeln = (answers.frage1 + answers.frage2 + answers.frage3 + answers.frage4) / 4;
const kreativitaet = (answers.frage5 + answers.frage6 + answers.frage7 + answers.frage8) / 4;
const fuersorge = (answers.frage9 + answers.frage10 + answers.frage11 + answers.frage12) / 4;
const weisheit = (answers.frage13 + answers.frage14 + answers.frage15 + answers.frage16) / 4;

// Finde dominanten Archetyp
const scores = {
  'Roter Krieger': handeln,
  'Gelber Schöpfer': kreativitaet,
  'Grüner Heiler': fuersorge,
  'Blauer Weiser': weisheit
};

const dominant = Object.keys(scores).reduce((a, b) =>
  scores[a] > scores[b] ? a : b
);

return {
  name: $json.name,
  email: $json.email,
  dominant: dominant,
  scores: scores
};
```

## Anpassungen

### Farben ändern

Die Farben sind in CSS-Variablen definiert und können leicht angepasst werden:

```css
:root {
    --primary-color: #6366f1;       /* Hauptfarbe für Buttons */
    --primary-hover: #4f46e5;       /* Hover-Farbe */
    --secondary-color: #f59e0b;     /* Sekundärfarbe */
    --success-color: #10b981;       /* Erfolgsfarbe */
}
```

### Fragen ändern

Die Fragen können direkt im HTML geändert werden. Jede Frage folgt diesem Muster:

```html
<div class="question-group">
    <label class="question-label">
        Frage X: Ihr Fragentext hier
    </label>
    <div class="rating-labels">
        <span class="rating-label-text">Trifft gar nicht zu</span>
        <span class="rating-label-text">Trifft absolut zu</span>
    </div>
    <div class="rating-options">
        <!-- Radio buttons für 1-5 -->
    </div>
</div>
```

### Intro-Text anpassen

Der Intro-Text kann im `<div class="intro-section">` Bereich geändert werden.

## Browser-Kompatibilität

- Chrome (empfohlen)
- Firefox
- Safari
- Edge

Funktioniert auf Desktop und Mobile.

## Sicherheitshinweise

- Die Webhook-URL sollte nicht öffentlich geteilt werden
- In n8n können Sie zusätzliche Authentifizierung hinzufügen
- Verwenden Sie HTTPS für Produktions-Deployments
- Implementieren Sie Rate-Limiting in n8n bei Bedarf

## Support

Bei Fragen oder Problemen:
1. Überprüfen Sie die Browser-Konsole auf Fehler
2. Stellen Sie sicher, dass die Webhook-URL korrekt ist
3. Testen Sie den Webhook direkt in n8n

## Lizenz

Dieses Tool ist für den privaten und kommerziellen Gebrauch frei verfügbar.
