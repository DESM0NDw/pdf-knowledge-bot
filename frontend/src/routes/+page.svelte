<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';

  type Doc = {
    id: string;
    name: string;
    industry: string;
    description: string;
    pdf_url: string;
    suggestions: string[];
  };

  type Message = { role: 'user' | 'bot'; text: string; sources?: number[] };

  let docs = $state<Doc[]>([]);
  let activeDoc = $state<Doc | null>(null);
  let messages = $state<Message[]>([]);
  let input = $state('');
  let loading = $state(false);
  let chatEl = $state<HTMLDivElement | null>(null);
  let pdfPage = $state(1);
  let draggingId = $state<string | null>(null);
  let dragOver = $state(false);
  let mobileTab = $state<'pdf' | 'chat'>('chat');

  onMount(async () => {
    const res = await fetch('/api/docs');
    docs = await res.json();
    if (docs.length > 0) selectDoc(docs[0]);
  });

  function selectDoc(doc: Doc) {
    if (activeDoc?.id === doc.id) return;
    activeDoc = doc;
    messages = [];
    pdfPage = 1;
  }

  function scrollChat() {
    setTimeout(() => chatEl?.scrollTo({ top: chatEl.scrollHeight, behavior: 'smooth' }), 50);
  }

  async function ask(question: string) {
    if (!question.trim() || loading || !activeDoc) return;
    messages = [...messages, { role: 'user', text: question }];
    input = '';
    loading = true;
    scrollChat();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, doc_id: activeDoc.id }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      messages = [...messages, { role: 'bot', text: data.answer, sources: data.sources }];
    } catch {
      messages = [...messages, { role: 'bot', text: 'Fehler beim Abrufen der Antwort.' }];
    } finally {
      loading = false;
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
    const id = e.dataTransfer?.getData('text/plain') ?? draggingId;
    const doc = docs.find(d => d.id === id);
    if (doc) selectDoc(doc);
    draggingId = null;
  }

  const INDUSTRY_COLOR: Record<string, string> = {
    Technologie: 'badge-amber',
    Gastronomie: 'badge-red',
    Immobilien: 'badge-blue',
  };
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
          <h1>PDF Wissens-Bot</h1>
          <p class="subtitle">Dokument waehlen &rarr; Frage stellen &rarr; Antwort mit Seitenangabe</p>
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

  <!-- Doc selector -->
  <div class="doc-bar">
    <span class="doc-bar-label">Demo-Dokumente:</span>
    <div class="doc-cards">
      {#each docs as doc}
        <div
          class="doc-card {activeDoc?.id === doc.id ? 'active' : ''}"
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
          <span class="industry-badge {INDUSTRY_COLOR[doc.industry] ?? 'badge-amber'}">{doc.industry}</span>
        </div>
      {/each}
    </div>
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

    <!-- PDF Viewer -->
    <div
      class="pdf-panel {mobileTab === 'chat' ? 'mobile-hidden' : ''} {dragOver ? 'drag-over' : ''}"
      ondragover={(e) => { e.preventDefault(); dragOver = true; }}
      ondragleave={() => dragOver = false}
      ondrop={onDrop}
      role="region"
      aria-label="PDF Viewer"
    >
      {#if dragOver}
        <div class="drop-overlay">
          <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m0-15.75h-3.75" />
          </svg>
          <span>Hier ablegen</span>
        </div>
      {:else if activeDoc}
        <div class="pdf-header">
          <span class="pdf-title">{activeDoc.name} — {activeDoc.description}</span>
          <a href={activeDoc.pdf_url} target="_blank" class="pdf-open-btn" title="In neuem Tab oeffnen">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
            Vollbild
          </a>
        </div>
        <embed
          src="{activeDoc.pdf_url}#page={pdfPage}"
          type="application/pdf"
          class="pdf-iframe"
          title="{activeDoc.name}"
        />
      {/if}
    </div>

    <!-- Chat -->
    <div class="chat-panel {mobileTab === 'pdf' ? 'mobile-hidden' : ''}">

      <!-- Suggestions -->
      {#if messages.length === 0 && activeDoc}
        <div class="suggestions">
          <p class="suggestions-label">Haeufige Fragen zu diesem Dokument:</p>
          <div class="chips">
            {#each activeDoc.suggestions as s}
              <button class="chip" onclick={() => ask(s)}>{s}</button>
            {/each}
          </div>
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

      <!-- Input -->
      <div class="input-bar">
        <div class="input-row">
          <input
            type="text"
            placeholder="Stelle eine Frage zum Dokument..."
            bind:value={input}
            onkeydown={onKeydown}
            disabled={loading || !activeDoc}
            aria-label="Frage eingeben"
          />
          <button
            class="send-btn"
            onclick={() => ask(input)}
            disabled={loading || !input.trim() || !activeDoc}
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
    &mdash; Stack: Qdrant &middot; nomic-embed-text &middot; Groq &middot; SvelteKit
    &middot; <a href="/impressum">Impressum & Datenschutz</a>
  </footer>

</div>

<style>
  .wrapper { min-height: 100vh; display: flex; flex-direction: column; background: #162032; }

  /* Header */
  header {
    position: sticky; top: 0; z-index: 20;
    background: rgba(22,32,50,0.97); backdrop-filter: blur(8px);
    border-bottom: 1px solid #243447;
  }
  .header-inner {
    max-width: 1400px; margin: 0 auto; padding: 0 1.25rem;
    height: 52px; display: flex; align-items: center; justify-content: space-between;
  }
  .header-left { display: flex; align-items: center; gap: 0.75rem; }
  .icon {
    width: 34px; height: 34px; border-radius: 9px; flex-shrink: 0;
    background: rgba(251,191,36,0.12); color: #fbbf24;
    display: flex; align-items: center; justify-content: center;
  }
  h1 { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; }
  .subtitle { font-size: 0.7rem; color: #475569; }
  .header-right { display: flex; align-items: center; gap: 0.75rem; }
  .demo-badge {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.05em;
    color: #fbbf24; background: rgba(251,191,36,0.1);
    border: 1px solid rgba(251,191,36,0.2); padding: 2px 8px; border-radius: 999px;
  }
  .pulse { width: 5px; height: 5px; border-radius: 50%; background: #fbbf24; animation: pulse 1.5s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .back-link {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.72rem; color: #475569; text-decoration: none; transition: color 0.15s;
  }
  .back-link:hover { color: #94a3b8; }

  /* Doc bar */
  .doc-bar {
    background: #162032; border-bottom: 1px solid #243447;
    padding: 0.6rem 1.25rem; display: flex; align-items: center; gap: 0.75rem;
    overflow-x: auto;
  }
  .doc-bar-label { font-size: 0.7rem; color: #475569; white-space: nowrap; flex-shrink: 0; }
  .doc-cards { display: flex; gap: 0.5rem; }
  .doc-card {
    display: flex; align-items: center; gap: 0.5rem;
    background: #1e2d42; border: 1px solid #2a3d55;
    border-radius: 10px; padding: 0.45rem 0.75rem;
    cursor: grab; transition: all 0.15s; white-space: nowrap; user-select: none;
  }
  .doc-card:hover { border-color: #3d5470; background: #263548; }
  .doc-card.active { border-color: #fbbf24; background: rgba(251,191,36,0.06); }
  .doc-card:active { cursor: grabbing; }
  .doc-icon { width: 16px; height: 16px; color: #64748b; flex-shrink: 0; }
  .doc-card.active .doc-icon { color: #fbbf24; }
  .doc-card-info { display: flex; flex-direction: column; }
  .doc-name { font-size: 0.78rem; font-weight: 600; color: #cbd5e1; line-height: 1.2; }
  .doc-desc { font-size: 0.65rem; color: #475569; }
  .industry-badge { font-size: 0.62rem; font-weight: 600; padding: 1px 6px; border-radius: 4px; }
  .badge-amber { color: #fbbf24; background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.2); }
  .badge-red { color: #f87171; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.2); }
  .badge-blue { color: #60a5fa; background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.2); }

  /* Mobile tabs */
  .mobile-tabs { display: none; border-bottom: 1px solid #243447; }
  .tab {
    flex: 1; padding: 0.6rem; font-size: 0.8rem; font-weight: 500;
    background: transparent; border: none; color: #475569; cursor: pointer;
    border-bottom: 2px solid transparent; transition: all 0.15s;
  }
  .tab.active { color: #fbbf24; border-bottom-color: #fbbf24; }

  /* Split */
  .split {
    flex: 1; display: grid; grid-template-columns: 1fr 1fr;
    min-height: 0; overflow: hidden;
  }

  /* PDF panel */
  .pdf-panel {
    display: flex; flex-direction: column;
    border-right: 1px solid #243447; position: relative;
    transition: border-color 0.15s;
  }
  .pdf-panel.drag-over { border-color: #fbbf24; background: rgba(251,191,36,0.03); }
  .drop-overlay {
    position: absolute; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 0.75rem;
    background: rgba(251,191,36,0.06); border: 2px dashed #fbbf24;
    color: #fbbf24; font-size: 0.9rem; font-weight: 600; z-index: 10;
    pointer-events: none;
  }
  .pdf-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.5rem 0.75rem; border-bottom: 1px solid #243447;
    background: #162032; flex-shrink: 0;
  }
  .pdf-title { font-size: 0.72rem; color: #64748b; }
  .pdf-open-btn {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.7rem; color: #475569; text-decoration: none; transition: color 0.15s;
  }
  .pdf-open-btn:hover { color: #94a3b8; }
  .pdf-iframe { flex: 1; width: 100%; border: none; background: #1e2d42; }

  /* Chat panel */
  .chat-panel {
    display: flex; flex-direction: column; overflow: hidden;
  }
  .suggestions { padding: 1rem; display: flex; flex-direction: column; gap: 0.6rem; }
  .suggestions-label { font-size: 0.7rem; color: #475569; }
  .chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .chip {
    font-size: 0.75rem; color: #94a3b8; background: #1e2d42;
    border: 1px solid #2a3d55; padding: 0.3rem 0.7rem; border-radius: 999px;
    cursor: pointer; transition: all 0.15s; text-align: left;
  }
  .chip:hover { background: #263548; color: #f1f5f9; border-color: #fbbf24; }

  .chat { flex: 1; overflow-y: auto; padding: 0.75rem 1rem; display: flex; flex-direction: column; gap: 0.85rem; }
  .msg { display: flex; gap: 0.5rem; }
  .msg.user { justify-content: flex-end; }
  .msg.bot { align-items: flex-start; }
  .bubble { max-width: 85%; padding: 0.6rem 0.85rem; border-radius: 14px; font-size: 0.83rem; line-height: 1.6; white-space: pre-wrap; }
  .user-bubble { background: #fbbf24; color: #1c1917; border-bottom-right-radius: 3px; font-weight: 500; }
  .bot-bubble { background: #1e2d42; color: #e2e8f0; border-bottom-left-radius: 3px; border: 1px solid #2a3d55; }
  .bot-avatar {
    width: 26px; height: 26px; flex-shrink: 0; margin-top: 2px;
    background: rgba(251,191,36,0.1); border-radius: 7px;
    display: flex; align-items: center; justify-content: center; color: #fbbf24;
  }
  .sources { display: flex; align-items: center; gap: 0.35rem; margin-top: 0.35rem; flex-wrap: wrap; }
  .sources-label { font-size: 0.67rem; color: #475569; }
  .source-badge {
    font-size: 0.65rem; font-weight: 600; color: #fbbf24;
    background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.25);
    padding: 1px 6px; border-radius: 4px; cursor: pointer; transition: all 0.15s;
  }
  .source-badge:hover { background: rgba(251,191,36,0.2); }
  .typing { display: flex; align-items: center; gap: 4px; padding: 0.7rem 0.9rem; }
  .typing span { width: 5px; height: 5px; border-radius: 50%; background: #475569; animation: bounce 1.2s ease-in-out infinite; }
  .typing span:nth-child(2) { animation-delay: 0.2s; }
  .typing span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-5px)} }

  .input-bar { padding: 0.65rem 0.75rem; border-top: 1px solid #243447; background: rgba(22,32,50,0.95); flex-shrink: 0; }
  .input-row { display: flex; gap: 0.4rem; }
  .warn-box {
    display: flex; align-items: flex-start; gap: 0.5rem;
    background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.2);
    border-radius: 8px; padding: 0.6rem 0.75rem; margin-top: 0.35rem;
    font-size: 0.75rem; color: #b8900a; line-height: 1.5;
  }
  .warn-box strong { color: #d4a820; }
  input {
    flex: 1; background: #1e2d42; border: 1px solid #2a3d55; color: #e2e8f0;
    border-radius: 10px; padding: 0.55rem 0.85rem; font-size: 0.83rem; outline: none; transition: border-color 0.15s;
  }
  input:focus { border-color: #fbbf24; }
  input::placeholder { color: #475569; }
  input:disabled { opacity: 0.5; }
  .send-btn {
    width: 38px; height: 38px; background: #fbbf24; color: #1c1917; border: none;
    border-radius: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.15s; flex-shrink: 0;
  }
  .send-btn:hover:not(:disabled) { background: #f59e0b; }
  .send-btn:disabled { opacity: 0.4; cursor: default; }

  footer { text-align: center; font-size: 0.68rem; color: #475569; padding: 0.6rem; border-top: 1px solid #243447; }
  footer a { color: #475569; text-decoration: none; }
  footer a:hover { color: #94a3b8; }

  /* Mobile */
  @media (max-width: 768px) {
    .split { grid-template-columns: 1fr; }
    .mobile-tabs { display: flex; }
    .mobile-hidden { display: none; }
    .subtitle { display: none; }
    .pdf-iframe { min-height: 60vh; }
  }
</style>
