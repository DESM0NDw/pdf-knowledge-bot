from fpdf import FPDF
from fpdf.enums import XPos, YPos

ACCENT = (234, 88, 12)  # orange — Sales-Enablement

class Doc(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(180, 180, 180)
        self.cell(0, 8, "VoltEdge Solar - Vertriebsunterlage  |  Demo-Dokument", align="R")
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
        self.cell(0, 15, "VoltEdge Solar", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.set_font("Helvetica", "", 18)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, "Produkt- & Preisuebersicht (Vertrieb)", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(100, 116, 139)
        self.multi_cell(
            0, 7,
            "VoltEdge ist ein fiktiver Anbieter von Solaranlagen. Diese Unterlage dient als\n"
            "Demo fuer den Use Case 'Sales-Enablement'. Alle Specs und Preise sind erfunden.\n"
            "Stell dem Assistenten direkt eine Frage - zum Beispiel:\n\n"
            '  "Welche Rabatte gibt es bei Jahreszahlung?"\n'
            '  "Wie hoch ist die Leistungsgarantie?"\n'
            '  "Laesst sich ein Speicher nachruesten?"',
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
            self.cell(70, 6, key + ":")
            self.set_font("Helvetica", "", 10)
            self.multi_cell(0, 6, val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)


pdf = Doc()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.cover()

# --- Produkt ---
pdf.add_page()
pdf.chapter("1. Produktuebersicht")
pdf.body(
    "Die VoltEdge-Serie umfasst drei Komplettpakete fuer Eigenheime - vom kompakten "
    "Einstieg bis zur Anlage mit Speicher. Alle Pakete enthalten Module, Wechselrichter, "
    "Montage und Inbetriebnahme."
)
pdf.keyval([
    ("VoltEdge Start", "4,0 kWp - 10 Module, ohne Speicher - ab 7.900 EUR"),
    ("VoltEdge Plus", "8,0 kWp - 20 Module, 5 kWh Speicher - ab 15.400 EUR"),
    ("VoltEdge Max", "12,0 kWp - 30 Module, 10 kWh Speicher - ab 22.800 EUR"),
])
pdf.body(
    "Alle Preise verstehen sich inkl. Lieferung, Montage und Inbetriebnahme, zzgl. "
    "gesetzlicher MwSt. Fuer private Photovoltaikanlagen gilt in Deutschland aktuell "
    "der Nullsteuersatz (0 Prozent MwSt.)."
)

pdf.section("Technische Eckdaten")
pdf.keyval([
    ("Modul-Wirkungsgrad", "bis 22,3 Prozent (Monokristallin, Halbzellen)"),
    ("Wechselrichter", "Hybrid-Wechselrichter, speicherfaehig"),
    ("Speicher", "Lithium-Eisenphosphat (LiFePO4), modular erweiterbar"),
    ("Notstromfaehig", "optional (Backup-Box, +890 EUR)"),
])

# --- Garantie ---
pdf.add_page()
pdf.chapter("2. Garantie & Leistung")

pdf.section("Garantieleistungen")
pdf.keyval([
    ("Produktgarantie Module", "25 Jahre"),
    ("Leistungsgarantie Module", "mind. 87 Prozent Leistung nach 25 Jahren"),
    ("Garantie Wechselrichter", "12 Jahre (auf 20 Jahre verlaengerbar)"),
    ("Garantie Speicher", "10 Jahre oder 6.000 Ladezyklen"),
    ("Montagegarantie", "5 Jahre auf die Installation"),
])
pdf.body(
    "Die Leistungsgarantie sichert zu, dass die Module auch nach 25 Jahren noch mindestens "
    "87 Prozent ihrer Nennleistung erbringen. Tritt ein Garantiefall ein, uebernehmen wir "
    "Austausch und Arbeitszeit."
)

pdf.section("Speicher nachruesten")
pdf.body(
    "Alle Pakete nutzen einen speicherfaehigen Hybrid-Wechselrichter. Das Start-Paket "
    "(ohne Speicher) laesst sich daher jederzeit mit einem Batteriespeicher nachruesten - "
    "ohne den Wechselrichter zu tauschen. Auch bestehende Speicher koennen modular von "
    "5 kWh auf bis zu 15 kWh erweitert werden. Eine Nachruestung dauert in der Regel "
    "einen halben Tag."
)

# --- Konditionen ---
pdf.add_page()
pdf.chapter("3. Preise, Rabatte & Foerderung")

pdf.section("Rabatte")
pdf.keyval([
    ("Jahreszahlung / Komplettzahlung", "3 Prozent Skonto bei Zahlung binnen 14 Tagen"),
    ("Mengenrabatt ab 5 Anlagen", "5 Prozent (z.B. Bautraeger, Hausverwaltungen)"),
    ("Mengenrabatt ab 10 Anlagen", "8 Prozent, individuelle Konditionen auf Anfrage"),
    ("Empfehlungsbonus", "250 EUR pro vermittelter, realisierter Anlage"),
])

pdf.section("Finanzierung")
pdf.body(
    "Auf Wunsch vermitteln wir eine Finanzierung ueber unseren Partner ab 3,9 Prozent "
    "effektivem Jahreszins, Laufzeiten von 24 bis 120 Monaten. Eine Anzahlung ist nicht "
    "erforderlich."
)

pdf.section("Foerderung")
pdf.body(
    "Foerderungen variieren je nach Bundesland und Kommune. Bundesweit ist die "
    "Einspeiseverguetung nach EEG relevant; viele Kommunen foerdern zusaetzlich Speicher. "
    "Wir pruefen die konkrete Foerderlage zur jeweiligen Postleitzahl im Angebot und "
    "unterstuetzen bei der Antragstellung. Der Nullsteuersatz (0 Prozent MwSt.) gilt "
    "bundesweit fuer private Anlagen."
)

# --- Ablauf ---
pdf.add_page()
pdf.chapter("4. Lieferung, Installation & Wartung")

pdf.section("Lieferzeit & Installation")
pdf.keyval([
    ("Lieferzeit", "in der Regel 4 bis 6 Wochen ab Auftrag"),
    ("Installationsdauer", "1 bis 2 Werktage (je nach Paket und Dach)"),
    ("Geruest", "im Preis enthalten"),
    ("Anmeldung Netzbetreiber", "uebernehmen wir komplett"),
    ("Inbetriebnahme", "am letzten Installationstag inkl. Einweisung"),
])

pdf.section("Wartung & Service")
pdf.keyval([
    ("Wartungsvertrag", "optional, 149 EUR pro Jahr"),
    ("Inhalt", "jaehrliche Sichtpruefung, Ertragscheck, Software-Updates"),
    ("Monitoring-App", "kostenlos, Ertrag und Verbrauch in Echtzeit"),
    ("Stoerungs-Hotline", "Mo-Fr 8-18 Uhr, Reaktionszeit 48 Stunden"),
])

pdf.section("Haeufige Einwaende - kurze Antworten")
pdf.body(
    "'Lohnt sich das bei wenig Sonne?' - Auch in Deutschland amortisieren sich Anlagen "
    "typisch in 9 bis 12 Jahren; die Module liefern 25+ Jahre.\n"
    "'Was bei einem Umzug?' - Die Anlage steigert den Immobilienwert; ein Mitnehmen ist "
    "technisch moeglich, aber selten wirtschaftlich.\n"
    "'Brauche ich ein neues Dach?' - Bei Dachalter ueber 30 Jahren empfehlen wir eine "
    "Pruefung; unser Team beraet kostenlos vor Ort."
)

pdf.ln(4)
pdf.set_fill_color(255, 247, 237)
pdf.set_draw_color(*ACCENT)
pdf.rect(10, pdf.get_y(), 190, 30, "FD")
pdf.set_y(pdf.get_y() + 4)
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(154, 52, 18)
pdf.cell(0, 7, "Hinweis: Demo-Dokument", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(150, 70, 30)
pdf.multi_cell(
    0, 6,
    "VoltEdge Solar ist ein fiktiver Anbieter fuer den Wissens-Assistenten auf desmond.autonomika.de.\n"
    "Alle Produkte, Specs und Preise sind erfunden.",
    align="C"
)

pdf.output("/out/voltedge_datenblatt_demo.pdf")
print("voltedge PDF erstellt.")
