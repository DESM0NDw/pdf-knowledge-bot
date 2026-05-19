from fpdf import FPDF
from fpdf.enums import XPos, YPos

class Doc(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(180, 180, 180)
        self.cell(0, 8, "Betriebshandbuch - Bella Vista Restaurants GmbH  |  Demo-Dokument", align="R")
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
        self.set_fill_color(180, 30, 30)
        self.rect(0, 0, 210, 297, "F")
        self.set_y(20)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(255, 220, 180)
        self.cell(0, 10, "DEMO-DOKUMENT - KI-Wissens-Bot Showcase", align="C")
        self.set_y(80)
        self.set_font("Helvetica", "B", 30)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "Bella Vista Restaurants", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        self.set_font("Helvetica", "", 16)
        self.set_text_color(255, 200, 160)
        self.cell(0, 10, "GmbH", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.set_font("Helvetica", "", 13)
        self.set_text_color(220, 180, 150)
        self.cell(0, 8, "Betriebshandbuch 2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(180, 130, 110)
        self.multi_cell(0, 7,
            "Fiktives Demo-Dokument fuer den PDF-Wissens-Bot.\n"
            "Alle Angaben, Personen und Preise sind erfunden.\n\n"
            'Beispielfragen:\n'
            '  "Welche Allergene hat das Tiramisu?"\n'
            '  "Wie wird das Trinkgeld aufgeteilt?"\n'
            '  "Was sind die Oeffnungszeiten am Wochenende?"',
            align="C")

    def chapter(self, title):
        self.ln(5)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(180, 30, 30)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(180, 30, 30)
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
            self.cell(65, 6, key + ":")
            self.set_font("Helvetica", "", 10)
            self.cell(0, 6, val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)


pdf = Doc()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.cover()

# --- Seite 2: Unternehmen ---
pdf.add_page()
pdf.chapter("1. Unternehmen & Standorte")
pdf.body(
    "Bella Vista Restaurants GmbH wurde 2015 in Muenchen gegruendet und betreibt "
    "fuenf italienische Restaurants in Deutschland. Wir stehen fuer authentische "
    "italienische Kueche, frische Zutaten und herzlichen Service."
)
pdf.kv([
    ("Hauptsitz", "Muenchen (Leopoldstrasse 42)"),
    ("Standorte", "Muenchen, Hamburg, Berlin, Koeln, Stuttgart"),
    ("Mitarbeiter gesamt", "ca. 85 (Kuche, Service, Verwaltung)"),
    ("Geschaeftsfuehrung", "Marco Ferretti (m.ferretti@bellavista.de)"),
    ("HR-Leitung", "Sandra Kohl (s.kohl@bellavista.de)"),
    ("Betriebsleitung", "Thomas Braun (t.braun@bellavista.de)"),
])

pdf.section("Oeffnungszeiten")
pdf.kv([
    ("Montag bis Freitag", "11:30 - 23:00 Uhr"),
    ("Samstag & Sonntag", "12:00 - 23:30 Uhr"),
    ("Kueche", "bis 30 Minuten vor Schliessung"),
    ("Feiertage", "12:00 - 22:00 Uhr (gesonderte Aushange beachten)"),
])

pdf.section("Werte & Leitbild")
pdf.body(
    "Frische zuerst: Wir verwenden ausschliesslich frische, saisonale Zutaten.\n"
    "Gastfreundschaft: Jeder Gast wird behandelt wie ein Gast bei uns zu Hause.\n"
    "Team: Wir unterstuetzen uns gegenseitig - Kueche und Service sind ein Team.\n"
    "Sauberkeit: Hygiene ist nicht verhandelbar."
)

# --- Seite 3: Schichten ---
pdf.add_page()
pdf.chapter("2. Schichtplanung & Arbeitszeiten")

pdf.section("Schichtmodelle")
pdf.kv([
    ("Fruehschicht (Service)", "10:00 - 16:00 Uhr"),
    ("Spaetschicht (Service)", "15:00 - 23:30 Uhr"),
    ("Doppelschicht", "10:00 - 23:30 Uhr (mit 1h Pause)"),
    ("Kueche Fruehdienst", "09:00 - 15:30 Uhr"),
    ("Kueche Spaetdienst", "14:30 - 23:30 Uhr"),
    ("Schichtuebergabe", "15 Minuten (Pflicht, wird bezahlt)"),
])

pdf.section("Schichtplanung")
pdf.body(
    "Der Schichtplan wird jeden Mittwoch fuer die darauffolgende Woche veroeffentlicht. "
    "Aenderungswuensche muessen bis Dienstag 12:00 Uhr beim Betriebsleiter eingereicht werden. "
    "Kurzfristige Tausche (weniger als 24h vorher) beduerfen der schriftlichen Genehmigung."
)
pdf.kv([
    ("Planveroeffentlichung", "Jeden Mittwoch fuer Folgewoche"),
    ("Aenderungsfrist", "Dienstag 12:00 Uhr"),
    ("Mindestbesetzung Service", "3 Personen pro Schicht"),
    ("Mindestbesetzung Kueche", "2 Personen pro Schicht"),
])

pdf.section("Verguetung")
pdf.kv([
    ("Mindestlohn Kueche", "14,50 Euro/Stunde"),
    ("Mindestlohn Service", "13,80 Euro/Stunde"),
    ("Nacht-Zuschlag (ab 22 Uhr)", "20% Aufschlag"),
    ("Sonn- & Feiertagszuschlag", "25% Aufschlag"),
    ("Ueberstunden", "Freizeitausgleich oder 125% Verguetung"),
    ("Gehaltsauszahlung", "Letzter Werktag des Monats"),
])

pdf.section("Mitarbeiterverpflegung")
pdf.body(
    "Jede Mitarbeiterin und jeder Mitarbeiter erhaelt pro Schicht eine kostenlose Mahlzeit "
    "aus dem Tagesangebot. Der Wert darf 8 Euro netto nicht uebersteigen. "
    "Getraenke (Wasser, Softdrinks) sind waehrend der Schicht kostenlos."
)
pdf.kv([
    ("Mahlzeit pro Schicht", "1x kostenlos (max. 8 Euro Wert)"),
    ("Getraenke", "Wasser & Softdrinks kostenlos"),
    ("Alkohol", "Nicht waehrend der Arbeitszeit erlaubt"),
])

# --- Seite 4: Speisekarte & Allergene ---
pdf.add_page()
pdf.chapter("3. Speisekarte & Preise")

pdf.section("Antipasti")
pdf.kv([
    ("Bruschetta al Pomodoro", "8,90 Euro"),
    ("Caprese (Bueffelmozzarella)", "12,50 Euro"),
    ("Antipasto Misto (fuer 2)", "18,90 Euro"),
    ("Vitello Tonnato", "14,50 Euro"),
])

pdf.section("Pasta")
pdf.kv([
    ("Spaghetti Carbonara", "15,50 Euro"),
    ("Penne all'Arrabbiata", "13,90 Euro"),
    ("Tagliatelle al Ragu", "16,90 Euro"),
    ("Gnocchi al Pesto", "14,50 Euro"),
    ("Linguine alle Vongole", "18,50 Euro"),
])

pdf.section("Pizza (alle 30 cm)")
pdf.kv([
    ("Margherita", "12,90 Euro"),
    ("Diavola (scharf)", "14,90 Euro"),
    ("Quattro Stagioni", "15,50 Euro"),
    ("Prosciutto e Funghi", "15,90 Euro"),
    ("Vegetariana", "14,50 Euro"),
    ("Calzone", "15,90 Euro"),
])

pdf.section("Desserts")
pdf.kv([
    ("Tiramisu (hausgemacht)", "7,90 Euro"),
    ("Panna Cotta", "6,90 Euro"),
    ("Tartufo al Cioccolato", "7,50 Euro"),
    ("Sorbetto (2 Kugeln)", "5,90 Euro"),
])

# --- Seite 5: Allergene ---
pdf.add_page()
pdf.chapter("4. Allergene & Zutaten")
pdf.body(
    "Alle Mitarbeiterinnen und Mitarbeiter muessen die Allergene der Hauptgerichte kennen. "
    "Bei Unklarheiten immer den Kuechen-Chef befragen. Gaste mit Allergien muessen an den "
    "Kuechen-Chef weitergeleitet werden."
)

pdf.section("Allergene - Pasta")
pdf.kv([
    ("Spaghetti Carbonara", "Gluten, Eier, Milch (Kaese), Schweinefleisch"),
    ("Penne all'Arrabbiata", "Gluten"),
    ("Tagliatelle al Ragu", "Gluten, Eier, Sellerie"),
    ("Gnocchi al Pesto", "Gluten, Eier, Nuesse (Pinienkerne), Milch"),
    ("Linguine alle Vongole", "Gluten, Weichtiere, Krebstiere"),
])

pdf.section("Allergene - Pizza")
pdf.kv([
    ("Margherita", "Gluten, Milch, Laktose"),
    ("Diavola", "Gluten, Milch, Laktose, Schweinefleisch"),
    ("Quattro Stagioni", "Gluten, Milch, Pilze"),
    ("Prosciutto e Funghi", "Gluten, Milch, Schweinefleisch"),
    ("Vegetariana", "Gluten, Milch, Laktose"),
])

pdf.section("Allergene - Desserts")
pdf.kv([
    ("Tiramisu", "Gluten, Milch, Eier, Laktose, Koffein (Espresso)"),
    ("Panna Cotta", "Milch, Laktose, Gelatine (Rind)"),
    ("Tartufo al Cioccolato", "Milch, Laktose, Kakao, Eier"),
    ("Sorbetto", "je nach Sorte: Fruchte (keine Milch, keine Gluten)"),
])
pdf.body("Hinweis: Unser Tiramisú wird taeglich frisch zubereitet und enthaelt rohe Eier.")

# --- Seite 6: Hygiene ---
pdf.add_page()
pdf.chapter("5. Hygiene & HACCP")
pdf.body(
    "Die Einhaltung der Hygienevorschriften nach HACCP (Hazard Analysis and Critical "
    "Control Points) ist fuer alle Mitarbeiterinnen und Mitarbeiter verbindlich. "
    "Verstösse werden dokumentiert und koennen arbeitsrechtliche Folgen haben."
)

pdf.section("Kuehltemperaturen")
pdf.kv([
    ("Frischware (Fleisch, Fisch)", "0 bis 4 Grad Celsius"),
    ("Milchprodukte", "2 bis 6 Grad Celsius"),
    ("Tiefgekuehltes", "mindestens -18 Grad Celsius"),
    ("Warmhaltung Speisen", "mindestens 65 Grad Celsius"),
    ("Temperaturkontrolle", "alle 2 Stunden, Eintrag ins HACCP-Heft"),
])

pdf.section("Koerperhygiene")
pdf.body(
    "Vor Arbeitsbeginn und nach jeder Pause gruendlich die Haende waschen (mind. 30 Sekunden). "
    "Bei Krankheitssymptomen (Durchfall, Erbrechen, infizierte Wunden) darf NICHT in der "
    "Kueche gearbeitet werden - sofort den Betriebsleiter informieren."
)
pdf.kv([
    ("Haendewaschen", "mind. 30 Sekunden, vor jedem Arbeitsabschnitt"),
    ("Haare", "zusammengebunden oder Haarnetz (Pflicht in der Kueche)"),
    ("Schmuck", "In der Kueche verboten"),
    ("Handschuhe", "Beim Schneiden von rohem Fleisch/Fisch Pflicht"),
])

pdf.section("Reinigungsplan")
pdf.kv([
    ("Arbeitsflaechein reinigen", "nach jedem Arbeitsabschnitt"),
    ("Kuehlschraenke", "wochentlich (Montag)"),
    ("Fritteuse", "taeglich nach Betrieb"),
    ("Boden Kueche", "nach jeder Schicht"),
    ("Gastraum", "taeglich vor Oeffnung"),
])

# --- Seite 7: Lieferanten ---
pdf.add_page()
pdf.chapter("6. Lieferanten & Bestellwesen")

pdf.section("Hauptlieferanten")
pdf.kv([
    ("Fisch & Meeresfruchte", "Meeresfruechte Richter GmbH (taeglich, 7 Uhr)"),
    ("Fleisch", "Metzgerei Huber KG (Mo/Mi/Fr, 6:30 Uhr)"),
    ("Gemuese & Kraeuter", "FreshDirect Bayern (Mo-Sa, 6 Uhr)"),
    ("Pasta & Trockenwaren", "Gustosi Italia Import GmbH (wochentlich, Montag)"),
    ("Milchprodukte", "Molkerei Allgaeu (taeglich, 7:30 Uhr)"),
    ("Getranke", "Getraenke Hoffmann GmbH (Dienstag & Freitag)"),
    ("Backwaren (Brot)", "Baeckerei Schmid (taeglich, 10 Uhr)"),
])

pdf.section("Bestellprozess")
pdf.body(
    "Bestellungen werden taeglich bis 14:00 Uhr fuer den naechsten Tag aufgegeben. "
    "Der Kuechen-Chef ist verantwortlich fuer den Lagerbestand und die Bestellmengen. "
    "Bei unerwarteten Lieferengpaessen sofort Marco Ferretti (Geschaeftsfuehrung) informieren."
)
pdf.kv([
    ("Bestellfrist", "Taeglich bis 14:00 Uhr fuer Folgetag"),
    ("Mindestbestand", "Fuer 2 Tage Betrieb immer vorhanden"),
    ("Lieferscheine", "Original ins Buero, Kopie in die Kueche"),
            ("Reklamation", "Sofort bei Lieferung dokumentieren, Foto machen"),
])

# --- Seite 8: Trinkgeld & Service ---
pdf.add_page()
pdf.chapter("7. Trinkgeld & Gastservice")

pdf.section("Trinkgeldverteilung")
pdf.body(
    "Das Trinkgeld wird am Ende jeder Schicht ehrlich zwischen Service und Kueche aufgeteilt. "
    "Die Aufteilung gilt als verbindliche Betriebsvereinbarung."
)
pdf.kv([
    ("Serviceanteil", "70% des gesamten Trinkgelds der Schicht"),
    ("Kuchenanteil", "30% des gesamten Trinkgelds der Schicht"),
    ("Verteilung Service", "Gleichmaessig auf alle Servicekraefte der Schicht"),
    ("Verteilung Kueche", "Gleichmaessig auf alle Kuechen-Mitarbeiter"),
    ("Auszahlung", "Bar am Ende der Schicht durch Schichtleiter"),
])

pdf.section("Beschwerdemanagement")
pdf.body(
    "Reklamationen werden ernst genommen und nach dem 5-Minuten-Prinzip bearbeitet: "
    "innerhalb von 5 Minuten muss eine Loesung angeboten werden."
)
pdf.kv([
    ("Schritt 1", "Zuhören, nicht unterbrechen"),
    ("Schritt 2", "Aufrichtig entschuldigen"),
    ("Schritt 3", "Loesung anbieten (Ersatz, Rabatt oder kostenlos)"),
    ("Schritt 4", "Kuechen-Chef informieren"),
    ("Schritt 5", "Im Reklamationsbuch dokumentieren"),
    ("Bearbeitungszeit", "max. 5 Minuten bis zur ersten Loesungsangebot"),
])
pdf.body("Bei aggressiven Gaesten sofort den Schichtleiter rufen. Niemals alleine eskalieren.")

pdf.section("Reservierungen")
pdf.kv([
    ("System", "ReservierungsTool Plus (Tablet an der Theke)"),
    ("Maximal-Groesse ohne Vorankuendigung", "8 Personen"),
    ("Gruppen ab 9 Personen", "mind. 48h vorher, Vorkasse 20%"),
    ("No-Show Regelung", "Erinnerungs-SMS 2h vorher, nach 15 Min. Tisch freigeben"),
])

pdf.output("/out/bellavista_betriebshandbuch_demo.pdf")
print("Bella Vista PDF erstellt.")
