from fpdf import FPDF
from fpdf.enums import XPos, YPos

ACCENT = (34, 197, 94)  # green — Onboarding

class Doc(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(180, 180, 180)
        self.cell(0, 8, "Nordlicht Studios - Onboarding-Guide  |  Demo-Dokument", align="R")
        self.ln(2)
        self.set_draw_color(230, 230, 230)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(180, 180, 180)
        self.cell(0, 10, f"Seite {self.page_no()}", align="C")

    def cover(self):
        self.add_page()
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 297, "F")
        self.set_y(20)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*ACCENT)
        self.cell(0, 10, "DEMO-DOKUMENT - Wissens-Assistent Showcase", align="C")
        self.set_y(80)
        self.set_font("Helvetica", "B", 32)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "Willkommen bei Nordlicht", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.set_font("Helvetica", "", 18)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, "Onboarding-Guide fuer neue Mitarbeitende", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(100, 116, 139)
        self.multi_cell(
            0, 7,
            "Nordlicht Studios ist eine fiktive Design-Agentur. Dieser Guide dient als Demo\n"
            "fuer den Use Case 'Onboarding'. Alle Personen und Ablaeufe sind erfunden.\n"
            "Stell dem Assistenten direkt eine Frage - zum Beispiel:\n\n"
            '  "Wo finde ich meine Zugangsdaten?"\n'
            '  "Wer ist mein Buddy und Ansprechpartner?"\n'
            '  "Wie richte ich den VPN-Zugang ein?"',
            align="C"
        )

    def chapter(self, title):
        self.ln(6)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*ACCENT)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*ACCENT)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(4)
        self.set_text_color(30, 30, 30)

    def section(self, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 30, 30)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def keyval(self, items):
        for key, val in items:
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(60, 60, 60)
            self.cell(60, 6, key + ":")
            self.set_font("Helvetica", "", 10)
            self.multi_cell(0, 6, val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)


pdf = Doc()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.cover()

# --- Erster Tag ---
pdf.add_page()
pdf.chapter("1. Dein erster Tag")
pdf.body(
    "Schoen, dass du da bist! Dieser Guide begleitet dich durch deine ersten Wochen bei "
    "Nordlicht Studios. Wenn eine Frage offen bleibt, sprich einfach deinen Buddy an "
    "(siehe Kapitel 2)."
)

pdf.section("Zugangsdaten")
pdf.body(
    "Deine persoenlichen Zugangsdaten erhaeltst du am ersten Arbeitstag per verschluesselter "
    "E-Mail an deine private Adresse - die IT versendet sie morgens vor 9:00 Uhr. "
    "Darin enthalten sind dein E-Mail-Konto, der Zugang zum Passwort-Manager (Bitwarden) "
    "und ein Erstanmelde-Link. Beim ersten Login wirst du aufgefordert, ein eigenes "
    "Passwort zu setzen und die Zwei-Faktor-Authentifizierung einzurichten. "
    "Alle weiteren Tool-Passwoerter findest du anschliessend im Passwort-Manager."
)

pdf.section("Was dich am ersten Tag erwartet")
pdf.keyval([
    ("09:00", "Begruessung durch People & Culture, Rundgang"),
    ("10:00", "IT-Setup: Laptop, Konten, VPN"),
    ("12:30", "Gemeinsames Team-Lunch (geht aufs Haus)"),
    ("14:00", "Kennenlernen mit deinem Buddy"),
    ("15:30", "Einrichtung deiner Tools, erste Umschau"),
])

# --- Ansprechpartner ---
pdf.add_page()
pdf.chapter("2. Dein Buddy & Ansprechpartner")
pdf.body(
    "In den ersten drei Monaten steht dir ein erfahrener Kollege als Buddy zur Seite - "
    "deine erste Anlaufstelle fuer alle kleinen und grossen Fragen. Wer dein Buddy ist, "
    "steht in deiner Willkommens-E-Mail und in deinem Profil im Intranet."
)
pdf.keyval([
    ("Buddy", "Dein persoenlicher Ansprechpartner fuer die ersten 3 Monate"),
    ("People & Culture", "Mara Lindqvist - mara@nordlicht.example (HR, Vertraege, Urlaub)"),
    ("IT-Support", "it@nordlicht.example oder Chat-Kanal #it-hilfe"),
    ("Dein Teamlead", "wird dir am ersten Tag vorgestellt"),
    ("Office Management", "office@nordlicht.example (Schluessel, Ausstattung)"),
])

pdf.section("Feedbackgespraeche")
pdf.body(
    "Regelmaessiges Feedback ist uns wichtig. Dein erstes Feedbackgespraech mit deinem "
    "Teamlead findet nach zwei Wochen statt. Weitere Gespraeche gibt es nach 30 Tagen, "
    "nach der Probezeit (3 Monate) und danach quartalsweise."
)

# --- Technik ---
pdf.add_page()
pdf.chapter("3. Technik & Tools einrichten")

pdf.section("VPN-Zugang einrichten")
pdf.body(
    "Fuer den Zugriff auf interne Systeme von unterwegs oder aus dem Homeoffice brauchst du "
    "den VPN-Zugang. So richtest du ihn ein:\n"
    "1. Installiere den WireGuard-Client (Link im Intranet unter 'IT > Downloads').\n"
    "2. Lade deine persoenliche Konfigurationsdatei aus dem Passwort-Manager (Eintrag "
    "'VPN-Config').\n"
    "3. Importiere die Datei in WireGuard und aktiviere die Verbindung.\n"
    "Bei Problemen hilft #it-hilfe oder it@nordlicht.example weiter."
)

pdf.section("Tools fuer den ersten Tag")
pdf.keyval([
    ("Kommunikation", "Slack (Chat), Gmail (E-Mail), Google Meet (Calls)"),
    ("Projektarbeit", "Notion (Doku & Aufgaben), Figma (Design)"),
    ("Zeiterfassung", "Clockodo (im Browser oder als App)"),
    ("Passwort-Manager", "Bitwarden (Pflicht fuer alle Konten)"),
    ("Dateiablage", "Google Drive (Team-Ordner werden vom Buddy freigegeben)"),
])

pdf.section("Zeiterfassung")
pdf.body(
    "Wir erfassen Arbeitszeiten in Clockodo. Du startest morgens den Timer und stoppst ihn "
    "zum Feierabend; Pausen werden automatisch beruecksichtigt. Projektzeiten ordnest du "
    "dem jeweiligen Kunden-Projekt zu. Trage deine Zeiten taeglich ein - das dauert keine "
    "zwei Minuten und erspart Nacharbeit am Monatsende."
)

# --- Erste Woche ---
pdf.add_page()
pdf.chapter("4. Deine erste Woche")
pdf.body(
    "Niemand erwartet, dass du sofort alles weisst. Deine erste Woche ist zum Ankommen da."
)
pdf.keyval([
    ("Tag 1", "Setup, Kennenlernen, Buddy"),
    ("Tag 2-3", "Einfuehrung in laufende Projekte, erste kleine Aufgaben"),
    ("Tag 4", "Teilnahme an den Team-Meetings, Tools vertiefen"),
    ("Tag 5", "Wochenrueckblick mit dem Buddy, offene Fragen klaeren"),
])

pdf.section("Wiederkehrende Termine")
pdf.keyval([
    ("Daily Standup", "taeglich 09:30, 15 Minuten (Team-Kanal)"),
    ("Team-Weekly", "montags 11:00"),
    ("Team-Kalender", "in Google Kalender unter 'Nordlicht - Team' (Buddy teilt ihn)"),
    ("All-Hands", "letzter Freitag im Monat, 15:00"),
])

pdf.section("Gut zu wissen")
pdf.body(
    "Fragen sind ausdruecklich erwuenscht - lieber einmal zu viel fragen als etwas raten. "
    "Die meisten Antworten findest du im Intranet (Notion-Bereich 'Onboarding'). "
    "Wenn etwas fehlt oder unklar ist, sag deinem Buddy Bescheid: So verbessern wir den "
    "Guide fuer die naechsten neuen Kolleginnen und Kollegen."
)

pdf.ln(6)
pdf.set_fill_color(240, 253, 244)
pdf.set_draw_color(*ACCENT)
pdf.rect(10, pdf.get_y(), 190, 32, "FD")
pdf.set_y(pdf.get_y() + 5)
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(22, 101, 52)
pdf.cell(0, 7, "Hinweis: Demo-Dokument", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(40, 120, 70)
pdf.multi_cell(
    0, 6,
    "Nordlicht Studios ist eine fiktive Firma fuer den Wissens-Assistenten auf desmond.autonomika.de.\n"
    "Alle Personen, Tools und Ablaeufe sind erfunden.",
    align="C"
)

pdf.output("/out/nordlicht_onboarding_demo.pdf")
print("nordlicht PDF erstellt.")
