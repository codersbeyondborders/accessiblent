<script lang="ts">
  // ---- Config ----
  const API = import.meta.env.VITE_API_BASE as string;
  import logo from '../lib/assets/logo.png'; 
  
  // ---- App State ----
  let url = '';
  let pageId: number | null = null;
  let statusMsg = '';
  let isProcessing = false;

  // Results
  let summary = '';
  let issuesTotal: number | null = null;
  let byType: Record<string, number> | null = null;

  // Viewer
  let originalHtml = '';
  let iframeHtml = '';
  let fontPct = 100;
  let highContrast = false;

  // Chat
  type ChatMsg = { role: 'user'|'assistant'; text: string; ts: number };
  let question = '';
  let answer = '';
  let chat: ChatMsg[] = [];

  // Per-session question limit per website
  const MAX_Q = 3;
  let questionCount = 0;  // reset on new process / resetAll

  // Speech (TTS)
  let speaking = false;
  let paused = false;
  let currentUtterance: SpeechSynthesisUtterance | null = null;

  // Reactive binding for iframe srcdoc
  $: srcdoc = iframeHtml;

  // ---- Utils ----
  function setStatus(msg: string) { statusMsg = msg; }

  function normalizeUrl(input: string): string | null {
    let s = (input || '').trim();
    if (!s) return null;
    if (!/^https?:\/\//i.test(s)) s = 'https://' + s;
    try {
      const u = new URL(s);
      if (!u.hostname) return null;
      if (!/^https?:$/i.test(u.protocol)) return null;
      return u.toString();
    } catch { return null; }
  }

  async function call(path: string, method = 'GET', body?: any) {
    const res = await fetch(`${API}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: body ? JSON.stringify(body) : undefined
    });
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`${method} ${path} → ${res.status} ${text}`);
    }
    const ct = res.headers.get('content-type') || '';
    return ct.includes('application/json') ? res.json() : res.text();
  }

  function buildIframeHtml(html: string): string {
    const style = `
      <style id="a11y-controls">
        :root {
          --a11y-font: ${fontPct}%;
          --a11y-bg: ${highContrast ? '#000' : 'initial'};
          --a11y-fg: ${highContrast ? '#fff' : 'initial'};
          --a11y-link: ${highContrast ? '#0ff' : 'initial'};
        }
        html, body {
          font-size: var(--a11y-font);
          background: var(--a11y-bg) !important;
          color: var(--a11y-fg) !important;
        }
        a { color: var(--a11y-link) !important; }
        img, video { max-width: 100%; height: auto; }
      </style>
    `;
    if (html.includes('<head')) return html.replace('<head', `<head>${style}`);
    return `<!doctype html><html><head>${style}</head><body>${html}</body></html>`;
  }

  // ---- Speech controls ----
  function speak(text: string) {
    try {
      stopSpeech();
      if (!text?.trim()) return;
      currentUtterance = new SpeechSynthesisUtterance(text);
      currentUtterance.onend = () => { speaking = false; paused = false; currentUtterance = null; };
      window.speechSynthesis.speak(currentUtterance);
      speaking = true; paused = false;
    } catch { /* ignore */ }
  }
  function pauseSpeech() { if (speaking && !paused) { window.speechSynthesis.pause(); paused = true; } }
  function resumeSpeech() { if (speaking && paused) { window.speechSynthesis.resume(); paused = false; } }
  function stopSpeech() { try { window.speechSynthesis.cancel(); } finally { speaking = false; paused = false; currentUtterance = null; } }

  function incFont() { fontPct = Math.min(220, fontPct + 10); if (originalHtml) iframeHtml = buildIframeHtml(originalHtml); }
  function decFont() { fontPct = Math.max(70, fontPct - 10); if (originalHtml) iframeHtml = buildIframeHtml(originalHtml); }
  function toggleContrast() { highContrast = !highContrast; if (originalHtml) iframeHtml = buildIframeHtml(originalHtml); }

  function resetAll() {
    stopSpeech();
    url = '';
    pageId = null;
    statusMsg = '';
    isProcessing = false;
    summary = '';
    issuesTotal = null;
    byType = null;
    originalHtml = '';
    iframeHtml = '';
    fontPct = 100;
    highContrast = false;
    chat = [];
    question = '';
    answer = '';
    questionCount = 0;
  }

  // ---- Actions ----
  async function processUrl() {
    try {
      stopSpeech();
      const fixed = normalizeUrl(url);
      if (!fixed) { setStatus('Please enter a valid URL, e.g., example.com or https://example.com'); return; }
      isProcessing = true;
      answer = '';
      summary = '';
      byType = null;
      issuesTotal = null;
      pageId = null;
      originalHtml = '';
      iframeHtml = '';
      questionCount = 0;   // reset limit on new website
      chat = [];
      setStatus('Processing…');
      const data = await call(`/process?url=${encodeURIComponent(fixed)}&mode=fast`, 'POST');
      pageId = data.page_id;
      summary = data.summary || '';
      issuesTotal = typeof data.issues === 'number' ? data.issues : null;
      byType = data.by_type || null;
      setStatus('Fetching remediated page…');
      const html = await call(`/output/${pageId}`, 'GET');
      originalHtml = html;
      iframeHtml = buildIframeHtml(originalHtml);
      setStatus('Ready.');
    } catch (e: any) {
      setStatus(e.message || String(e));
    } finally {
      isProcessing = false;
    }
  }

  async function ask() {
    if (!pageId) return;
    const remaining = MAX_Q - questionCount;
    if (remaining <= 0) { setStatus('Limit reached: 3 questions for this website. Click Reset to start over.'); return; }
    const q = question.trim();
    if (!q) return;
    stopSpeech();
    chat = [...chat, { role: 'user', text: q, ts: Date.now() }];
    question = '';
    questionCount += 1;  // count this question
    setStatus(`Thinking… (${MAX_Q - questionCount} left)`);
    try {
      const data = await call(`/chat/${pageId}`, 'POST', { question: q });
      answer = data.answer || '';
      chat = [...chat, { role: 'assistant', text: answer, ts: Date.now() }];
      setStatus(questionCount >= MAX_Q ? 'Question limit reached for this website.' : '');
    } catch (e: any) {
      setStatus(e.message || String(e));
    }
  }

  function onUrlKeydown(e: KeyboardEvent) { if (e.key === 'Enter') { e.preventDefault(); processUrl(); } }
  function onChatKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      ask();
    }
  }
</script>

<svelte:head>
  <title>Accessibility Agent</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 text-gray-900">
  <header class="border-b bg-white">
    <div class="mx-auto w-full max-w-5xl px-4 py-4 text-center">
      <div class="flex justify-center items-center">
        <a href="/" class="align-center">
          <img src={logo} alt="Logo" class="h-16 w-auto">
        </a>
      </div>
      <h6 class="text-lg font-semibold">Accessibilent: Your Smart Accessibility Agent</h6>

      <div class="mt-4 flex space-x-4 justify-center items-center">
        <p class="text-sm text-blue-600 font-semibold">1. Paste a URL</p>
        <p class="text-sm text-green-600 font-semibold">2. Process</p>
        <p class="text-sm text-red-600 font-semibold">3. Read & Chat</p>
      </div>

    </div>
  </header>

  <main id="main" class="mx-auto w-full max-w-5xl px-4 py-6 space-y-6" aria-live="polite">
    <!-- URL & Process -->
    <section class="bg-white rounded-2xl shadow p-4 space-y-4" aria-labelledby="url-sec-h">
      <h2 id="url-sec-h" class="sr-only">Enter website URL</h2>

      <div>
        <label for="page-url" class="block text-sm font-bold">Website URL</label>
        <div class="mt-1 flex gap-2 items-start">
          <input
            id="page-url"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring focus:ring-blue-200"
            bind:value={url}
            placeholder="example.com or https://example.com"
            type="url"
            inputmode="url"
            on:keydown={onUrlKeydown}
            aria-describedby="url-help"
            aria-invalid={!!statusMsg && !pageId}
          />
          <button
            on:click={processUrl}
            class="flex items-center gap-2 rounded-lg border border-gray-300 bg-gray-800 text-white px-3 py-2 text-sm hover:bg-gray-700 active:bg-gray-700 disabled:opacity-60 cursor-pointer"
            aria-label="Process the page to fix accessibility and prepare chat"
            disabled={isProcessing}
          >
            {#if isProcessing}
              <span class="animate-spin h-4 w-4 rounded-full border-2 border-white border-t-transparent"></span>
              <span>Processing…</span>
            {:else}
              Process
            {/if}
          </button>
          <button
            on:click={resetAll}
            class="rounded-lg border border-gray-500 bg-white px-3 py-2 text-sm text-gray-900 hover:bg-gray-100"
            aria-label="Reset the current session"
          >
            Reset
          </button>
        </div>
        <p id="url-help" class="text-xs text-gray-500 mt-1">You can enter with or without http/https. We’ll validate and normalize it.</p>
      </div>

      <div class="flex flex-wrap gap-2" role="group" aria-label="Summary controls">
        {#if pageId}
          <button
            on:click={() => speak(summary || 'No summary available')}
            class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm hover:bg-gray-100"
          >
            Play Summary
          </button>
          <button on:click={pauseSpeech} class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm hover:bg-gray-100" aria-pressed={paused}>Pause</button>
          <button on:click={resumeSpeech} class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm hover:bg-gray-100" aria-pressed={!paused && speaking}>Resume</button>
          <button on:click={stopSpeech} class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm hover:bg-gray-100">Stop</button>
        {/if}
      </div>

      <p class="text-sm text-gray-700 min-h-5" aria-live="polite">{statusMsg}</p>

      {#if summary}
        <div class="rounded-lg bg-blue-50 border border-blue-200 p-3">
          <h3 class="font-semibold mb-1">Summary</h3>
          <pre class="whitespace-pre-wrap text-sm">{summary}</pre>
        </div>
      {/if}

      {#if typeof issuesTotal === 'number'}
        <div class="text-sm text-gray-700">
          <span class="font-medium">Issues fixed:</span> {issuesTotal}
          {#if byType}
            <ul class="list-disc list-inside">
              {#each Object.entries(byType) as [k, v]}
                <li>{k}: {v}</li>
              {/each}
            </ul>
          {/if}
        </div>
      {/if}
    </section>

    <!-- Viewer & A11y Controls -->
    {#if pageId}
      <section class="bg-white rounded-2xl shadow p-4 space-y-3" aria-labelledby="viewer-h">
        <h2 id="viewer-h" class="text-lg font-semibold">Remediated Page Viewer</h2>
        <div class="flex flex-wrap items-center gap-2" role="group" aria-label="Viewer controls">
          <button on:click={decFont} class="rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100" aria-label="Decrease text size">A−</button>
          <button on:click={incFont} class="rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100" aria-label="Increase text size">A+</button>
          <button on:click={toggleContrast} class="rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100" aria-pressed={highContrast} aria-label="Toggle high contrast">
            {highContrast ? 'Normal Contrast' : 'High Contrast'}
          </button>
          <button on:click={() => speak('Viewer loaded. Use A plus, A minus, and High Contrast to adjust readability.')} class="rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100">
            Read Instructions
          </button>
        </div>

        <div class="border rounded-lg overflow-hidden">
          <iframe
            title="Remediated page"
            class="w-full h-[70vh] bg-white"
            {srcdoc}
            sandbox="allow-same-origin allow-forms allow-popups"
          />
        </div>
      </section>
    {/if}

     <!-- Chat -->
     {#if pageId}
     <section class="bg-white rounded-2xl shadow p-4 space-y-3" aria-labelledby="chat-h">
       <div class="flex items-baseline justify-between">
         <h2 id="chat-h" class="text-lg font-semibold">Chat about this page</h2>
         <p class="text-xs text-gray-600">Questions left: {Math.max(0, MAX_Q - questionCount)}</p>
       </div>

       {#if questionCount >= MAX_Q}
         <div class="rounded-lg border border-amber-300 bg-amber-50 p-2 text-sm text-amber-800" role="alert">
           You’ve reached the limit of {MAX_Q} questions for this website. Click <button class="underline" on:click={resetAll}>Reset</button> to start over.
         </div>
       {/if}

       <div class="flex gap-2 items-start">
         <textarea
           class="flex-1 rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring focus:ring-blue-200 min-h-[44px] max-h-40 disabled:opacity-60"
           bind:value={question}
           placeholder={questionCount >= MAX_Q ? 'Limit reached — Reset to continue' : 'e.g., Give me a short summary of this website'}
           on:keydown={onChatKeydown}
           aria-label="Message"
           disabled={questionCount >= MAX_Q}

         />
         <div class="flex flex-col gap-2">
           <button on:click={ask} class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm hover:bg-gray-100 disabled:opacity-60" disabled={questionCount >= MAX_Q}>Ask</button>
         </div>
       </div>

       <!-- Chat transcript -->
       <div class="space-y-2 max-h-[40vh] overflow-auto" aria-live="polite">
         {#each chat as m (m.ts)}
           <div class="flex {m.role === 'user' ? 'justify-end' : 'justify-start'}">
             <div class="{m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'} rounded-2xl px-3 py-2 max-w-[80%]">
               <p class="whitespace-pre-wrap text-sm">{m.text}</p>
               {#if m.role === 'assistant'}
                 <div class="mt-2 flex gap-2">
                   <button on:click={() => speak(m.text)} class="rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100" aria-label="Play this answer">Play</button>
                   <button on:click={pauseSpeech} class="rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100" aria-label="Pause reading">Pause</button>
                   <button on:click={resumeSpeech} class="rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100" aria-label="Resume reading">Resume</button>
                   <button on:click={stopSpeech} class="rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100" aria-label="Stop reading">Stop</button>
                 </div>
               {/if}
             </div>
           </div>
         {/each}
       </div>
     </section>
   {/if}
    
  </main>
</div>
