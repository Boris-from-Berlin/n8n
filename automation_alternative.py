#!/usr/bin/env python3
"""
Chromatic Archetypes Automation - Python Alternative zu n8n Workflow

Diese Skript repliziert die n8n Workflow-Funktionalität:
1. Airtable-Einträge überwachen
2. Archetyp mit OpenAI analysieren
3. Personalisierte PDFs erstellen
4. Per E-Mail versenden

Vorteile:
- Volle Kontrolle über Logik
- Einfachere Fehlerbehandlung
- Keine n8n-Installation nötig
- Kann als Cronjob laufen

Requirements:
    pip install openai pyairtable google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

import os
import time
from typing import Dict, List, Optional
from datetime import datetime

# API Imports
from openai import OpenAI
from pyairtable import Api as AirtableApi
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64
import io


class ChromaticArchetypesAutomation:
    """Hauptklasse für Archetyp-Automation"""

    # Archetyp-Definitionen
    ARCHETYPES = {
        'roter Krieger': {
            'template_id': '1ZwdenAmhFfritqRwhXx6thtzB6v5Vn3M',
            'questions': [1, 2, 3, 4]
        },
        'gelber Schöpfer': {
            'template_id': '1S3upJoKqKUelIQcAPfCGT3wLUjrggzXd',
            'questions': [5, 6, 7, 8]
        },
        'grüner Heiler': {
            'template_id': '1d4SZfk4qsiQ9cP1JrtPuoppquulFHgXoqAZfUa93vPY',
            'questions': [9, 10, 11, 12]
        },
        'blauer Weiser': {
            'template_id': '1IhjW71NpbYdSK8S_o0lacpuVxw79Cam5AkssnJ6zpuM',
            'questions': [13, 14, 15, 16]
        }
    }

    def __init__(self):
        """Initialisiere API-Clients"""
        # OpenAI
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Airtable
        self.airtable = AirtableApi(os.getenv('AIRTABLE_API_KEY'))
        self.base_id = os.getenv('AIRTABLE_BASE_ID')
        self.table_name = 'Table 1'

        # Google APIs
        creds = self._get_google_credentials()
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.docs_service = build('docs', 'v1', credentials=creds)
        self.gmail_service = build('gmail', 'v1', credentials=creds)

        self.pdf_folder_id = os.getenv('GOOGLE_DRIVE_PDF_FOLDER_ID')

    def _get_google_credentials(self) -> Credentials:
        """Google OAuth2 Credentials laden"""
        # Vereinfachte Version - in Produktion: OAuth2 Flow implementieren
        # Siehe: https://developers.google.com/drive/api/quickstart/python
        from google.oauth2 import service_account

        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE'),
            scopes=[
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/gmail.send'
            ]
        )
        return credentials

    def get_unprocessed_records(self) -> List[Dict]:
        """Hole alle unbearbeiteten Airtable-Einträge"""
        table = self.airtable.table(self.base_id, self.table_name)

        # Filter: Gesendet = FALSE und Dominante Tag - Label leer
        formula = "AND({Gesendet} = FALSE(), OR({Dominante Tag - Label} = BLANK(), {Dominante Tag - Label} = ''))"

        records = table.all(formula=formula)
        print(f"📥 {len(records)} unbearbeitete Einträge gefunden")
        return records

    def analyze_archetype(self, record: Dict) -> str:
        """Analysiere Archetyp mit OpenAI"""
        fields = record['fields']

        # Prompt erstellen
        prompt = self._build_archetype_prompt(fields)

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": '{"Tag_Label": "dominanter Archetyp"}'
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            archetype = result.get('Tag_Label', '')

            print(f"🤖 AI-Analyse für {fields.get('Name')}: {archetype}")
            return archetype

        except Exception as e:
            print(f"❌ OpenAI Fehler: {e}")
            return self._fallback_archetype_calculation(fields)

    def _build_archetype_prompt(self, fields: Dict) -> str:
        """Erstelle OpenAI Prompt aus Airtable-Feldern"""
        name = fields.get('Name', 'Unbekannt')

        prompt = f"""Du bist ein einfühlsamer Coach und Erklärer. Deine Aufgabe ist es, den dominanten Archetyp einer Person anhand ihrer Antworten auf 16 Fragen zu identifizieren [Name:{name}]

Werte die 16 Antworten (Skala 1–5) aus:

Fragen 1–4 → roter Krieger
Frage 1: {fields.get('Frage 1: Ich fühle mich kraftvoll, wenn ich Herausforderungen aktiv anpacke')}
Frage 2: {fields.get('Frage 2: Ich setze mich mutig für meine Ziele ein, auch wenn Hindernisse auftreten.')}
Frage 3: {fields.get('Frage 3: Ich stehe gerne für andere ein und übernehme Verantwortung.')}
Frage 4: {fields.get('Frage 4: Es fällt mir leicht, Entscheidungen zu treffen und zu handeln')}

Fragen 5–8 → gelber Schöpfer
Frage 5: {fields.get('Frage 5: Ich habe viele kreative Ideen, die ich in die Welt bringen möchte.')}
Frage 6: {fields.get('Frage 6: Ich erfinde gern neue Lösungen und denke in Visionen der Zukunft.')}
Frage 7: {fields.get('Frage 7: Ich bin begeistert, wenn ich etwas Schönes oder Originelles erschaffen kann.')}
Frage 8: {fields.get('Frage 8: Ich bringe Leichtigkeit und Freude in meine Projekte.')}

Fragen 9–12 → grüner Heiler
Frage 9: {fields.get('Frage 9: Mir ist wichtig, dass es meinen Mitmenschen gut geht, und ich helfe gern.')}
Frage 10: {fields.get('Frage 10: Ich suche Harmonie und Balance in Beziehungen und Umfeldern.')}
Frage 11: {fields.get('Frage 11: Ich kann mich leicht in andere hineinversetzen und ihre Bedürfnisse erkennen.')}
Frage 12: {fields.get('Frage 12: Ich ziehe Kraft aus Natur, Ruhe und regenerativen Tätigkeiten.')}

Fragen 13–16 → blauer Weiser
Frage 13: {fields.get('Frage 13: Ich reflektiere gern über komplexe Fragen und suche nach tieferem Sin')}
Frage 14: {fields.get('Frage 14: Ich beobachte Situationen analytisch und erkenne Muster.')}
Frage 15: {fields.get('Frage 15: Ich vermittle gern Wissen und bringe Klarheit in schwierige Zusammenhänge.')}
Frage 16: {fields.get('Frage 16: Ich bleibe ruhig und besonnen, wenn andere emotional reagieren.')}

Regeln:
1. Addiere die Werte pro Archetyp (min. 4, max. 20)
2. Der Archetyp mit der höchsten Punktzahl gewinnt
3. Bei Gleichstand: Der mit den meisten "5"-Bewertungen

Output: Nur JSON mit Tag_Label (exakt: "roter Krieger", "gelber Schöpfer", "grüner Heiler", oder "blauer Weiser")
"""
        return prompt

    def _fallback_archetype_calculation(self, fields: Dict) -> str:
        """Fallback: Archetyp manuell berechnen wenn OpenAI fehlschlägt"""
        scores = {}

        for archetype, config in self.ARCHETYPES.items():
            score = 0
            for q in config['questions']:
                field_name = self._get_question_field_name(q)
                score += fields.get(field_name, 0)
            scores[archetype] = score

        # Höchsten Score finden
        dominant = max(scores, key=scores.get)
        print(f"🔧 Fallback-Berechnung: {dominant} (Scores: {scores})")
        return dominant

    def _get_question_field_name(self, question_num: int) -> str:
        """Mappe Frage-Nummer zu Airtable-Feldname"""
        question_map = {
            1: "Frage 1: Ich fühle mich kraftvoll, wenn ich Herausforderungen aktiv anpacke",
            2: "Frage 2: Ich setze mich mutig für meine Ziele ein, auch wenn Hindernisse auftreten.",
            3: "Frage 3: Ich stehe gerne für andere ein und übernehme Verantwortung.",
            4: "Frage 4: Es fällt mir leicht, Entscheidungen zu treffen und zu handeln",
            5: "Frage 5: Ich habe viele kreative Ideen, die ich in die Welt bringen möchte.",
            6: "Frage 6: Ich erfinde gern neue Lösungen und denke in Visionen der Zukunft.",
            7: "Frage 7: Ich bin begeistert, wenn ich etwas Schönes oder Originelles erschaffen kann.",
            8: "Frage 8: Ich bringe Leichtigkeit und Freude in meine Projekte.",
            9: "Frage 9: Mir ist wichtig, dass es meinen Mitmenschen gut geht, und ich helfe gern.",
            10: "Frage 10: Ich suche Harmonie und Balance in Beziehungen und Umfeldern.",
            11: "Frage 11: Ich kann mich leicht in andere hineinversetzen und ihre Bedürfnisse erkennen.",
            12: "Frage 12: Ich ziehe Kraft aus Natur, Ruhe und regenerativen Tätigkeiten.",
            13: "Frage 13: Ich reflektiere gern über komplexe Fragen und suche nach tieferem Sin",
            14: "Frage 14: Ich beobachte Situationen analytisch und erkenne Muster.",
            15: "Frage 15: Ich vermittle gern Wissen und bringe Klarheit in schwierige Zusammenhänge.",
            16: "Frage 16: Ich bleibe ruhig und besonnen, wenn andere emotional reagieren."
        }
        return question_map.get(question_num, '')

    def create_pdf_report(self, name: str, archetype: str) -> bytes:
        """Erstelle PDF-Report aus Google Docs Template"""
        template_id = self.ARCHETYPES[archetype]['template_id']

        # 1. Template kopieren
        copy_title = f"{name} - {archetype}"
        copied_file = self.drive_service.files().copy(
            fileId=template_id,
            body={'name': copy_title}
        ).execute()

        doc_id = copied_file['id']
        print(f"📄 Dokument erstellt: {copy_title}")

        # 2. [NAME] Platzhalter ersetzen
        requests = [
            {
                'replaceAllText': {
                    'containsText': {
                        'text': '[NAME]',
                        'matchCase': True
                    },
                    'replaceText': name
                }
            }
        ]

        self.docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"✏️  [NAME] ersetzt durch {name}")

        # 3. Als PDF exportieren
        pdf_request = self.drive_service.files().export_media(
            fileId=doc_id,
            mimeType='application/pdf'
        )

        pdf_file = io.BytesIO()
        downloader = MediaIoBaseDownload(pdf_file, pdf_request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        pdf_content = pdf_file.getvalue()
        print(f"📑 PDF generiert ({len(pdf_content)} bytes)")

        # 4. Temporäres Dokument löschen
        self.drive_service.files().delete(fileId=doc_id).execute()

        return pdf_content

    def upload_and_share_pdf(self, name: str, archetype: str, pdf_content: bytes, user_email: str) -> str:
        """PDF hochladen und mit User teilen"""
        file_metadata = {
            'name': f"{name} - Ergebnis - {archetype}.pdf",
            'parents': [self.pdf_folder_id],
            'mimeType': 'application/pdf'
        }

        media = MediaFileUpload(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            resumable=True
        )

        # Upload
        uploaded_file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()

        file_id = uploaded_file['id']
        web_link = uploaded_file['webViewLink']

        print(f"☁️  PDF hochgeladen: {web_link}")

        # Mit User teilen
        permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': user_email
        }

        self.drive_service.permissions().create(
            fileId=file_id,
            body=permission,
            sendNotificationEmail=True,
            emailMessage=self._get_share_email_message(name)
        ).execute()

        print(f"🔗 Geteilt mit {user_email}")

        return web_link

    def _get_share_email_message(self, name: str) -> str:
        """E-Mail-Text für Google Drive Sharing"""
        return f"""Hallo {name},
dein Ergebnis ist da – und wir freuen uns riesig, dich auf deiner Reise begleiten zu dürfen!
Tauche ein in deine ganz persönliche Analyse und entdecke, was in dir steckt.

Wir wünschen dir viel Freude mit deinen Erkenntnissen – und sind gespannt auf dein Feedback.
Gemeinsam starten wir in eine spannende Reise.

✨ Teile den Test mit deinen Liebsten
und erhaltet nicht nur neue Einsichten,
sondern auch 100 stärkende Affirmationen
als Geschenk von uns dazu.

👉 Hier geht's zum Test-Link zum Teilen
Link: http://bit.ly/4lmWTiX

Viel Spaß beim Entdecken –
und danke, dass du Teil dieser Reise bist 💫

Herzliche Grüße
Dein Chromatic Archetypes Team"""

    def send_email_with_pdf(self, to_email: str, name: str, pdf_content: bytes):
        """Sende E-Mail mit PDF-Anhang"""
        message = MIMEMultipart()
        message['to'] = to_email
        message['bcc'] = os.getenv('BCC_EMAIL', '')
        message['subject'] = f"Hallo {name}, dein Ergebnis ist da."

        # E-Mail Body
        body = f"""Hallo {name},
im Anhang findest du die gewünschte Datei.

Wir wünschen dir ganz viel Spaß mit deinem Ergebnis.

EIN GESCHENK
Wir würden uns freuen, wenn du uns kurz Bescheid gibst, dass du unser Ergebnis erhalten hast.

Ein "ich hab es erhalten" würde genügen.
Zum Dank gibts es noch ein Geschenk von uns.

Liebe Grüße
dein Chromatic Archetypes-Team"""

        message.attach(MIMEText(body, 'html'))

        # PDF anhängen
        pdf_attachment = MIMEApplication(pdf_content, _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f'{name}_Archetyp_Analyse.pdf')
        message.attach(pdf_attachment)

        # Senden via Gmail API
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        self.gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        print(f"📧 E-Mail gesendet an {to_email}")

    def update_airtable_record(self, record_id: str, archetype: str):
        """Markiere Airtable-Eintrag als verarbeitet"""
        table = self.airtable.table(self.base_id, self.table_name)

        table.update(record_id, {
            'Gesendet': True,
            'Dominante Tag - Label': archetype
        })

        print(f"✅ Airtable aktualisiert: {record_id}")

    def process_record(self, record: Dict):
        """Verarbeite einen einzelnen Airtable-Eintrag"""
        try:
            fields = record['fields']
            record_id = record['id']

            name = fields.get('Name', 'Unbekannt')
            email = fields.get('E-Mail', '')

            print(f"\n{'='*60}")
            print(f"🚀 Verarbeite: {name} ({email})")
            print(f"{'='*60}")

            # 1. Archetyp analysieren
            archetype = self.analyze_archetype(record)

            if not archetype or archetype not in self.ARCHETYPES:
                raise ValueError(f"Ungültiger Archetyp: {archetype}")

            # 2. PDF erstellen
            pdf_content = self.create_pdf_report(name, archetype)

            # 3. Hochladen & Teilen
            drive_link = self.upload_and_share_pdf(name, archetype, pdf_content, email)

            # 4. E-Mail senden
            self.send_email_with_pdf(email, name, pdf_content)

            # 5. Airtable aktualisieren
            self.update_airtable_record(record_id, archetype)

            print(f"✨ Erfolgreich verarbeitet: {name} → {archetype}")

        except Exception as e:
            print(f"❌ Fehler bei {fields.get('Name', record_id)}: {e}")
            import traceback
            traceback.print_exc()

    def run(self, continuous: bool = False, interval: int = 60):
        """Hauptschleife"""
        print("🎨 Chromatic Archetypes Automation gestartet")

        while True:
            try:
                # Unbearbeitete Einträge holen
                records = self.get_unprocessed_records()

                # Verarbeiten
                for record in records:
                    self.process_record(record)

                if not continuous:
                    break

                print(f"\n💤 Warte {interval} Sekunden...")
                time.sleep(interval)

            except KeyboardInterrupt:
                print("\n👋 Automation gestoppt")
                break
            except Exception as e:
                print(f"❌ Fehler in Hauptschleife: {e}")
                if not continuous:
                    break
                time.sleep(interval)


def main():
    """CLI Entry Point"""
    import argparse

    parser = argparse.ArgumentParser(description='Chromatic Archetypes Automation')
    parser.add_argument('--continuous', '-c', action='store_true', help='Kontinuierlich laufen (wie n8n Trigger)')
    parser.add_argument('--interval', '-i', type=int, default=60, help='Poll-Intervall in Sekunden (Standard: 60)')

    args = parser.parse_args()

    # Umgebungsvariablen prüfen
    required_env = [
        'OPENAI_API_KEY',
        'AIRTABLE_API_KEY',
        'AIRTABLE_BASE_ID',
        'GOOGLE_SERVICE_ACCOUNT_FILE',
        'GOOGLE_DRIVE_PDF_FOLDER_ID'
    ]

    missing = [var for var in required_env if not os.getenv(var)]
    if missing:
        print(f"❌ Fehlende Umgebungsvariablen: {', '.join(missing)}")
        print("\nSetze sie mit:")
        for var in missing:
            print(f"export {var}='...'")
        return 1

    # Automation starten
    automation = ChromaticArchetypesAutomation()
    automation.run(continuous=args.continuous, interval=args.interval)

    return 0


if __name__ == '__main__':
    exit(main())
