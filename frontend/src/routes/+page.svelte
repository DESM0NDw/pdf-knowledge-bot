<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';

  type Doc = {
    id: string;
    name: string;
    use_case: string;
    description: string;
    pdf_url: string;
    flow_steps: string[];
    flow_hint: string;
    processing_text: string;
    suggestions: string[];
  };

  type TrackedQuestion = { text: string; count: number };
  type Message = { role: 'user' | 'bot'; text: string; sources?: number[] };
  type Phase = 'idle' | 'indexing' | 'ready' | 'answering';

  // Die vier Phasen sind technisch immer gleich (Laden → Indexieren → Fragen → Antworten),
  // nur die Beschriftung wechselt je Use Case (kommt aus dem aktiven Dokument).
  const STEP_ICONS = [
    'M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z',
    'M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 0 0 2.25-2.25V6.75a2.25 2.25 0 0 0-2.25-2.25H6.75A2.25 2.25 0 0 0 4.5 6.75v10.5a2.25 2.25 0 0 0 2.25 2.25Zm.75-12h9v9h-9v-9Z',
    'M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.282 48.282 0 0 0 5.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z',
    'M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z',
  ];
  const DEFAULT_STEPS = ['Dokument laden', 'Wissensbasis aufbauen', 'Frage stellen', 'Antwort + Analyse'];
  const DEFAULT_HINT = 'Wähle oben einen Use Case — der Ablauf passt sich an. Das System beantwortet Fragen aus dem Dokument und erkennt mit der Zeit, welche am häufigsten kommen.';

  const USE_CASE_COLOR: Record<string, string> = {
    'Mitarbeiter-Self-Service': 'badge-amber',
    'Kundensupport': 'badge-blue',
    'Onboarding': 'badge-green',
    'Sales-Enablement': 'badge-red',
  };

  let docs = $state<Doc[]>([]);
  let activeDoc = $state<Doc | null>(null);
  let activeDocId = $state('');
  let activeDocName = $state('');
  let pdfSrc = $state('');
  let phase = $state<Phase>('idle');
  let activeStep = $state(-1);
  let messages = $state<Message[]>([]);
  let input = $state('');
  let loading = $state(false);
  let chatEl = $state<HTMLDivElement | null>(null);
  let pdfPage = $state(1);
  let dragOver = $state(false);
  let uploadError = $state('');
  let draggingId = $state<string | null>(null);
  let mobileTab = $state<'pdf' | 'chat'>('chat');
  let trackedQuestions = $state<TrackedQuestion[]>([]);
  let clusterFeedback = $state<{ isNew: boolean; count: number } | null>(null);
  let feedbackTimer: ReturnType<typeof setTimeout>;

  let stepLabels = $derived(activeDoc?.flow_steps ?? DEFAULT_STEPS);
  let flowHint = $derived(activeDoc?.flow_hint ?? DEFAULT_HINT);

  onMount(async () => {
    const res = await fetch('/api/docs');
    docs = await res.json();
  });

  async function fetchTracked(docId: string) {
    const res = await fetch(`/api/questions/${docId}`);
    if (res.ok) trackedQuestions = await res.json();
  }

  function showClusterFeedback(isNew: boolean, count: number) {
    if (count === 0) return;
    clusterFeedback = { isNew, count };
    clearTimeout(feedbackTimer);
    feedbackTimer = setTimeout(() => (clusterFeedback = null), 4000);
  }

  async function selectDoc(doc: Doc) {
    if (phase === 'indexing') return;
    if (activeDocId === doc.id && phase !== 'idle') return;

    messages = [];
    trackedQuestions = [];
    pdfPage = 1;
    pdfSrc = '';
    phase = 'indexing';
    activeDoc = doc;
    activeDocId = doc.id;
    activeDocName = `${doc.name}, ${doc.description}`;

    activeStep = 0;
    await new Promise(r => setTimeout(r, 350));
    activeStep = 1;

    await fetch(`/api/index/${doc.id}`, { method: 'POST' });

    pdfSrc = doc.pdf_url;
    activeStep = 2;
    phase = 'ready';
    fetchTracked(doc.id);
  }

  async function uploadAndIndex(file: File) {
    if (phase === 'indexing') return;
    uploadError = '';

    if (file.size > 20 * 1024 * 1024) {
      uploadError = 'Datei zu groß — max. 20 MB erlaubt.';
      return;
    }

    messages = [];
    trackedQuestions = [];
    pdfPage = 1;
    pdfSrc = '';
    phase = 'indexing';
    activeDoc = null;
    activeDocId = '';
    activeDocName = file.name.replace(/\.pdf$/i, '');

    activeStep = 0;
    await new Promise(r => setTimeout(r, 350));
    activeStep = 1;

    const form = new FormData();
    form.append('file', file);
    const res = await fetch('/api/upload', { method: 'POST', body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      uploadError = err.detail ?? 'Upload fehlgeschlagen.';
      phase = 'idle';
      activeStep = -1;
      return;
    }
    const data = await res.json();

    activeDocId = data.doc_id;
    pdfSrc = URL.createObjectURL(file);
    activeStep = 2;
    phase = 'ready';
  }

  function scrollChat() {
    setTimeout(() => chatEl?.scrollTo({ top: chatEl.scrollHeight, behavior: 'smooth' }), 50);
  }

  async function ask(question: string) {
    if (!question.trim() || loading || phase !== 'ready') return;
    messages = [...messages, { role: 'user', text: question }];
    input = '';
    loading = true;
    activeStep = 3;
    scrollChat();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, doc_id: activeDocId, doc_name: activeDocName }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      messages = [...messages, { role: 'bot', text: data.answer, sources: data.sources }];
      showClusterFeedback(data.is_new_question, data.question_count);
      fetchTracked(activeDocId);
    } catch {
      messages = [...messages, { role: 'bot', text: 'Fehler beim Abrufen der Antwort.' }];
    } finally {
      loading = false;
      activeStep = 2;
      scrollChat();
    }
  }

  function jumpToPage(page: number) {
    pdfPage = page;
    mobileTab = 'pdf';
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(input); }
  }

  function onDragStart(e: DragEvent, id: string) {
    draggingId = id;
    e.dataTransfer?.setData('text/plain', id);
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    dragOver = false;
    const file = e.dataTransfer?.files[0];
    if (file?.type === 'application/pdf') {
      uploadAndIndex(file);
      return;
    }
    const id = e.dataTransfer?.getData('text/plain') ?? draggingId;
    const doc = docs.find(d => d.id === id);
    if (doc) selectDoc(doc);
    draggingId = null;
  }

  function onFileInput(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) uploadAndIndex(file);
  }
</script>

<div class="wrapper">

  <!-- Header -->
  <header>
    <div class="header-inner">
      <div class="header-left">
        <div class="icon">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
        </div>
        <div>
          <h1>Wissens-Assistent</h1>
          <p class="subtitle">Antworten mit Quellenangabe — und erkennt, welche Fragen am häufigsten gestellt werden</p>
        </div>
      </div>
      <div class="header-right">
        <span class="demo-badge"><span class="pulse"></span>DEMO</span>
        <a href="https://desmond.autonomika.de" class="back-link" target="_blank">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          Portfolio
        </a>
      </div>
    </div>
  </header>

  <!-- Flow bar -->
  <div class="flow-bar">
    <p class="flow-label">So läuft die Automation:</p>
    <div class="flow-steps">
      {#each STEP_ICONS as path, i}
        <div class="flow-step {activeStep === i ? 'active' : ''} {activeStep > i ? 'done' : ''}">
          <svg class="step-icon" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d={path} />
          </svg>
          <span class="step-label">{stepLabels[i]}</span>
        </div>
        {#if i < STEP_ICONS.length - 1}
          <div class="flow-arrow {activeStep > i ? 'done' : ''}">→</div>
        {/if}
      {/each}
    </div>
    <p class="flow-hint">{flowHint}</p>
  </div>

  <!-- Doc selector -->
  <div class="doc-bar">
    <span class="doc-bar-label">Use Case wählen:</span>
    <div class="doc-cards">
      {#each docs as doc}
        <div
          class="doc-card {activeDocId === doc.id && phase !== 'idle' ? 'active' : ''} {phase === 'indexing' && activeDocId === doc.id ? 'loading' : ''}"
          role="button"
          tabindex="0"
          draggable="true"
          onclick={() => selectDoc(doc)}
          onkeydown={(e) => e.key === 'Enter' && selectDoc(doc)}
          ondragstart={(e) => onDragStart(e, doc.id)}
          ondragend={() => draggingId = null}
          title="Klicken oder in den Viewer ziehen"
        >
          <svg class="doc-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          <div class="doc-card-info">
            <span class="doc-name">{doc.name}</span>
            <span class="doc-desc">{doc.description}</span>
          </div>
          <span class="industry-badge {USE_CASE_COLOR[doc.use_case] ?? 'badge-amber'}">{doc.use_case}</span>
        </div>
      {/each}
    </div>
    <span class="doc-bar-hint">Klicken oder in den Viewer ziehen</span>
  </div>

  <!-- Mobile tabs -->
  <div class="mobile-tabs">
    <button class="tab {mobileTab === 'pdf' ? 'active' : ''}" onclick={() => mobileTab = 'pdf'}>
      Dokument ansehen
    </button>
    <button class="tab {mobileTab === 'chat' ? 'active' : ''}" onclick={() => mobileTab = 'chat'}>
      Chat
    </button>
  </div>

  <!-- Main split -->
  <div class="split">

    <!-- PDF / Drop panel -->
    <div
      class="pdf-panel {mobileTab === 'chat' ? 'mobile-hidden' : ''} {dragOver ? 'drag-over' : ''}"
      ondragover={(e) => { e.preventDefault(); dragOver = true; }}
      ondragleave={() => dragOver = false}
      ondrop={onDrop}
      role="region"
      aria-label="PDF Viewer"
    >
      {#if phase === 'idle'}
        <div class="idle-state {dragOver ? 'drag-active' : ''}">
          <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1" class="idle-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m0-15.75h-3.75" />
          </svg>
          <p class="idle-title">PDF hier ablegen</p>
          <p class="idle-sub">oder Demo-Dokument oben auswählen</p>
          <label class="upload-btn">
            <input type="file" accept=".pdf" onchange={onFileInput} hidden />
            Eigene PDF auswählen · max. 20 MB
          </label>
          <div class="idle-warn">
            <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="flex-shrink:0;margin-top:1px">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
            </svg>
            <span>Keine persönlichen oder vertraulichen Dokumente hochladen.</span>
          </div>
          {#if uploadError}
            <p class="upload-error">{uploadError}</p>
          {/if}
        </div>

      {:else if phase === 'indexing'}
        <div class="indexing-state">
          <div class="spinner"></div>
          <p class="indexing-title">Wird eingelesen...</p>
          <p class="indexing-sub">{activeDoc?.processing_text ?? 'Seiten werden in Vektoren umgewandelt'}</p>
        </div>

      {:else if dragOver}
        <div class="drop-overlay">
          <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m0-15.75h-3.75" />
          </svg>
          <span>Hier ablegen</span>
        </div>

      {:else}
        <div class="pdf-header">
          <span class="pdf-title">{activeDocName}</span>
          <a href={pdfSrc} target="_blank" class="pdf-open-btn" title="In neuem Tab oeffnen">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
            Vollbild
          </a>
        </div>
        {#key `${activeDocId}-${pdfPage}`}
          <embed
            src="{pdfSrc}#page={pdfPage}"
            type="application/pdf"
            class="pdf-iframe"
            title="{activeDocName}"
          />
        {/key}
      {/if}
    </div>

    <!-- Chat -->
    <div class="chat-panel {mobileTab === 'pdf' ? 'mobile-hidden' : ''}">

      {#if phase === 'idle'}
        <div class="chat-idle">
          <p>Wähle ein Dokument aus um Fragen zu stellen.</p>
        </div>
      {:else if phase === 'indexing'}
        <div class="chat-idle">
          <p>Dokument wird eingelesen — einen Moment...</p>
        </div>
      {:else}
        <!-- FAQ / Suggestions -->
        {#if messages.length === 0}
          <div class="suggestions">
            {#if trackedQuestions.length > 0}
              {@const maxCount = Math.max(...trackedQuestions.map(q => q.count))}
              <p class="suggestions-label">
                <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" style="flex-shrink:0">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
                </svg>
                Was andere am häufigsten fragen
              </p>
              <div class="faq-list">
                {#each trackedQuestions as q (q.text)}
                  <button class="faq-item" onclick={() => ask(q.text)}>
                    <span class="faq-bar" style="width: {Math.max((q.count / maxCount) * 100, 8)}%"></span>
                    <span class="faq-text">{q.text}</span>
                    <span class="faq-count">{q.count}×</span>
                  </button>
                {/each}
              </div>
              <p class="faq-hint">
                Fragen werden semantisch gruppiert — unterschiedlich formulierte, aber inhaltsgleiche Fragen zählen zum selben Eintrag.
              </p>
            {:else if activeDoc}
              <p class="suggestions-label">Beispielfragen zu diesem Dokument:</p>
              <div class="chips">
                {#each activeDoc.suggestions as s}
                  <button class="chip" onclick={() => ask(s)}>{s}</button>
                {/each}
              </div>
            {/if}
          </div>
        {/if}

        <!-- Messages -->
        <div class="chat" bind:this={chatEl}>
          {#each messages as msg}
            {#if msg.role === 'user'}
              <div class="msg user">
                <div class="bubble user-bubble">{msg.text}</div>
              </div>
            {:else}
              <div class="msg bot">
                <div class="bot-avatar">
                  <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                  </svg>
                </div>
                <div>
                  <div class="bubble bot-bubble">{msg.text}</div>
                  {#if msg.sources && msg.sources.length > 0}
                    <div class="sources">
                      <span class="sources-label">Quellen:</span>
                      {#each msg.sources as page}
                        <button class="source-badge" onclick={() => jumpToPage(page)} title="Im Viewer anzeigen">
                          Seite {page}
                        </button>
                      {/each}
                    </div>
                  {/if}
                </div>
              </div>
            {/if}
          {/each}

          {#if loading}
            <div class="msg bot">
              <div class="bot-avatar">
                <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                </svg>
              </div>
              <div class="bubble bot-bubble typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          {/if}
        </div>
      {/if}

      <!-- Input -->
      <div class="input-bar">
        {#if clusterFeedback}
          <div class="cluster-toast {clusterFeedback.isNew ? 'is-new' : 'is-existing'}">
            {#if clusterFeedback.isNew}
              <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
              </svg>
              <span><strong>Neue Frage erkannt</strong> — zur Wissensbasis hinzugefügt</span>
            {:else}
              <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 7.5 7.5 3m0 0L12 7.5M7.5 3v13.5m13.5 0L16.5 21m0 0L12 16.5m4.5 4.5V7.5" />
              </svg>
              <span><strong>Ähnliche Frage erkannt</strong> — dieser Cluster wurde jetzt {clusterFeedback.count}× gefragt</span>
            {/if}
          </div>
        {/if}
        <div class="input-row">
          <input
            type="text"
            placeholder="Stelle eine Frage zum Dokument..."
            bind:value={input}
            onkeydown={onKeydown}
            disabled={loading || phase !== 'ready'}
            aria-label="Frage eingeben"
          />
          <button
            class="send-btn"
            onclick={() => ask(input)}
            disabled={loading || !input.trim() || phase !== 'ready'}
            aria-label="Frage senden"
          >
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
            </svg>
          </button>
        </div>
        <div class="warn-box">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="flex-shrink:0;margin-top:1px">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
          </svg>
          <span>Fragen werden zur Verarbeitung an <strong>Groq (USA)</strong> übermittelt und können dort gespeichert werden. Bitte <strong>keine persönlichen oder vertraulichen Daten</strong> eingeben.</span>
        </div>
      </div>

    </div>
  </div>

  <footer>
    Demo von <a href="https://desmond.autonomika.de" target="_blank">Desmond Wong</a>
    &middot; Stack: Qdrant &middot; nomic-embed-text &middot; Groq &middot; SvelteKit
    &middot; <a href="/impressum">Impressum & Datenschutz</a>
  </footer>

</div>

<style>
  .wrapper { min-height: 100vh; display: flex; flex-direction: column; background: #0c0c0c; }

  /* Header */
  header {
    position: sticky; top: 0; z-index: 20;
    background: rgba(12,12,12,0.95); backdrop-filter: blur(8px);
    border-bottom: 1px solid #1e1e1e;
  }
  .header-inner {
    max-width: 1400px; margin: 0 auto; padding: 0 1.25rem;
    height: 52px; display: flex; align-items: center; justify-content: space-between;
  }
  .header-left { display: flex; align-items: center; gap: 0.75rem; }
  .icon {
    width: 34px; height: 34px; border-radius: 9px; flex-shrink: 0;
    background: rgba(34,211,238,0.1); color: #22d3ee;
    display: flex; align-items: center; justify-content: center;
  }
  h1 { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; }
  .subtitle { font-size: 0.76rem; color: #94a3b8; }
  .header-right { display: flex; align-items: center; gap: 0.75rem; }
  .demo-badge {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.05em;
    color: #22d3ee; background: rgba(34,211,238,0.1);
    border: 1px solid rgba(34,211,238,0.2); padding: 2px 8px; border-radius: 999px;
  }
  .pulse { width: 5px; height: 5px; border-radius: 50%; background: #22d3ee; animation: pulse 1.5s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .back-link {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.78rem; color: #94a3b8; text-decoration: none; transition: color 0.15s;
  }
  .back-link:hover { color: #94a3b8; }

  /* Flow bar */
  .flow-bar {
    background: #111; border-bottom: 1px solid #1e1e1e;
    padding: 0.75rem 1.25rem; display: flex; flex-direction: column; align-items: center;
  }
  .flow-label { font-size: 0.75rem; color: #b0bfcc; margin-bottom: 0.5rem; }
  .flow-steps { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; justify-content: center; }
  .flow-step {
    display: flex; align-items: center; gap: 0.4rem;
    background: #0c0c0c; border: 1px solid #1e1e1e;
    border-radius: 8px; padding: 0.35rem 0.65rem;
    font-size: 0.82rem; color: #b0bfcc; transition: all 0.3s;
  }
  .flow-step.active { border-color: #22d3ee; color: #22d3ee; background: rgba(34,211,238,0.06); }
  .flow-step.done { border-color: #22c55e; color: #22c55e; background: rgba(34,197,94,0.06); }
  .step-icon { flex-shrink: 0; }
  .flow-arrow { font-size: 0.75rem; color: #475569; transition: color 0.3s; }
  .flow-arrow.done { color: #22c55e; }
  .flow-hint { font-size: 0.73rem; color: #94a3b8; margin-top: 0.5rem; text-align: center; }

  /* Doc bar */
  .doc-bar {
    background: #0c0c0c; border-bottom: 1px solid #1e1e1e;
    padding: 0.6rem 1.25rem; display: flex; align-items: center; gap: 0.75rem;
    overflow-x: auto;
  }
  .doc-bar-label { font-size: 0.76rem; color: #94a3b8; white-space: nowrap; flex-shrink: 0; }
  .doc-bar-hint { font-size: 0.72rem; color: #475569; white-space: nowrap; flex-shrink: 0; }
  .doc-cards { display: flex; gap: 0.5rem; }
  .doc-card {
    display: flex; align-items: center; gap: 0.5rem;
    background: #111; border: 1px solid #252525;
    border-radius: 10px; padding: 0.45rem 0.75rem;
    cursor: grab; transition: all 0.15s; white-space: nowrap; user-select: none;
  }
  .doc-card:hover { border-color: #333; background: #1a1a1a; }
  .doc-card.active { border-color: #22d3ee; background: rgba(34,211,238,0.06); }
  .doc-card.loading { opacity: 0.6; cursor: wait; }
  .doc-card:active { cursor: grabbing; }
  .doc-icon { width: 16px; height: 16px; color: #64748b; flex-shrink: 0; }
  .doc-card.active .doc-icon { color: #22d3ee; }
  .doc-card-info { display: flex; flex-direction: column; }
  .doc-name { font-size: 0.85rem; font-weight: 600; color: #e2eaf2; line-height: 1.2; }
  .doc-desc { font-size: 0.72rem; color: #94a3b8; }
  .industry-badge { font-size: 0.62rem; font-weight: 600; padding: 1px 6px; border-radius: 4px; }
  .badge-amber { color: #22d3ee; background: rgba(34,211,238,0.1); border: 1px solid rgba(34,211,238,0.2); }
  .badge-red { color: #f87171; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.2); }
  .badge-blue { color: #60a5fa; background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.2); }
  .badge-green { color: #4ade80; background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.2); }

  /* Mobile tabs */
  .mobile-tabs { display: none; border-bottom: 1px solid #1e1e1e; }
  .tab {
    flex: 1; padding: 0.6rem; font-size: 0.8rem; font-weight: 500;
    background: transparent; border: none; color: #475569; cursor: pointer;
    border-bottom: 2px solid transparent; transition: all 0.15s;
  }
  .tab.active { color: #22d3ee; border-bottom-color: #22d3ee; }

  /* Split */
  .split { flex: 1; display: grid; grid-template-columns: 1fr 1fr; min-height: 0; overflow: hidden; }

  /* PDF panel */
  .pdf-panel {
    display: flex; flex-direction: column;
    border-right: 1px solid #1e1e1e; position: relative;
    transition: border-color 0.15s;
  }
  .pdf-panel.drag-over { border-color: #22d3ee; }

  /* Idle state */
  .idle-state {
    flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 0.75rem; padding: 2rem;
    border: 2px dashed #252525; margin: 1rem; border-radius: 12px;
    transition: all 0.2s;
  }
  .idle-state.drag-active { border-color: #22d3ee; background: rgba(34,211,238,0.06); }
  .idle-icon { color: #333; }
  .idle-title { font-size: 1rem; font-weight: 600; color: #94a3b8; }
  .idle-sub { font-size: 0.8rem; color: #475569; text-align: center; }
  .upload-btn {
    margin-top: 0.25rem; padding: 0.45rem 1.1rem;
    font-size: 0.8rem; font-weight: 500; color: #94a3b8;
    background: #111; border: 1px solid #252525;
    border-radius: 8px; cursor: pointer; transition: all 0.15s;
  }
  .upload-btn:hover { border-color: #22d3ee; color: #22d3ee; }
  .upload-error { font-size: 0.75rem; color: #f87171; margin-top: 0.25rem; }
  .idle-warn {
    display: flex; align-items: flex-start; gap: 0.4rem;
    background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.2);
    border-radius: 7px; padding: 0.4rem 0.6rem;
    font-size: 0.72rem; color: #b8900a; line-height: 1.4;
  }

  /* Indexing state */
  .indexing-state {
    flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem;
  }
  .spinner {
    width: 36px; height: 36px; border-radius: 50%;
    border: 3px solid #1e1e1e; border-top-color: #22d3ee;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .indexing-title { font-size: 0.95rem; font-weight: 600; color: #94a3b8; }
  .indexing-sub { font-size: 0.78rem; color: #475569; }

  .drop-overlay {
    position: absolute; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 0.75rem;
    background: rgba(34,211,238,0.06); border: 2px dashed #22d3ee;
    color: #22d3ee; font-size: 0.9rem; font-weight: 600; z-index: 10;
    pointer-events: none;
  }
  .pdf-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.5rem 0.75rem; border-bottom: 1px solid #1e1e1e;
    background: #0c0c0c; flex-shrink: 0;
  }
  .pdf-title { font-size: 0.78rem; color: #94a3b8; }
  .pdf-open-btn {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.76rem; color: #94a3b8; text-decoration: none; transition: color 0.15s;
  }
  .pdf-open-btn:hover { color: #94a3b8; }
  .pdf-iframe { flex: 1; width: 100%; border: none; background: #111; }

  /* Chat panel */
  .chat-panel { display: flex; flex-direction: column; overflow: hidden; position: relative; }
  .chat-idle {
    flex: 1; display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; color: #475569; padding: 2rem; text-align: center;
  }
  .suggestions { padding: 1rem; display: flex; flex-direction: column; gap: 0.6rem; }
  .suggestions-label { font-size: 0.76rem; color: #94a3b8; display: flex; align-items: center; gap: 0.4rem; }
  .chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .chip {
    font-size: 0.75rem; color: #94a3b8; background: #111;
    border: 1px solid #252525; padding: 0.3rem 0.7rem; border-radius: 999px;
    cursor: pointer; transition: all 0.15s; text-align: left;
  }
  .chip:hover { background: #1a1a1a; color: #f1f5f9; border-color: #22d3ee; }

  /* FAQ list with frequency bars */
  .faq-list { display: flex; flex-direction: column; gap: 0.35rem; }
  .faq-item {
    position: relative; display: flex; align-items: center; gap: 0.5rem;
    width: 100%; text-align: left; overflow: hidden;
    background: #111; border: 1px solid #252525; border-radius: 8px;
    padding: 0.5rem 0.7rem; cursor: pointer; transition: border-color 0.15s;
  }
  .faq-item:hover { border-color: #22d3ee; }
  .faq-bar {
    position: absolute; left: 0; top: 0; bottom: 0;
    background: rgba(34,211,238,0.1); border-right: 1px solid rgba(34,211,238,0.25);
    transition: width 0.5s cubic-bezier(0.22,1,0.36,1); z-index: 0;
  }
  .faq-text { position: relative; z-index: 1; flex: 1; font-size: 0.8rem; color: #e2eaf2; line-height: 1.35; }
  .faq-count {
    position: relative; z-index: 1; flex-shrink: 0;
    font-size: 0.7rem; font-weight: 700; color: #22d3ee;
    background: rgba(34,211,238,0.15); padding: 1px 6px; border-radius: 4px;
  }
  .faq-hint { font-size: 0.7rem; color: #475569; line-height: 1.4; margin-top: 0.15rem; }

  /* Cluster feedback toast */
  .cluster-toast {
    position: absolute; left: 0.75rem; right: 0.75rem; bottom: 100%; margin-bottom: 0.4rem;
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.55rem 0.75rem; border-radius: 9px;
    font-size: 0.76rem; line-height: 1.4; z-index: 5;
    animation: toast-in 0.3s cubic-bezier(0.22,1,0.36,1);
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
  }
  .cluster-toast svg { flex-shrink: 0; }
  .cluster-toast strong { font-weight: 700; }
  .cluster-toast.is-new {
    background: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.35); color: #4ade80;
  }
  .cluster-toast.is-existing {
    background: rgba(34,211,238,0.12); border: 1px solid rgba(34,211,238,0.35); color: #22d3ee;
  }
  @keyframes toast-in { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

  .chat { flex: 1; overflow-y: auto; padding: 0.75rem 1rem; display: flex; flex-direction: column; gap: 0.85rem; }
  .msg { display: flex; gap: 0.5rem; }
  .msg.user { justify-content: flex-end; }
  .msg.bot { align-items: flex-start; }
  .bubble { max-width: 85%; padding: 0.6rem 0.85rem; border-radius: 14px; font-size: 0.83rem; line-height: 1.6; white-space: pre-wrap; }
  .user-bubble { background: #22d3ee; color: #000; border-bottom-right-radius: 3px; font-weight: 500; }
  .bot-bubble { background: #111; color: #e2e8f0; border-bottom-left-radius: 3px; border: 1px solid #252525; }
  .bot-avatar {
    width: 26px; height: 26px; flex-shrink: 0; margin-top: 2px;
    background: rgba(34,211,238,0.1); border-radius: 7px;
    display: flex; align-items: center; justify-content: center; color: #22d3ee;
  }
  .sources { display: flex; align-items: center; gap: 0.35rem; margin-top: 0.35rem; flex-wrap: wrap; }
  .sources-label { font-size: 0.74rem; color: #94a3b8; }
  .source-badge {
    font-size: 0.65rem; font-weight: 600; color: #22d3ee;
    background: rgba(34,211,238,0.1); border: 1px solid rgba(34,211,238,0.25);
    padding: 1px 6px; border-radius: 4px; cursor: pointer; transition: all 0.15s;
  }
  .source-badge:hover { background: rgba(34,211,238,0.2); }
  .typing { display: flex; align-items: center; gap: 4px; padding: 0.7rem 0.9rem; }
  .typing span { width: 5px; height: 5px; border-radius: 50%; background: #475569; animation: bounce 1.2s ease-in-out infinite; }
  .typing span:nth-child(2) { animation-delay: 0.2s; }
  .typing span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-5px)} }

  .input-bar { padding: 0.65rem 0.75rem; border-top: 1px solid #1e1e1e; background: rgba(12,12,12,0.95); flex-shrink: 0; position: relative; }
  .input-row { display: flex; gap: 0.4rem; }
  .warn-box {
    display: flex; align-items: flex-start; gap: 0.5rem;
    background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.2);
    border-radius: 8px; padding: 0.6rem 0.75rem; margin-top: 0.35rem;
    font-size: 0.75rem; color: #b8900a; line-height: 1.5;
  }
  .warn-box strong { color: #d4a820; }
  input {
    flex: 1; background: #111; border: 1px solid #252525; color: #e2e8f0;
    border-radius: 10px; padding: 0.55rem 0.85rem; font-size: 0.83rem; outline: none; transition: border-color 0.15s;
  }
  input:focus { border-color: #22d3ee; }
  input::placeholder { color: #475569; }
  input:disabled { opacity: 0.5; }
  .send-btn {
    width: 38px; height: 38px; background: #22d3ee; color: #000; border: none;
    border-radius: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.15s; flex-shrink: 0;
  }
  .send-btn:hover:not(:disabled) { background: #06b6d4; }
  .send-btn:disabled { opacity: 0.4; cursor: default; }

  footer { text-align: center; font-size: 0.68rem; color: #475569; padding: 0.6rem; border-top: 1px solid #1e1e1e; }
  footer a { color: #475569; text-decoration: none; }
  footer a:hover { color: #94a3b8; }

  @media (max-width: 768px) {
    .split { grid-template-columns: 1fr; }
    .mobile-tabs { display: flex; }
    .mobile-hidden { display: none; }
    .subtitle { display: none; }
    .pdf-iframe { min-height: 60vh; }
  }
</style>
