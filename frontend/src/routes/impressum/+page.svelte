<svelte:head>
  <title>Impressum – PDF Wissens-Bot</title>
</svelte:head>

<div class="wrapper">
  <div class="content">
    <a href="/" class="back">&larr; Zurück zur Demo</a>

    <h1>Impressum</h1>
    <p>Angaben gemäß §5 TMG</p>

    <section>
      <h2>Verantwortlich</h2>
      <p>
        Desmond Wong<br>
        Lichtenbroicher Weg 29<br>
        40472 Düsseldorf<br>
        Deutschland
      </p>
      <p>E-Mail: <a href="mailto:desmond.wong.dev@proton.me">desmond.wong.dev@proton.me</a></p>
    </section>

    <hr>

    <h1>Datenschutzerklärung</h1>

    <section>
      <h2>Verantwortlicher</h2>
      <p>Desmond Wong, Lichtenbroicher Weg 29, 40472 Düsseldorf<br>
      E-Mail: <a href="mailto:desmond.wong.dev@proton.me">desmond.wong.dev@proton.me</a></p>
    </section>

    <section>
      <h2>Erhobene Daten</h2>
      <p>Diese Website setzt keine Tracking-Cookies und verwendet keine Analyse-Tools. Es werden keine personenbezogenen Nutzerdaten dauerhaft gespeichert.</p>
      <p>Beim Besuch der Website werden durch den Webserver technische Zugriffsdaten (IP-Adresse, Zeitstempel, aufgerufene Seite) im Rahmen normaler Server-Logs kurzfristig verarbeitet.</p>
    </section>

    <section>
      <h2>Nutzung der KI-Funktion (Chat)</h2>
      <p>Die Chat-Funktion dieser Demo verarbeitet die eingegebenen Fragen zur Beantwortung. Eingaben werden an die Groq Cloud API (Groq Inc., 101 2nd St, San Francisco, CA 94105, USA) übermittelt. Groq verarbeitet die Anfragen auf US-amerikanischen Servern. Es werden keine Nachrichten dauerhaft gespeichert. Die Übermittlung erfolgt verschlüsselt (HTTPS).</p>
      <p>Bitte geben Sie in der Chat-Funktion keine personenbezogenen Daten ein.</p>
    </section>

    <section>
      <h2>Ihre Rechte</h2>
      <p>Sie haben jederzeit das Recht auf Auskunft, Berichtigung, Löschung und Einschränkung der Verarbeitung Ihrer personenbezogenen Daten sowie das Recht auf Datenübertragbarkeit. Wenden Sie sich dazu an: <a href="mailto:desmond.wong.dev@proton.me">desmond.wong.dev@proton.me</a></p>
      <p>Beschwerden können Sie bei der zuständigen Aufsichtsbehörde einreichen: Landesbeauftragte für Datenschutz und Informationsfreiheit Nordrhein-Westfalen (<a href="https://www.ldi.nrw.de" target="_blank" rel="noopener">ldi.nrw.de</a>).</p>
    </section>

    <section>
      <h2>Haftungsausschluss</h2>
      <p>Dies ist eine Demonstrations-Anwendung. Die angezeigten Dokumente und Firmendaten sind fiktiv. Für die Richtigkeit der KI-generierten Antworten wird keine Gewähr übernommen.</p>
    </section>
  </div>
</div>

<style>
  .wrapper {
    min-height: 100vh;
    background: #162032;
    color: #cbd5e1;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    padding: 2rem 1rem;
  }
  .content {
    max-width: 680px;
    margin: 0 auto;
  }
  .back {
    display: inline-block;
    color: #64748b;
    text-decoration: none;
    font-size: 0.85rem;
    margin-bottom: 2rem;
  }
  .back:hover { color: #94a3b8; }
  h1 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 0.25rem;
  }
  h1 + p {
    font-size: 0.8rem;
    color: #475569;
    margin-bottom: 1.75rem;
  }
  h2 {
    font-size: 1rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 0.5rem;
  }
  section {
    margin-bottom: 1.5rem;
  }
  p {
    font-size: 0.88rem;
    line-height: 1.7;
    color: #94a3b8;
    margin-bottom: 0.6rem;
  }
  a { color: #fbbf24; text-decoration: none; }
  a:hover { text-decoration: underline; }
  hr {
    border: none;
    border-top: 1px solid #243447;
    margin: 2.5rem 0;
  }
</style>
