<script lang="ts">
	// Ethics Agreement Page
	// Requirements: 3.1, 3.2, 3.3
	
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { marked } from 'marked';
	import Header from '$lib/components/Header.svelte';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	interface EthicsAgreement {
		version: string;
		content: string;
		effective_date: string;
	}
	
	// State
	let user = $state<any>(null);
	let agreement = $state<EthicsAgreement | null>(null);
	let loading = $state(true);
	let accepting = $state(false);
	let error = $state('');
	let successMessage = $state('');
	let hasAccepted = $state(false);
	let acceptanceChecked = $state(false);
	
	// Render markdown content as HTML
	let renderedContent = $derived(agreement?.content ? marked(agreement.content) : '');
	
	onMount(async () => {
		// Check authentication
		const isAuth = await authStore.checkAuth();
		if (!isAuth) {
			goto('/login');
			return;
		}
		
		// Get user from store
		authStore.subscribe(state => {
			user = state.user;
		});
		
		// Load agreement and status
		await loadAgreement();
		await checkAcceptanceStatus();
	});
	
	async function loadAgreement() {
		loading = true;
		error = '';
		
		try {
			const response = await fetch(`${API}/api/ethics/current`, {
				credentials: 'include'
			});
			
			if (!response.ok) {
				throw new Error('Failed to load ethics agreement');
			}
			
			const data = await response.json();
			agreement = data.agreement;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load agreement';
			console.error('Agreement load error:', err);
		} finally {
			loading = false;
		}
	}
	
	async function checkAcceptanceStatus() {
		try {
			const response = await fetch(`${API}/api/ethics/status`, {
				credentials: 'include'
			});
			
			if (response.ok) {
				const data = await response.json();
				hasAccepted = data.status?.has_accepted || false;
			}
		} catch (err) {
			console.error('Failed to check acceptance status:', err);
		}
	}
	
	async function handleAccept() {
		if (!acceptanceChecked) {
			error = 'Please check the box to confirm you have read and agree to the terms';
			return;
		}
		
		if (!agreement) {
			error = 'No agreement loaded';
			return;
		}
		
		accepting = true;
		error = '';
		successMessage = '';
		
		try {
			const response = await fetch(`${API}/api/ethics/accept`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({
					agreement_version: agreement.version,
					ip_address: null // Will be captured by backend
				})
			});
			
			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail?.message || errorData.detail || 'Failed to accept agreement');
			}
			
			successMessage = 'Ethics agreement accepted successfully!';
			hasAccepted = true;
			
			// Redirect to dashboard after a short delay
			setTimeout(() => {
				goto('/dashboard');
			}, 2000);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to accept agreement';
			console.error('Accept error:', err);
		} finally {
			accepting = false;
		}
	}
	
	function formatDate(dateString: string): string {
		try {
			const date = new Date(dateString);
			return date.toLocaleDateString('en-US', {
				year: 'numeric',
				month: 'long',
				day: 'numeric'
			});
		} catch {
			return dateString;
		}
	}
</script>

<svelte:head>
	<title>Ethics Agreement - Accessify</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<Header showAuth={false} />
	
	<!-- Page Header -->
	<div class="bg-white shadow">
		<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<div class="flex items-center justify-between">
				<h1 class="text-2xl font-bold text-gray-900">Ethics Agreement</h1>
				<a
					href="/dashboard"
					class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
				>
					<svg class="mr-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
					</svg>
					Back to Dashboard
				</a>
			</div>
		</div>
	</div>

	<!-- Main Content -->
	<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="flex items-center gap-3">
					<div class="animate-spin h-8 w-8 rounded-full border-4 border-blue-600 border-t-transparent"></div>
					<span class="text-gray-600">Loading agreement...</span>
				</div>
			</div>
		{:else if error && !agreement}
			<div class="rounded-lg bg-red-50 border border-red-200 p-4" role="alert">
				<div class="flex">
					<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
					</svg>
					<div class="ml-3">
						<p class="text-sm text-red-700">{error}</p>
						<button
							onclick={loadAgreement}
							class="mt-2 text-sm font-medium text-red-700 hover:text-red-600 underline"
						>
							Try again
						</button>
					</div>
				</div>
			</div>
		{:else if agreement}
			<!-- Success Message -->
			{#if successMessage}
				<div class="mb-6 rounded-lg bg-green-50 border border-green-200 p-4" role="alert">
					<div class="flex">
						<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<p class="text-sm text-green-700">{successMessage}</p>
							<p class="mt-1 text-xs text-green-600">Redirecting to dashboard...</p>
						</div>
					</div>
				</div>
			{/if}
			
			<!-- Already Accepted Notice -->
			{#if hasAccepted && !successMessage}
				<div class="mb-6 rounded-lg bg-blue-50 border border-blue-200 p-4" role="alert">
					<div class="flex">
						<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<p class="text-sm text-blue-700">You have already accepted this version of the ethics agreement.</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Agreement Card -->
			<div class="bg-white shadow rounded-lg overflow-hidden">
				<!-- Agreement Header -->
				<div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
					<div class="flex items-center justify-between">
						<div>
							<h2 class="text-lg font-semibold text-gray-900">
								Accessify Ethics Agreement
							</h2>
							<p class="mt-1 text-sm text-gray-600">
								Version {agreement.version}
								{#if agreement.effective_date}
									<span class="text-gray-400">•</span>
									<span>Effective {formatDate(agreement.effective_date)}</span>
								{/if}
							</p>
						</div>
					</div>
				</div>

				<!-- Agreement Content -->
				<div class="px-6 py-8">
					<article class="max-w-none text-gray-700 space-y-6">
						<div class="
							[&>h1]:text-2xl [&>h1]:font-bold [&>h1]:text-gray-900 [&>h1]:mb-6
							[&>h2]:text-xl [&>h2]:font-semibold [&>h2]:text-gray-900 [&>h2]:mt-8 [&>h2]:mb-4
							[&>h3]:text-lg [&>h3]:font-semibold [&>h3]:text-gray-900 [&>h3]:mt-6 [&>h3]:mb-3
							[&>p]:mb-4 [&>p]:leading-7 [&>p]:text-gray-700
							[&>ul]:my-4 [&>ul]:ml-6 [&>ul]:space-y-2 [&>ul]:list-disc
							[&>ol]:my-4 [&>ol]:ml-6 [&>ol]:space-y-2 [&>ol]:list-decimal
							[&>li]:leading-7 [&>li]:text-gray-700
							[&>strong]:font-semibold [&>strong]:text-gray-900
							[&>em]:italic
							[&>a]:text-blue-600 [&>a]:underline [&>a]:hover:text-blue-700
							[&>blockquote]:border-l-4 [&>blockquote]:border-gray-300 [&>blockquote]:pl-4 [&>blockquote]:italic [&>blockquote]:my-4
							[&>hr]:my-8 [&>hr]:border-gray-300
						">
							{@html renderedContent}
						</div>
					</article>
				</div>

				<!-- Acceptance Section -->
				{#if !hasAccepted}
					<div class="bg-gray-50 px-6 py-4 border-t border-gray-200">
						<!-- Error Message -->
						{#if error}
							<div class="mb-4 rounded-lg bg-red-50 border border-red-200 p-3" role="alert">
								<div class="flex">
									<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
									</svg>
									<div class="ml-3">
										<p class="text-sm text-red-700">{error}</p>
									</div>
								</div>
							</div>
						{/if}

						<!-- Acceptance Checkbox -->
						<div class="flex items-start mb-4">
							<div class="flex items-center h-5">
								<input
									id="acceptance-checkbox"
									type="checkbox"
									bind:checked={acceptanceChecked}
									class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
									disabled={accepting}
								/>
							</div>
							<div class="ml-3">
								<label for="acceptance-checkbox" class="text-sm text-gray-700">
									I have read and agree to the terms of this ethics agreement
								</label>
							</div>
						</div>

						<!-- Accept Button -->
						<button
							onclick={handleAccept}
							disabled={!acceptanceChecked || accepting}
							class="w-full inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600"
						>
							{#if accepting}
								<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Accepting...
							{:else}
								Accept Agreement
							{/if}
						</button>
					</div>
				{/if}
			</div>
		{/if}
	</main>
</div>
