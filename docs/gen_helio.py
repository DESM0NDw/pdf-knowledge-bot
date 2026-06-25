from fpdf import FPDF
from fpdf.enums import XPos, YPos

ACCENT = (59, 130, 246)  # blue — Kundensupport

class Doc(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(180, 180, 180)
        self.cell(0, 8, "Helio - Hilfe-Center  |  Demo-Dokument", align="R")
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
        self.cell(0, 15, "Helio", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.set_font("Helvetica", "", 18)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, "Hilfe-Center & Benutzerhandbuch", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(100, 116, 139)
        self.multi_cell(
            0, 7,
            "Helio ist ein fiktives Projektmanagement-Tool. Dieses Hilfe-Center dient als\n"
            "Demo fuer den Use Case 'Kundensupport'. Alle Funktionen und Preise sind erfunden.\n"
            "Stell dem Assistenten direkt eine Frage - zum Beispiel:\n\n"
            '  "Wie setze ich mein Passwort zurueck?"\n'
            '  "Welche Plaene gibt es und was kosten sie?"\n'
            '  "Unterstuetzt Helio Zwei-Faktor-Authentifizierung?"',
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

# --- Konto & Zugang ---
pdf.add_page()
pdf.chapter("1. Konto & Anmeldung")

pdf.section("Passwort zuruecksetzen")
pdf.body(
    "Falls du dein Passwort vergessen hast, klicke auf der Anmeldeseite auf 'Passwort "
    "vergessen?'. Gib deine E-Mail-Adresse ein und du erhaeltst innerhalb weniger Minuten "
    "einen Link zum Zuruecksetzen. Der Link ist aus Sicherheitsgruenden 60 Minuten gueltig. "
    "Nach dem Zuruecksetzen wirst du automatisch von allen aktiven Sitzungen abgemeldet."
)

pdf.section("Zwei-Faktor-Authentifizierung (2FA)")
pdf.body(
    "Helio unterstuetzt Zwei-Faktor-Authentifizierung ueber Authenticator-Apps "
    "(z.B. Google Authenticator, Authy, 1Password). Du aktivierst 2FA unter "
    "Einstellungen > Sicherheit > Zwei-Faktor-Authentifizierung. Beim Aktivieren "
    "erhaeltst du 10 einmalige Backup-Codes - bewahre diese sicher auf. "
    "Im Business- und Enterprise-Plan kann 2FA fuer alle Teammitglieder verpflichtend "
    "gemacht werden."
)

pdf.section("Single Sign-On (SSO)")
pdf.body(
    "SSO via SAML 2.0 und Google Workspace ist im Enterprise-Plan verfuegbar. "
    "Die Einrichtung erfolgt durch einen Workspace-Administrator unter "
    "Einstellungen > Sicherheit > SSO."
)

# --- Team ---
pdf.add_page()
pdf.chapter("2. Team & Zusammenarbeit")

pdf.section("Teammitglieder einladen")
pdf.body(
    "Als Workspace-Administrator ladst du neue Mitglieder unter 'Team > Mitglied einladen' "
    "per E-Mail ein. Du kannst mehrere Adressen auf einmal eingeben (kommagetrennt). "
    "Eingeladene erhalten eine E-Mail mit einem Beitritts-Link, der 7 Tage gueltig ist. "
    "Offene Einladungen siehst du jederzeit in der Team-Uebersicht und kannst sie erneut "
    "senden oder zurueckziehen."
)

pdf.section("Rollen & Berechtigungen")
pdf.keyval([
    ("Administrator", "Voller Zugriff inkl. Abrechnung, Team- und Sicherheitseinstellungen"),
    ("Mitglied", "Projekte erstellen und bearbeiten, eigene Aufgaben verwalten"),
    ("Gast", "Nur Lesezugriff auf explizit freigegebene Projekte"),
])
pdf.body(
    "Die Rolle laesst sich jederzeit in der Team-Uebersicht aendern. Die Anzahl der "
    "Mitglieder richtet sich nach deinem Plan (siehe Kapitel 4)."
)

# --- Daten ---
pdf.add_page()
pdf.chapter("3. Projekte & Daten")

pdf.section("Projektdaten exportieren")
pdf.body(
    "Du kannst deine Projektdaten jederzeit exportieren unter "
    "Projekt > Einstellungen > Export. Verfuegbare Formate sind CSV und JSON. "
    "Ein vollstaendiger Workspace-Export (alle Projekte als ZIP) ist im Business- und "
    "Enterprise-Plan verfuegbar und wird per E-Mail-Link bereitgestellt, sobald er fertig "
    "ist. Exporte enthalten alle Aufgaben, Kommentare und Anhaenge."
)

pdf.section("Integrationen & API")
pdf.body(
    "Helio bietet eine REST-API sowie Webhooks ab dem Pro-Plan. Einen API-Token erstellst "
    "du unter Einstellungen > Entwickler > API-Tokens. Die vollstaendige API-Dokumentation "
    "findest du unter developers.helio.example. Fertige Integrationen gibt es u.a. fuer "
    "Slack, GitHub, Google Kalender und Zapier."
)

pdf.section("Datensicherung")
pdf.body(
    "Alle Daten werden automatisch taeglich gesichert und auf Servern in der EU (Frankfurt) "
    "gespeichert. Geloeschte Projekte landen 30 Tage im Papierkorb und koennen in diesem "
    "Zeitraum wiederhergestellt werden."
)

# --- Abo ---
pdf.add_page()
pdf.chapter("4. Plaene, Preise & Abrechnung")

pdf.section("Verfuegbare Plaene")
pdf.keyval([
    ("Free", "0 EUR - bis 3 Mitglieder, 2 aktive Projekte, 500 MB Speicher"),
    ("Pro", "9 EUR/Monat pro Mitglied - unbegrenzte Projekte, API, 10 GB/Mitglied"),
    ("Business", "18 EUR/Monat pro Mitglied - 2FA-Pflicht, Workspace-Export, 100 GB"),
    ("Enterprise", "individuell - SSO, SLA, dedizierter Ansprechpartner"),
])
pdf.body(
    "Bei jaehrlicher Zahlung sparst du 20 Prozent gegenueber der monatlichen Abrechnung. "
    "Der Wechsel zwischen Plaenen ist jederzeit moeglich; die Differenz wird anteilig "
    "verrechnet."
)

pdf.section("Abo kuendigen")
pdf.body(
    "Du kannst dein Abo jederzeit unter Einstellungen > Abrechnung > Abo kuendigen beenden. "
    "Die Kuendigung wird zum Ende des laufenden Abrechnungszeitraums wirksam - bis dahin "
    "bleibt dein Plan voll nutzbar. Nach Ablauf wird das Konto automatisch auf den "
    "Free-Plan zurueckgestuft, deine Daten bleiben erhalten."
)

pdf.section("Zahlungsmethoden")
pdf.keyval([
    ("Akzeptiert", "Kreditkarte (Visa, Mastercard, Amex), SEPA-Lastschrift"),
    ("Rechnung", "Auf Anfrage ab Business-Plan"),
    ("Rechnungen", "Jederzeit als PDF unter Einstellungen > Abrechnung"),
])

# --- Support ---
pdf.add_page()
pdf.chapter("5. Support kontaktieren")
pdf.body(
    "Unser Support-Team hilft dir gerne weiter. Die Antwortzeiten richten sich nach deinem "
    "Plan."
)
pdf.keyval([
    ("E-Mail", "support@helio.example (alle Plaene)"),
    ("Live-Chat", "im Produkt unten rechts (Pro und hoeher)"),
    ("Telefon", "+49 30 000 000 (Enterprise)"),
    ("Antwortzeit Free/Pro", "innerhalb von 24 Stunden (werktags)"),
    ("Antwortzeit Business", "innerhalb von 4 Stunden (werktags)"),
    ("Antwortzeit Enterprise", "1 Stunde, mit SLA"),
    ("Statusseite", "status.helio.example"),
])

pdf.ln(6)
pdf.set_fill_color(239, 246, 255)
pdf.set_draw_color(*ACCENT)
pdf.rect(10, pdf.get_y(), 190, 32, "FD")
pdf.set_y(pdf.get_y() + 5)
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(30, 64, 120)
pdf.cell(0, 7, "Hinweis: Demo-Dokument", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(60, 90, 140)
pdf.multi_cell(
    0, 6,
    "Helio ist ein fiktives Produkt fuer den Wissens-Assistenten auf desmond.autonomika.de.\n"
    "Alle Funktionen, Preise und Kontaktdaten sind erfunden.",
    align="C"
)

pdf.output("/out/helio_hilfecenter_demo.pdf")
print("helio PDF erstellt.")
