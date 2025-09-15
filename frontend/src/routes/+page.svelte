<script lang="ts">
  // ---- Config ----
  const API = import.meta.env.VITE_API_BASE as string;
  import logo from '../lib/assets/logo.png'; 
  
  // ---- App State ----
  let url = '';
  let pageId: number | null = null;
  let statusMsg = '';
  let isProcessing = false;
  let isThinking = false;

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

  // Toggles (all hidden by default)
  let showSummary = false;
  let showIframe = false;
  let showChat = false;

  // Which panel is visible: 'summary' | 'iframe' | 'chat' | null
  let activeView: 'summary' | 'iframe' | 'chat' | null = null;

  // Optional: helper for opening new tab
  function openInNewTab() {
    if (!pageId) return;
    const urlOut = `${API}/output/${pageId}`;
    window.open(urlOut, '_blank', 'noopener,noreferrer');
  }
  
  // When starting a new Process, hide all (inside processUrl(), after you clear prior state)
  activeView = 'summary';  

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
      showSummary = false;
      showIframe = false;
      showChat = false;
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
    isThinking = true;
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
      isThinking = false;
    } catch (e: any) {
      setStatus(e.message || String(e));
      isThinking = false;
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
  <title>Accessiblent: Your Smart Accessibility Agent</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 text-gray-900">
  <header class="border-b bg-white">
    <div class="mx-auto w-full max-w-5xl px-4 py-4 text-center">
      <div class="flex justify-center items-center">
        <nav><a on:click={resetAll} class="cursor-pointer align-center" title="Go to home page">
          <img src={logo} alt="Accessibilent Logo" class="h-16 w-auto">
        </a>
        </nav>
      </div>
      <h6 class="text-lg">Your Smart Accessibility Agent</h6>

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
            class="cursor-pointer flex items-center gap-2 rounded-lg border border-gray-300 bg-gray-800 text-white px-3 py-2 text-sm hover:bg-gray-700 active:bg-gray-700 disabled:opacity-60 cursor-pointer"
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
            class="cursor-pointer rounded-lg border border-gray-500 bg-white px-3 py-2 text-sm text-gray-900 hover:bg-gray-100"
            aria-label="Reset the current session"
          >
            Reset
          </button>
        </div>
        <p id="url-help" class="text-xs text-gray-500 mt-1">You can enter with or without http/https. We’ll validate and normalize it.</p>
      </div>

      <!-- toggle toolbar -->
      {#if pageId}
      <div class="mt-8 flex flex-wrap gap-10 justify-between items-center  " role="toolbar" aria-label="Website actions">
        <div class="flex flex-col items-center border border-gray-300 py-2 px-4 bg-gray-600">
          <h4 class="text-md text-white mb-1">Summarize the Website</h4>
          <button
            type="button"
            class="cursor-pointer flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm hover:bg-gray-200 aria-pressed:font-semibold"
            aria-controls="summary-panel"
            aria-label="Summarize the Website"
            aria-pressed={activeView === 'summary'}
            on:click={() => (activeView = activeView === 'summary' ? null : 'summary')}
          >
            <svg class="h-4 w-4 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M8.75 5C8.33579 5 8 5.33579 8 5.75C8 6.16421 8.33579 6.5 8.75 6.5H15.25C15.6642 6.5 16 6.16421 16 5.75C16 5.33579 15.6642 5 15.25 5H8.75Z" fill="#212121"/>
<path d="M8.75 9C8.33579 9 8 9.33579 8 9.75C8 10.1642 8.33579 10.5 8.75 10.5H15.25C15.6642 10.5 16 10.1642 16 9.75C16 9.33579 15.6642 9 15.25 9H8.75Z" fill="#212121"/>
<path d="M8 13.75C8 13.3358 8.33579 13 8.75 13H15.25C15.6642 13 16 13.3358 16 13.75C16 14.1642 15.6642 14.5 15.25 14.5H8.75C8.33579 14.5 8 14.1642 8 13.75Z" fill="#212121"/>
<path d="M8.75 17C8.33579 17 8 17.3358 8 17.75C8 18.1642 8.33579 18.5 8.75 18.5H15.25C15.6642 18.5 16 18.1642 16 17.75C16 17.3358 15.6642 17 15.25 17H8.75Z" fill="#212121"/>
</svg>
            <span>Summarize</span>
          </button>
        </div>
      
        <div class="flex flex-col items-center border border-gray-300 py-2 px-4 bg-gray-600">
          <h4 class="text-md text-white mb-1">View Accessible Version</h4>
          <div class="relative inline-flex gap-2">
            <button
              type="button"
              class="flex items-center gap-2 rounded-lg border border-gray-300 cursor-pointer bg-white px-4 py-2 text-sm hover:bg-gray-200 rounded-l-lg aria-pressed:font-semibold"
              aria-pressed={activeView === 'iframe'}
              aria-controls="iframe-panel"
              on:click={() => (activeView = activeView === 'iframe' ? null : 'iframe')}
            >
              <span class="">Open inline</span>
              <svg class="h-4 w-4 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M7.05025 1.53553C8.03344 0.552348 9.36692 0 10.7574 0C13.6528 0 16 2.34721 16 5.24264C16 6.63308 15.4477 7.96656 14.4645 8.94975L12.4142 11L11 9.58579L13.0503 7.53553C13.6584 6.92742 14 6.10264 14 5.24264C14 3.45178 12.5482 2 10.7574 2C9.89736 2 9.07258 2.34163 8.46447 2.94975L6.41421 5L5 3.58579L7.05025 1.53553Z" fill="#000000"/>
<path d="M7.53553 13.0503L9.58579 11L11 12.4142L8.94975 14.4645C7.96656 15.4477 6.63308 16 5.24264 16C2.34721 16 0 13.6528 0 10.7574C0 9.36693 0.552347 8.03344 1.53553 7.05025L3.58579 5L5 6.41421L2.94975 8.46447C2.34163 9.07258 2 9.89736 2 10.7574C2 12.5482 3.45178 14 5.24264 14C6.10264 14 6.92742 13.6584 7.53553 13.0503Z" fill="#000000"/>
<path d="M5.70711 11.7071L11.7071 5.70711L10.2929 4.29289L4.29289 10.2929L5.70711 11.7071Z" fill="#000000"/>
</svg>
            </button>
            <button
              type="button"
              class="flex items-center gap-2 rounded-lg border border-gray-300 cursor-pointer bg-white px-4 py-2 text-sm hover:bg-gray-200 rounded-r-lg"
              aria-label="Open remediated page in a new browser tab"
              on:click={openInNewTab}
            >
              <span class="">Open in new tab</span>
              <svg class="h-4 w-4 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </button>
          </div>
        </div>
      
        <div class="flex flex-col items-center border border-gray-300 py-2 px-4 bg-gray-600">
          <h4 class="text-md text-white mb-1">Ask questions about this Website</h4>
          <button
            type="button"
            class="cursor-pointer flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm hover:bg-gray-200 aria-pressed:font-semibold"
            aria-label="Chat and ask questions about the website"
            aria-pressed={activeView === 'chat'}
            aria-controls="chat-panel"
            on:click={() => (activeView = activeView === 'chat' ? null : 'chat')}
          >
            <svg class="h-4 w-4 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 13.5997 2.37562 15.1116 3.04346 16.4525C3.22094 16.8088 3.28001 17.2161 3.17712 17.6006L2.58151 19.8267C2.32295 20.793 3.20701 21.677 4.17335 21.4185L6.39939 20.8229C6.78393 20.72 7.19121 20.7791 7.54753 20.9565C8.88837 21.6244 10.4003 22 12 22Z" stroke="#1C274C" stroke-width="1.5"/>
            </svg>
            <span>Chat</span>
          </button>
        </div>
      </div>
      
      {/if} 

      {#if summary && activeView === 'summary'}
      <section id="summary-panel" class="rounded-lg bg-blue-50 border border-blue-200 p-3" aria-labelledby="summary-h">
      <h3 id="summary-h" class="font-semibold mb-1">Summary</h3>
      <pre class="whitespace-pre-wrap text-sm">{summary}</pre>
      <div class="mt-2 flex gap-2">
        <button on:click={() => speak(summary)} class="cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100">Play</button>
        <button on:click={pauseSpeech} class="cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100">Pause</button>
        <button on:click={resumeSpeech} class="cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100">Resume</button>
        <button on:click={stopSpeech} class="cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100">Stop</button>
      </div>
    </section>
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
    {/if}

    <!-- Viewer & A11y Controls -->
    {#if pageId && activeView === 'iframe'}
    <section id="iframe-panel" class="bg-white rounded-2xl shadow p-4 space-y-3" aria-labelledby="viewer-h">
    <h2 id="viewer-h" class="text-lg font-semibold">Remediated Page Viewer</h2>
    <div class="flex flex-wrap items-center gap-2" role="group" aria-label="Viewer controls">
      <button on:click={decFont} class="cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100" aria-label="Decrease text size">A−</button>
      <button on:click={incFont} class="cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100" aria-label="Increase text size">A+</button>
      <button on:click={toggleContrast} class="cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100" aria-pressed={highContrast} aria-label="Toggle high contrast">
        {highContrast ? 'Normal Contrast' : 'High Contrast'}
      </button>
      <button on:click={() => speak('Use A plus, A minus, and High Contrast to adjust readability.')} class="cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-1 text-sm hover:bg-gray-100">
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
     {#if pageId && activeView === 'chat'}
     <section id="chat-panel" class="bg-white rounded-2xl shadow p-4 space-y-3" aria-labelledby="chat-h">
      <div class="flex items-baseline justify-between">
         <h2 id="chat-h" class="text-lg font-semibold">Chat about this website</h2>
         <p class="text-xs text-gray-600">Questions left: {Math.max(0, MAX_Q - questionCount)}</p>
       </div>

       {#if questionCount >= MAX_Q}
         <div class="rounded-lg border border-amber-300 bg-amber-50 p-2 text-sm text-amber-800" role="alert">
           You’ve reached the limit of {MAX_Q} questions for this website. Click <button class="cursor-pointer underline" on:click={resetAll}>Reset</button> to start over.
         </div>
       {/if}

       <div class="flex gap-2 items-start">
         <textarea
           class="flex-1 rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring focus:ring-blue-200 min-h-[44px] max-h-40 disabled:opacity-60"
           bind:value={question}
           placeholder={questionCount >= MAX_Q ? 'Limit reached — Reset to continue' : 'e.g., Give me a short summary of this website'}
           on:keydown={onChatKeydown}
           aria-label="Message"
           disabled={isThinking || questionCount >= MAX_Q}

         />
         <div class="flex flex-col gap-2">
           <button on:click={ask} class="cursor-pointer rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm hover:bg-gray-100 disabled:opacity-60" disabled={questionCount >= MAX_Q}>
            {#if isThinking}
              <span class="animate-spin h-4 w-4 rounded-full border-2 border-white border-t-transparent"></span>
              <span>Thinking…</span>
            {:else}
              Ask
            {/if}
          </button>
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
                   <button on:click={() => speak(m.text)} class="cursor-pointer rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100" aria-label="Play this answer">Play</button>
                   <button on:click={pauseSpeech} class="cursor-pointer rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100" aria-label="Pause reading">Pause</button>
                   <button on:click={resumeSpeech} class="cursor-pointer rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100" aria-label="Resume reading">Resume</button>
                   <button on:click={stopSpeech} class="cursor-pointer rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100" aria-label="Stop reading">Stop</button>
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
