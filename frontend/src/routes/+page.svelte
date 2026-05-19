<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { cn } from '$lib/utils';

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

  const INDUSTRY_CLASSES: Record<string, string> = {
    Technologie: 'text-primary border-primary/30 bg-primary/10',
    Gastronomie: 'text-rose-400 border-rose-400/30 bg-rose-400/10',
    Immobilien:  'text-blue-400 border-blue-400/30 bg-blue-400/10',
  };
</script>

<div class="min-h-screen flex flex-col bg-background">

  <!-- Header -->
  <header class="sticky top-0 z-20 bg-background/95 backdrop-blur border-b border-border">
    <div class="h-13 flex items-center justify-between px-5 max-w-[1400px] mx-auto">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center flex-shrink-0">
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
        </div>
        <div>
          <h1 class="text-sm font-bold text-foreground">PDF Wissens-Bot</h1>
          <p class="text-xs text-muted-foreground hidden sm:block">Dokument wählen → Frage stellen → Antwort mit Seitenangabe</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-wide text-primary bg-primary/10 border border-primary/20 px-2.5 py-1 rounded-full">
          <span class="w-1.5 h-1.5 rounded-full bg-primary animate-pulse-slow"></span>
          DEMO
        </span>
        <a href="https://desmond.autonomika.de" target="_blank"
           class="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
          <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          Portfolio
        </a>
      </div>
    </div>
  </header>

  <!-- Doc selector -->
  <div class="border-b border-border bg-background px-5 py-2.5 flex items-center gap-3 overflow-x-auto">
    <span class="text-[11px] text-muted-foreground whitespace-nowrap flex-shrink-0">Demo-Dokumente:</span>
    <div class="flex gap-2">
      {#each docs as doc}
        <div
          role="button"
          tabindex="0"
          draggable="true"
          onclick={() => selectDoc(doc)}
          onkeydown={(e) => e.key === 'Enter' && selectDoc(doc)}
          ondragstart={(e) => onDragStart(e, doc.id)}
          ondragend={() => draggingId = null}
          title="Klicken oder in Viewer ziehen"
          class={cn(
            'flex items-center gap-2 bg-secondary border rounded-xl px-3 py-2 cursor-grab select-none transition-all whitespace-nowrap',
            activeDoc?.id === doc.id
              ? 'border-primary/60 bg-primary/5'
              : 'border-border hover:border-muted-foreground/50 hover:bg-accent'
          )}
        >
          <svg class={cn('w-4 h-4 flex-shrink-0', activeDoc?.id === doc.id ? 'text-primary' : 'text-muted-foreground')}
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          <div class="flex flex-col">
            <span class="text-[13px] font-semibold text-foreground leading-tight">{doc.name}</span>
            <span class="text-[11px] text-muted-foreground">{doc.description}</span>
          </div>
          <span class={cn('text-[11px] font-semibold px-1.5 py-0.5 rounded border', INDUSTRY_CLASSES[doc.industry] ?? INDUSTRY_CLASSES.Technologie)}>
            {doc.industry}
          </span>
        </div>
      {/each}
    </div>
  </div>

  <!-- Mobile tabs -->
  <div class="flex border-b border-border sm:hidden">
    <button
      onclick={() => mobileTab = 'pdf'}
      class={cn('flex-1 py-2.5 text-sm font-medium border-b-2 transition-colors',
        mobileTab === 'pdf' ? 'text-primary border-primary' : 'text-muted-foreground border-transparent')}
    >Dokument ansehen</button>
    <button
      onclick={() => mobileTab = 'chat'}
      class={cn('flex-1 py-2.5 text-sm font-medium border-b-2 transition-colors',
        mobileTab === 'chat' ? 'text-primary border-primary' : 'text-muted-foreground border-transparent')}
    >Chat</button>
  </div>

  <!-- Split -->
  <div class="flex-1 grid sm:grid-cols-2 min-h-0 overflow-hidden">

    <!-- PDF panel -->
    <div
      class={cn(
        'flex flex-col border-r border-border relative transition-colors',
        dragOver && 'border-primary bg-primary/5',
        mobileTab === 'chat' && 'hidden sm:flex'
      )}
      ondragover={(e) => { e.preventDefault(); dragOver = true; }}
      ondragleave={() => dragOver = false}
      ondrop={onDrop}
      role="region"
      aria-label="PDF Viewer"
    >
      {#if dragOver}
        <div class="absolute inset-0 flex flex-col items-center justify-center gap-3 border-2 border-dashed border-primary bg-primary/5 z-10 pointer-events-none text-primary font-semibold">
          <svg width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m0-15.75h-3.75" />
          </svg>
          Hier ablegen
        </div>
      {:else if activeDoc}
        <div class="flex items-center justify-between px-3 py-2 border-b border-border bg-background flex-shrink-0">
          <span class="text-xs text-muted-foreground truncate">{activeDoc.name} — {activeDoc.description}</span>
          <a href={activeDoc.pdf_url} target="_blank"
             class="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors ml-2 flex-shrink-0">
            <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
            Vollbild
          </a>
        </div>
        <embed
          src="{activeDoc.pdf_url}#page={pdfPage}"
          type="application/pdf"
          class="flex-1 w-full min-h-[60vh]"
          title={activeDoc.name}
        />
      {/if}
    </div>

    <!-- Chat panel -->
    <div class={cn('flex flex-col overflow-hidden', mobileTab === 'pdf' && 'hidden sm:flex')}>

      {#if messages.length === 0 && activeDoc}
        <div class="p-4 flex flex-col gap-2.5">
          <p class="text-xs text-muted-foreground">Häufige Fragen zu diesem Dokument:</p>
          <div class="flex flex-wrap gap-1.5">
            {#each activeDoc.suggestions as s}
              <button
                onclick={() => ask(s)}
                class="text-xs text-muted-foreground bg-secondary border border-border rounded-full px-3 py-1.5 hover:border-muted-foreground/60 hover:text-foreground hover:bg-accent transition-all text-left"
              >{s}</button>
            {/each}
          </div>
        </div>
      {/if}

      <div class="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-3" bind:this={chatEl}>
        {#each messages as msg}
          {#if msg.role === 'user'}
            <div class="flex justify-end">
              <div class="max-w-[85%] bg-primary text-primary-foreground rounded-2xl rounded-br-sm px-3.5 py-2.5 text-sm leading-relaxed font-medium whitespace-pre-wrap">
                {msg.text}
              </div>
            </div>
          {:else}
            <div class="flex gap-2 items-start">
              <div class="w-7 h-7 flex-shrink-0 mt-0.5 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                </svg>
              </div>
              <div>
                <div class="max-w-[85%] bg-secondary border border-border rounded-2xl rounded-bl-sm px-3.5 py-2.5 text-sm leading-relaxed text-foreground whitespace-pre-wrap">
                  {msg.text}
                </div>
                {#if msg.sources && msg.sources.length > 0}
                  <div class="flex items-center gap-1.5 mt-1.5 flex-wrap">
                    <span class="text-[11px] text-muted-foreground">Quellen:</span>
                    {#each msg.sources as page}
                      <button
                        onclick={() => jumpToPage(page)}
                        class="text-[11px] font-semibold text-primary bg-primary/10 border border-primary/25 px-1.5 py-0.5 rounded hover:bg-primary/20 transition-colors"
                        title="Im Viewer anzeigen"
                      >Seite {page}</button>
                    {/each}
                  </div>
                {/if}
              </div>
            </div>
          {/if}
        {/each}

        {#if loading}
          <div class="flex gap-2 items-start">
            <div class="w-7 h-7 flex-shrink-0 mt-0.5 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
              <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
            </div>
            <div class="bg-secondary border border-border rounded-2xl rounded-bl-sm px-3.5 py-3 flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce-dot"></span>
              <span class="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce-dot [animation-delay:0.2s]"></span>
              <span class="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce-dot [animation-delay:0.4s]"></span>
            </div>
          </div>
        {/if}
      </div>

      <!-- Input -->
      <div class="px-3 py-2.5 border-t border-border bg-background/95 flex-shrink-0">
        <div class="flex gap-2">
          <input
            type="text"
            placeholder="Stelle eine Frage zum Dokument..."
            bind:value={input}
            onkeydown={onKeydown}
            disabled={loading || !activeDoc}
            aria-label="Frage eingeben"
            class="flex-1 bg-secondary border border-input text-foreground placeholder:text-muted-foreground rounded-lg px-3.5 py-2 text-sm outline-none focus:border-ring transition-colors disabled:opacity-50"
          />
          <button
            onclick={() => ask(input)}
            disabled={loading || !input.trim() || !activeDoc}
            aria-label="Frage senden"
            class="w-10 h-10 bg-primary text-primary-foreground rounded-lg flex items-center justify-center flex-shrink-0 hover:bg-primary/90 transition-colors disabled:opacity-40 disabled:cursor-default"
          >
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>

  <footer class="text-center text-[11px] text-muted-foreground/50 py-2 border-t border-border">
    Demo von <a href="https://desmond.autonomika.de" target="_blank" class="hover:text-muted-foreground transition-colors">Desmond Wong</a>
    &mdash; Qdrant &middot; nomic-embed-text &middot; Groq &middot; SvelteKit
  </footer>

</div>
