<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import ChatMessage from '$lib/components/ChatMessage.svelte';
	import AccessibilityToolbar from '$lib/components/AccessibilityToolbar.svelte';

	const API = (import.meta.env.VITE_API_BASE as string) || '';

	// Get website ID from URL params
	$: websiteId = parseInt($page.params.id || '0');

	// State
	let loading = true;
	let error = '';
	let website: any = null;
	let remediationStatus: any = null;
	let question = '';
	let isThinking = false;
	let chat: Array<{ role: 'user' | 'assistant'; text: string; ts: number }> = [];

	// Question limit
	const MAX_Q = 3;
	let questionCount = 0;

	// Speech (TTS)
	let speaking = false;
	let paused = false;
	let currentUtterance: SpeechSynthesisUtterance | null = null;

	onMount(async () => {
		await loadWebsiteData();
	});

	async function loadWebsiteData() {
		try {
			loading = true;
			error = '';

			// Fetch website details
			const websiteRes = await fetch(`${API}/api/websites/${websiteId}`, {
				credentials: 'include'
			});

			if (!websiteRes.ok) {
				if (websiteRes.status === 401) {
					goto('/login');
					return;
				}
				throw new Error('Failed to load webpage details');
			}

			website = await websiteRes.json();

			// Fetch remediation status
			const statusRes = await fetch(`${API}/api/websites/${websiteId}/status`, {
				credentials: 'include'
			});

			if (statusRes.ok) {
				remediationStatus = await statusRes.json();

				// Check if remediation is complete
				if (!remediationStatus.page || (remediationStatus.page.page_status !== 'complete' && remediationStatus.page.page_status !== 'FIXED')) {
					error = 'This webpage has not been remediated yet. Please complete remediation first.';
				}
			}
		} catch (e: any) {
			error = e.message || 'Failed to load webpage data';
		} finally {
			loading = false;
		}
	}

	async function ask() {
		if (!remediationStatus?.page?.page_id) return;

		const remaining = MAX_Q - questionCount;
		if (remaining <= 0) {
			return;
		}

		const q = question.trim();
		if (!q) return;

		stopSpeech();
		chat = [...chat, { role: 'user', text: q, ts: Date.now() }];
		question = '';
		questionCount += 1;
		isThinking = true;

		try {
			const res = await fetch(`${API}/chat/${remediationStatus.page.page_id}`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({ question: q })
			});

			if (!res.ok) {
				throw new Error('Failed to get response');
			}

			const data = await res.json();
			const answer = data.answer || '';
			chat = [...chat, { role: 'assistant', text: answer, ts: Date.now() }];
		} catch (e: any) {
			error = e.message || 'Failed to get response';
		} finally {
			isThinking = false;
		}
	}

	function onChatKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			ask();
		}
	}

	// Speech controls
	function speak(text: string) {
		try {
			stopSpeech();
			if (!text?.trim()) return;
			currentUtterance = new SpeechSynthesisUtterance(text);
			currentUtterance.onend = () => {
				speaking = false;
				paused = false;
				currentUtterance = null;
			};
			window.speechSynthesis.speak(currentUtterance);
			speaking = true;
			paused = false;
		} catch {
			/* ignore */
		}
	}

	function pauseSpeech() {
		if (speaking && !paused) {
			window.speechSynthesis.pause();
			paused = true;
		}
	}

	function resumeSpeech() {
		if (speaking && paused) {
			window.speechSynthesis.resume();
			paused = false;
		}
	}

	function stopSpeech() {
		try {
			window.speechSynthesis.cancel();
		} finally {
			speaking = false;
			paused = false;
			currentUtterance = null;
		}
	}

	function goBack() {
		goto(`/websites/${websiteId}`);
	}
</script>

<svelte:head>
	<title>Chat - {website?.name || 'Webpage'}</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 pb-16">
	<div class="max-w-4xl mx-auto px-4 py-8">
		<!-- Header -->
		<div class="mb-6">
			<button
				onclick={goBack}
				class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
			>
				<svg
					class="w-4 h-4 mr-2"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 19l-7-7 7-7"
					/>
				</svg>
				Back to Webpage
			</button>

			{#if loading}
				<div class="animate-pulse">
					<div class="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
					<div class="h-4 bg-gray-200 rounded w-1/2"></div>
				</div>
			{:else if website}
				<h1 class="text-3xl font-bold text-gray-900 mb-2">
					Chat with AI
				</h1>
				<div class="text-sm text-gray-600">
					<p class="font-medium">{website.name || 'Unnamed Webpage'}</p>
					<p class="text-gray-500">{website.entry_url}</p>
				</div>
			{/if}
		</div>

		<!-- Accessibility Improvements Summary -->
		{#if remediationStatus?.issues_found > 0}
			<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
				<h2 class="text-sm font-semibold text-blue-900 mb-2">
					Accessibility Improvements Applied
				</h2>
				<p class="text-sm text-blue-800">
					{remediationStatus.issues_found} accessibility issue{remediationStatus.issues_found !== 1
						? 's'
						: ''} fixed on this page. You can ask questions about the content and the improvements made.
				</p>
			</div>
		{/if}

		<!-- Error Message -->
		{#if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
				<p class="text-sm text-red-800">{error}</p>
			</div>
		{/if}

		<!-- Chat Interface -->
		{#if !loading && !error && remediationStatus?.page}
			<div class="bg-white shadow rounded-lg p-6">
				<div class="flex items-baseline justify-between mb-4">
					<h2 class="text-lg font-semibold text-gray-900">Chat about this webpage</h2>
					<p class="text-xs text-gray-600">
						Questions left: {Math.max(0, MAX_Q - questionCount)}
					</p>
				</div>

				{#if questionCount >= MAX_Q}
					<div
						class="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800 mb-4"
						role="alert"
					>
						You've reached the limit of {MAX_Q} questions for this webpage. Refresh the page to start
						over.
					</div>
				{/if}

				<!-- Chat Input -->
				<div class="flex gap-2 items-start mb-4">
					<textarea
						class="flex-1 rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px] max-h-40 disabled:opacity-60"
						bind:value={question}
						placeholder={questionCount >= MAX_Q
							? 'Limit reached — Refresh to continue'
							: 'e.g., What accessibility improvements were made?'}
						onkeydown={onChatKeydown}
						aria-label="Message"
						disabled={isThinking || questionCount >= MAX_Q}
					></textarea>
					<button
						onclick={ask}
						class="rounded-lg bg-blue-600 text-white px-4 py-2 text-sm hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
						disabled={questionCount >= MAX_Q || isThinking}
					>
						{#if isThinking}
							<span class="flex items-center gap-2">
								<span
									class="animate-spin h-4 w-4 rounded-full border-2 border-white border-t-transparent"
								></span>
								<span>Thinking…</span>
							</span>
						{:else}
							Ask
						{/if}
					</button>
				</div>

				<!-- Chat Transcript -->
				<div class="space-y-3 max-h-[60vh] overflow-auto" aria-live="polite">
					{#each chat as m (m.ts)}
						<ChatMessage
							role={m.role}
							text={m.text}
							onSpeak={speak}
							onPause={pauseSpeech}
							onResume={resumeSpeech}
							onStop={stopSpeech}
						/>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>

<AccessibilityToolbar />
