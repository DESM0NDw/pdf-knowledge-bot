<script lang="ts">
  import '../app.css';

  const SUGGESTIONS = [
    'Wie viele Urlaubstage habe ich?',
    'Was ist die Kernarbeitszeit?',
    'Wie viele Homeoffice-Tage sind erlaubt?',
    'Wie reiche ich Spesen ein?',
    'Wie lange dauert das Onboarding?',
    'Was ist mein Equipment-Budget?',
    'Welche Tools nutzen wir im Team?',
    'Wann finden Leistungsbeurteilungen statt?',
  ];

  type Message = { role: 'user' | 'bot'; text: string; sources?: number[] };

  let messages = $state<Message[]>([]);
  let input = $state('');
  let loading = $state(false);
  let chatEl = $state<HTMLDivElement | null>(null);

  async function ask(question: string) {
    if (!question.trim() || loading) return;
    messages = [...messages, { role: 'user', text: question }];
    input = '';
    loading = true;
    setTimeout(() => chatEl?.scrollTo({ top: chatEl.scrollHeight, behavior: 'smooth' }), 50);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      messages = [...messages, { role: 'bot', text: data.answer, sources: data.sources }];
    } catch {
      messages = [...messages, { role: 'bot', text: 'Fehler beim Abrufen der Antwort. Bitte versuche es erneut.' }];
    } finally {
      loading = false;
      setTimeout(() => chatEl?.scrollTo({ top: chatEl.scrollHeight, behavior: 'smooth' }), 50);
    }
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      ask(input);
    }
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
          <h1>PDF Wissens-Bot</h1>
          <p class="subtitle">Autonomika GmbH — Mitarbeiterhandbuch</p>
        </div>
      </div>
      <span class="demo-badge">
        <span class="pulse"></span>
        DEMO
      </span>
    </div>
  </header>

  <!-- Info banner -->
  <div class="banner">
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" style="flex-shrink:0;margin-top:1px">
      <path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
    </svg>
    <span>Dieses Demo durchsucht ein <strong>fiktives Mitarbeiterhandbuch</strong>. Alle Angaben sind erfunden. Die KI antwortet mit Seitenangabe aus dem Dokument.</span>
  </div>

  <main>
    <!-- Suggestions -->
    {#if messages.length === 0}
      <div class="suggestions">
        <p class="suggestions-label">Häufige Fragen — einfach anklicken:</p>
        <div class="chips">
          {#each SUGGESTIONS as s}
            <button class="chip" onclick={() => ask(s)}>{s}</button>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Chat -->
    <div class="chat" bind:this={chatEl}>
      {#each messages as msg}
        {#if msg.role === 'user'}
          <div class="msg user">
            <div class="bubble user-bubble">{msg.text}</div>
          </div>
        {:else}
          <div class="msg bot">
            <div class="bot-avatar">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
            </div>
            <div>
              <div class="bubble bot-bubble">{msg.text}</div>
              {#if msg.sources && msg.sources.length > 0}
                <div class="sources">
                  <span class="sources-label">Quellen:</span>
                  {#each msg.sources as page}
                    <span class="source-badge">Seite {page}</span>
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
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          </div>
          <div class="bubble bot-bubble typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      {/if}
    </div>
  </main>

  <!-- Input -->
  <div class="input-bar">
    <div class="input-inner">
      {#if messages.length > 0}
        <button class="chip-small" onclick={() => ask(SUGGESTIONS[Math.floor(Math.random() * SUGGESTIONS.length)])}>
          Neue Frage vorschlagen
        </button>
      {/if}
      <div class="input-row">
        <input
          type="text"
          placeholder="Stelle eine Frage zum Handbuch..."
          bind:value={input}
          onkeydown={onKeydown}
          disabled={loading}
        />
        <button class="send-btn" onclick={() => ask(input)} disabled={loading || !input.trim()}>
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer>
    Demo von <a href="https://desmond.autonomika.de" target="_blank">Desmond Wong</a> &mdash;
    Stack: Qdrant · nomic-embed-text · Groq · SvelteKit
  </footer>

</div>

<style>
  .wrapper {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    max-width: 800px;
    margin: 0 auto;
  }

  header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid #1e293b;
    padding: 0 1.25rem;
  }
  .header-inner {
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .header-left { display: flex; align-items: center; gap: 0.75rem; }
  .icon {
    width: 36px; height: 36px;
    background: rgba(251,191,36,0.1);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: #fbbf24;
  }
  h1 { font-size: 1rem; font-weight: 700; color: #f1f5f9; }
  .subtitle { font-size: 0.75rem; color: #64748b; }
  .demo-badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.7rem; font-weight: 600;
    color: #fbbf24;
    background: rgba(251,191,36,0.1);
    border: 1px solid rgba(251,191,36,0.2);
    padding: 3px 10px; border-radius: 999px;
  }
  .pulse {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #fbbf24;
    animation: pulse 1.5s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  .banner {
    display: flex; gap: 0.6rem; align-items: flex-start;
    background: rgba(30,41,59,0.8);
    border-bottom: 1px solid #1e293b;
    padding: 0.65rem 1.25rem;
    font-size: 0.8rem; color: #94a3b8;
    line-height: 1.5;
  }
  .banner strong { color: #cbd5e1; }

  main {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 1.25rem;
    gap: 1rem;
    overflow: hidden;
  }

  .suggestions { display: flex; flex-direction: column; gap: 0.75rem; }
  .suggestions-label { font-size: 0.75rem; color: #475569; }
  .chips { display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .chip {
    font-size: 0.8rem; color: #94a3b8;
    background: #1e293b; border: 1px solid #334155;
    padding: 0.4rem 0.85rem; border-radius: 999px;
    cursor: pointer; transition: all 0.15s;
    text-align: left;
  }
  .chip:hover { background: #334155; color: #f1f5f9; border-color: #fbbf24; }

  .chat {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding-bottom: 0.5rem;
  }

  .msg { display: flex; gap: 0.6rem; }
  .msg.user { justify-content: flex-end; }
  .msg.bot { justify-content: flex-start; align-items: flex-start; }

  .bubble {
    max-width: 80%;
    padding: 0.65rem 0.9rem;
    border-radius: 16px;
    font-size: 0.875rem;
    line-height: 1.6;
    white-space: pre-wrap;
  }
  .user-bubble {
    background: #fbbf24; color: #1c1917;
    border-bottom-right-radius: 4px; font-weight: 500;
  }
  .bot-bubble {
    background: #1e293b; color: #e2e8f0;
    border-bottom-left-radius: 4px;
    border: 1px solid #334155;
  }
  .bot-avatar {
    width: 28px; height: 28px; flex-shrink: 0;
    background: rgba(251,191,36,0.1);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: #fbbf24; margin-top: 2px;
  }

  .sources { display: flex; align-items: center; gap: 0.4rem; margin-top: 0.4rem; flex-wrap: wrap; }
  .sources-label { font-size: 0.7rem; color: #475569; }
  .source-badge {
    font-size: 0.68rem; font-weight: 600;
    color: #fbbf24; background: rgba(251,191,36,0.1);
    border: 1px solid rgba(251,191,36,0.2);
    padding: 1px 7px; border-radius: 4px;
  }

  .typing { display: flex; align-items: center; gap: 4px; padding: 0.75rem 1rem; }
  .typing span {
    width: 6px; height: 6px; border-radius: 50%;
    background: #475569; animation: bounce 1.2s ease-in-out infinite;
  }
  .typing span:nth-child(2) { animation-delay: 0.2s; }
  .typing span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-6px); }
  }

  .input-bar {
    border-top: 1px solid #1e293b;
    padding: 0.75rem 1.25rem;
    background: rgba(15,23,42,0.95);
  }
  .input-inner { display: flex; flex-direction: column; gap: 0.5rem; }
  .chip-small {
    align-self: flex-start;
    font-size: 0.72rem; color: #475569;
    background: transparent; border: 1px solid #334155;
    padding: 0.25rem 0.65rem; border-radius: 999px;
    cursor: pointer; transition: all 0.15s;
  }
  .chip-small:hover { color: #94a3b8; border-color: #475569; }

  .input-row { display: flex; gap: 0.5rem; }
  input {
    flex: 1;
    background: #1e293b; border: 1px solid #334155;
    color: #e2e8f0; border-radius: 12px;
    padding: 0.65rem 1rem; font-size: 0.875rem;
    outline: none; transition: border-color 0.15s;
  }
  input:focus { border-color: #fbbf24; }
  input::placeholder { color: #475569; }
  input:disabled { opacity: 0.5; }

  .send-btn {
    width: 42px; height: 42px;
    background: #fbbf24; color: #1c1917;
    border: none; border-radius: 12px;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: background 0.15s; flex-shrink: 0;
  }
  .send-btn:hover:not(:disabled) { background: #f59e0b; }
  .send-btn:disabled { opacity: 0.4; cursor: default; }

  footer {
    text-align: center; font-size: 0.72rem; color: #334155;
    padding: 0.75rem; border-top: 1px solid #1e293b;
  }
  footer a { color: #475569; text-decoration: none; }
  footer a:hover { color: #94a3b8; }
</style>
