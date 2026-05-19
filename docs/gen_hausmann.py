from fpdf import FPDF
from fpdf.enums import XPos, YPos

class Doc(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(180, 180, 180)
        self.cell(0, 8, "Mitarbeiterhandbuch - Hausmann & Partner Immobilien GmbH  |  Demo-Dokument", align="R")
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
        self.set_fill_color(20, 40, 80)
        self.rect(0, 0, 210, 297, "F")
        self.set_y(20)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(180, 210, 255)
        self.cell(0, 10, "DEMO-DOKUMENT - KI-Wissens-Bot Showcase", align="C")
        self.set_y(80)
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(255, 255, 255)
        self.cell(0, 14, "Hausmann & Partner", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        self.set_font("Helvetica", "", 16)
        self.set_text_color(180, 210, 255)
        self.cell(0, 10, "Immobilien GmbH", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.set_font("Helvetica", "", 13)
        self.set_text_color(140, 170, 220)
        self.cell(0, 8, "Mitarbeiterhandbuch 2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 140, 190)
        self.multi_cell(0, 7,
            "Fiktives Demo-Dokument fuer den PDF-Wissens-Bot.\n"
            "Alle Angaben, Personen und Zahlen sind erfunden.\n\n"
            "Beispielfragen:\n"
            '  "Wie hoch ist die Maklerprovision beim Kauf?"\n'
            '  "Welche Unterlagen brauche ich fuer den Verkauf?"\n'
            '  "Wie schnell antworten wir auf Anfragen?"',
            align="C")

    def chapter(self, title):
        self.ln(5)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(20, 60, 140)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(20, 60, 140)
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

    def kv(self, items):
        for key, val in items:
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(60, 60, 60)
            self.cell(70, 6, key + ":")
            self.set_font("Helvetica", "", 10)
            self.cell(0, 6, val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)


pdf = Doc()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.cover()

# --- Seite 2: Unternehmen ---
pdf.add_page()
pdf.chapter("1. Unternehmen & Team")
pdf.body(
    "Hausmann & Partner Immobilien GmbH wurde 2008 in Frankfurt am Main gegruendet. "
    "Wir vermitteln Wohn- und Gewerbeimmobilien in der DACH-Region und gehoeren zu den "
    "fuenf groessten unabhaengigen Maklerhaeusern in Hessen. Unser Anspruch: transparente "
    "Beratung, marktgerechte Preise und persoenlicher Service."
)
pdf.kv([
    ("Hauptsitz", "Frankfurt am Main (Bockenheimer Landstr. 18)"),
    ("Weitere Standorte", "Muenchen, Duesseldorf"),
    ("Mitarbeiter", "38 (Makler, Backoffice, IT, Marketing)"),
    ("Geschaeftsfuehrung", "Klaus Hausmann & Petra Voss"),
    ("HR", "Miriam Koehler (m.koehler@hausmann-immobilien.de)"),
    ("IT-Support", "it@hausmann-immobilien.de"),
    ("CRM-System", "Propstack (propstack.com)"),
])

pdf.section("Kernwerte")
pdf.body(
    "Transparenz: Wir kommunizieren Preise, Provisionssaetze und Prozesse klar.\n"
    "Marktkenntnis: Wir kennen unsere lokalen Maerkte besser als jeder andere.\n"
    "Schnelligkeit: Anfragen werden innerhalb von 4 Stunden beantwortet.\n"
    "Diskretion: Verkaufsabsichten und Kundendaten behandeln wir streng vertraulich."
)

# --- Seite 3: Provision ---
pdf.add_page()
pdf.chapter("2. Provision & Gebuehren")
pdf.body(
    "Die Maklerprovision ist gesetzlich geregelt und wird transparent kommuniziert. "
    "Seit der Gesetzesaenderung 2020 teilen Kaeufer und Verkaeufer die Provision gleich auf."
)

pdf.section("Kaufimmobilien")
pdf.kv([
    ("Provision Kaeufer", "3,57% des Kaufpreises (inkl. 19% MwSt.)"),
    ("Provision Verkaeufer", "3,57% des Kaufpreises (inkl. 19% MwSt.)"),
    ("Gesamtprovision", "7,14% des Kaufpreises"),
    ("Faelligkeit", "Bei notariellem Vertragsabschluss"),
    ("Mindestprovision", "5.000 Euro pro Seite"),
])

pdf.section("Mietimmobilien")
pdf.kv([
    ("Provision Mieter", "2 Nettokaltmieten + 19% MwSt."),
    ("Provision Vermieter", "Verhandlungssache (meist 1-2 Nettokaltmieten)"),
    ("Faelligkeit", "Bei Mietvertragsunterzeichnung"),
    ("Wohnflaeche ab 80qm", "Sonderkonditionen moeglich - Ruecksprache mit GL"),
])

pdf.section("Gewerbeobjekte")
pdf.kv([
    ("Kauf Gewerbe", "4,76% des Kaufpreises (inkl. MwSt.) pro Seite"),
    ("Miete Gewerbe", "3 Nettokaltmieten + MwSt."),
    ("Projektentwicklung", "Individuelle Vereinbarung, mind. 2% vom Projektwert"),
])

pdf.section("Bewertungskosten")
pdf.kv([
    ("Marktpreiseinschaetzung", "Kostenlos fuer potenzielle Auftraggeber"),
    ("Zertifiziertes Gutachten", "Ab 800 Euro (externer Gutachter)"),
    ("Energieausweis", "Verweis an zertifizierten Aussteller (150-500 Euro)"),
])

# --- Seite 4: Verkaufsprozess ---
pdf.add_page()
pdf.chapter("3. Verkaufsprozess")
pdf.body(
    "Der typische Immobilienverkauf dauert von der Bewertung bis zum Notartermin "
    "zwischen 4 und 12 Wochen. Folgende Schritte sind verbindlich einzuhalten."
)

pdf.kv([
    ("Schritt 1", "Erstberatung & Bewertung (kostenlos, 1-2 Stunden)"),
    ("Schritt 2", "Alleinauftrag unterzeichnen (Laufzeit: 6 Monate)"),
    ("Schritt 3", "Unterlagen zusammenstellen (1-2 Wochen)"),
    ("Schritt 4", "Exposee erstellen & Fotos (professioneller Fotograf, kostenlos)"),
    ("Schritt 5", "Vermarktung: Immoscout, Immowelt, eigene Website"),
    ("Schritt 6", "Besichtigungen koordinieren & durchfuehren"),
    ("Schritt 7", "Kaufpreisverhandlung & Bonititaetspruefung"),
    ("Schritt 8", "Notartermin vorbereiten & begleiten"),
    ("Schritt 9", "Uebergabe & Schluesseluebergabe"),
])

pdf.section("Besichtigungen")
pdf.kv([
    ("Dauer pro Besichtigung", "30 bis 45 Minuten"),
    ("Antwortzeit auf Anfragen", "Innerhalb von 4 Stunden (Pflicht)"),
    ("Gruppen-Besichtigung", "Moeglich bei hoher Nachfrage, max. 4 Parteien"),
    ("Protokoll", "Nach jeder Besichtigung ins Propstack eintragen"),
    ("Feedback an Verkaeufer", "Innerhalb von 24h nach Besichtigung"),
])

pdf.section("Typische Verkaufsdauer")
pdf.kv([
    ("Gefragte Wohnlage", "4 bis 6 Wochen"),
    ("Durchschnittliche Lage", "6 bis 10 Wochen"),
    ("Schwierige Objekte", "10 bis 16 Wochen"),
    ("Luxussegment (ab 1 Mio.)", "3 bis 9 Monate"),
])

# --- Seite 5: Unterlagen ---
pdf.add_page()
pdf.chapter("4. Erforderliche Unterlagen")

pdf.section("Pflichtunterlagen Verkauf")
pdf.body("Folgende Unterlagen muessen vor der Vermarktung vollstaendig vorliegen:")
pdf.kv([
    ("Grundbuchauszug", "Nicht aelter als 3 Monate (Grundbuchamt)"),
    ("Energieausweis", "Pflicht seit 2014, Ausstellung durch Energieberater"),
    ("Bauplaene & Grundrisse", "Vom Bauamt oder Architekten"),
    ("Wohnflaechen-berechnung", "Nach DIN 277 oder Wohnflaechen-VO"),
    ("Lageplan", "Aktueller Katasterauszug"),
    ("Teilungserklaerung", "Nur bei Eigentumswohnungen"),
    ("Protokolle Eigentuemer-versammlung", "Letzte 3 Jahre (bei ETW)"),
    ("Mietvertraege", "Bei vermieteten Objekten"),
])

pdf.section("Notartermin Vorbereitung")
pdf.body(
    "Der Kaufvertrag wird vom Notar (Wahl des Kaeufers) aufgesetzt. "
    "Wir koordinieren den Termin und begleiten beide Parteien. "
    "Notarkosten traegt der Kaeufer (ca. 1,5% des Kaufpreises)."
)
pdf.kv([
    ("Vorlaufzeit Notartermin", "Mind. 2 Wochen nach Kaufpreiseinigung"),
    ("Kaufvertragsentwurf", "3 Werktage vor Termin an beide Parteien"),
    ("Eigenkapitalnachweis", "Vorab per E-Mail an Notar"),
    ("Grunderwerbsteuer Hessen", "6,0% des Kaufpreises"),
])

# --- Seite 6: Vermietung ---
pdf.add_page()
pdf.chapter("5. Vermietungsprozess")
pdf.body(
    "Bei der Vermietung sind die Anforderungen an Bewerber seit der Mietpreisbremse "
    "und den DSGVO-Regelungen gestiegen. Alle Interessenten werden gleich behandelt."
)

pdf.section("Mietinteressenten-Pruefung")
pdf.kv([
    ("SCHUFA-Auskunft", "Selbstauskunft des Mieters (Pflicht)"),
    ("Einkommensnachweis", "3 aktuelle Gehaltsabrechnungen"),
    ("Mietschuldenfreiheits-bescheinigung", "Vom Vorvermieter"),
    ("Faustregel Miete/Einkommen", "Kaltmiete max. 30% des Netto-Einkommens"),
    ("Haustiere", "Nur mit schriftlicher Genehmigung des Vermieters"),
])

pdf.section("Mietkaution")
pdf.kv([
    ("Maximale Kaution", "3 Nettokaltmieten (gesetzlich)"),
    ("Zahlungszeitpunkt", "Bei Schluesseleruebergabe"),
    ("Kautionskonto", "Separates, verzinsliches Konto des Vermieters"),
    ("Rueckzahlung", "Innerhalb von 6 Monaten nach Auszug"),
])

pdf.section("Pflichten des Maklers")
pdf.body(
    "Bei der Vermietung gelten zusaetzlich die Regelungen des Bestellerprinzips: "
    "Wer den Makler beauftragt, zahlt die Provision. In der Regel ist das der Vermieter."
)

# --- Seite 7: Tools & Datenschutz ---
pdf.add_page()
pdf.chapter("6. Tools, IT & Datenschutz")

pdf.section("Software-Uebersicht")
pdf.kv([
    ("CRM & Objekte", "Propstack (propstack.com) - Hauptsystem"),
    ("Kommunikation intern", "Microsoft Teams"),
    ("E-Mail", "Outlook (Exchange Server)"),
    ("Dokumente", "SharePoint / OneDrive"),
    ("E-Signatur", "DocuSign (fuer Auftraege & Vertraege)"),
    ("Marktanalyse", "VALUE Marktdaten"),
    ("Foto-Bearbeitung", "Lightroom (Lizenz ueber IT)"),
    ("Grundriss-Zeichnung", "Floorplanner (Online-Tool)"),
])

pdf.section("Datenschutz DSGVO")
pdf.body(
    "Alle Kunden- und Objektdaten sind vertraulich zu behandeln. "
    "Die Weitergabe an Dritte ist ohne schriftliche Einwilligung verboten. "
    "Datenschutzbeauftragter: Dr. Felix Bauer (datenschutz@hausmann-immobilien.de)"
)
pdf.kv([
    ("Datenspeicherung", "Ausschliesslich in Propstack oder SharePoint"),
    ("Private Geraete", "Kundendaten duerfen NICHT auf privaten Geraeten gespeichert werden"),
    ("Loeschfristen", "Interessentendaten: 6 Monate, Abschlussunterlagen: 10 Jahre"),
    ("Datenpanne melden", "Sofort an Datenschutzbeauftragten und IT"),
])

pdf.section("Erreichbarkeit & Reaktionszeiten")
pdf.kv([
    ("Anfragen (E-Mail/Portal)", "Antwort innerhalb von 4 Stunden (Pflicht)"),
    ("Telefonische Erreichbarkeit", "Mo-Fr 8:30-18:00 Uhr, Sa 10:00-14:00 Uhr"),
    ("Ausserhalb Geschaeftszeiten", "Anrufbeantworter, Rueckruf am naechsten Werktag"),
    ("Urlaubsvertretung", "Pflicht: Abwesenheitsnotiz + Vertreter benennen"),
])

pdf.output("/out/hausmann_handbuch_demo.pdf")
print("Hausmann PDF erstellt.")
