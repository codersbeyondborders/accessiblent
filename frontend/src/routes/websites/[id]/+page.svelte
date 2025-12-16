<script lang="ts">
	// Webpage detail page
	// Requirements: 4.5, 5.1, 6.4, 10.5
	
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth';
	import RemediationProgress from '$lib/components/RemediationProgress.svelte';
	import PreviewPanel from '$lib/components/PreviewPanel.svelte';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import AccessibilityToolbar from '$lib/components/AccessibilityToolbar.svelte';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	interface Website {
		id: number;
		entry_url: string;
		name?: string;
		domain_id: number;
		domain_name?: string;
		domain_verified?: boolean;
		status: string;
		last_remediation_at?: string;
		created_at?: string;
	}
	
	interface RemediationStatus {
		website_id: number;
		status: string;
		last_remediation_at?: string;
		page?: {
			page_id: number;
			page_status: string;
			created_at?: string;
		};
		issues_found?: number;
	}
	
	interface PreviewInfo {
		preview_url: string;
		iframe_snippet: string;
		issue_stats: {
			total_issues: number;
			critical_issues: number;
			serious_issues: number;
		};
	}
	
	// Get website ID from URL
	let websiteId = $derived(parseInt($page.params.id || '0'));
	
	// State
	let website = $state<Website | null>(null);
	let remediationStatus = $state<RemediationStatus | null>(null);
	let previewInfo = $state<PreviewInfo | null>(null);
	let loading = $state(true);
	let remediating = $state(false);
	let error = $state('');
	let pollingInterval: ReturnType<typeof setInterval> | null = null;
	
	onMount(() => {
		// Load website details (no auth required for viewing)
		loadWebsiteDetails().then(() => {
			// If website is processing, start polling
			if (website?.status === 'processing') {
				startPolling();
			}
		});
		
		// Cleanup polling on unmount
		return () => {
			if (pollingInterval) {
				clearInterval(pollingInterval);
			}
		};
	});
	
	async function loadWebsiteDetails() {
		loading = true;
		error = '';
		
		try {
			const response = await fetch(`${API}/api/websites/${websiteId}`, {
				credentials: 'include'
			});
			
			if (!response.ok) {
				if (response.status === 404) {
					error = 'Webpage not found';
				} else if (response.status === 403) {
					error = 'You do not have permission to view this webpage';
				} else {
					throw new Error('Failed to load webpage details');
				}
				return;
			}
			
			const data = await response.json();
			website = data.website;
			
			// Load remediation status
			await loadRemediationStatus();
			
			// Load preview info if remediated
			if (website && website.status === 'remediated') {
				await loadPreviewInfo();
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load webpage';
			console.error('Webpage load error:', err);
		} finally {
			loading = false;
		}
	}
	
	async function loadRemediationStatus() {
		try {
			const response = await fetch(`${API}/api/websites/${websiteId}/status`, {
				credentials: 'include'
			});
			
			if (response.ok) {
				const data = await response.json();
				remediationStatus = data;
			}
		} catch (err) {
			console.error('Failed to load remediation status:', err);
		}
	}
	
	async function loadPreviewInfo() {
		try {
			const response = await fetch(`${API}/api/websites/${websiteId}/preview`, {
				credentials: 'include'
			});
			
			if (response.ok) {
				const data = await response.json();
				previewInfo = data;
			}
		} catch (err) {
			console.error('Failed to load preview info:', err);
		}
	}
	
	async function handleStartRemediation() {
		// Check if user is authenticated
		const isAuth = await authStore.checkAuth();
		if (!isAuth) {
			goto(`/login?redirect=/websites/${websiteId}`);
			return;
		}
		
		remediating = true;
		error = '';
		
		try {
			const response = await fetch(`${API}/api/websites/${websiteId}/remediate`, {
				method: 'POST',
				credentials: 'include'
			});
			
			if (!response.ok) {
				const data = await response.json();
				
				if (data.detail?.code === 'ETHICS_NOT_ACCEPTED') {
					error = 'You must accept the ethics agreement before starting remediation.';
				} else {
					error = data.detail?.message || data.detail || 'Failed to start remediation';
				}
				return;
			}
			
			const data = await response.json();
			
			// Update website status
			if (website) {
				website.status = 'remediated';
			}
			
			// Load preview info
			previewInfo = {
				preview_url: data.preview_url,
				iframe_snippet: data.iframe_snippet,
				issue_stats: {
					total_issues: data.issues_found || 0,
					critical_issues: 0,
					serious_issues: 0,
				}
			};
			
			// Reload status
			await loadRemediationStatus();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to start remediation';
			console.error('Remediation error:', err);
		} finally {
			remediating = false;
		}
	}
	
	function startPolling() {
		pollingInterval = setInterval(async () => {
			await loadRemediationStatus();
			
			// Stop polling if remediation is complete or failed
			if (remediationStatus && 
			    (remediationStatus.status === 'remediated' || 
			     remediationStatus.status === 'error')) {
				if (pollingInterval) {
					clearInterval(pollingInterval);
					pollingInterval = null;
				}
				
				// Reload full details
				await loadWebsiteDetails();
			}
		}, 3000); // Poll every 3 seconds
	}
	
	function handleChatClick() {
		if (remediationStatus?.page?.page_id) {
			goto(`/websites/${websiteId}/chat`);
		}
	}
</script>

<svelte:head>
	<title>{website?.name || 'Webpage'} - Accessify</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50 pb-16">
	<Header showAuth={true} />
	
	<div class="flex-grow py-8">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<a
				href="/dashboard"
				class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
			>
				<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
				</svg>
				Back to Dashboard
			</a>
		</div>

		{#if loading}
			<div class="bg-white shadow rounded-lg p-8">
				<div class="flex items-center justify-center">
					<div class="flex items-center gap-3">
						<div class="animate-spin h-8 w-8 rounded-full border-4 border-blue-600 border-t-transparent"></div>
						<span class="text-gray-600">Loading webpage details...</span>
					</div>
				</div>
			</div>
		{:else if error}
			<div class="rounded-lg bg-red-50 border border-red-200 p-4" role="alert">
				<div class="flex">
					<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
					</svg>
					<div class="ml-3">
						<p class="text-sm text-red-700">{error}</p>
					</div>
				</div>
			</div>
		{:else if website}
			<!-- Webpage Info Card -->
			<div class="bg-white shadow rounded-lg p-6 mb-6">
				<div class="flex items-start justify-between">
					<div class="flex-1">
						<h1 class="text-2xl font-bold text-gray-900">
							{website.name || 'Unnamed Webpage'}
						</h1>
						<div class="mt-2 space-y-1">
							<div class="flex items-center text-sm text-gray-600">
								<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
								</svg>
								<a href={website.entry_url} target="_blank" rel="noopener noreferrer" class="hover:text-blue-600">
									{website.entry_url}
								</a>
							</div>
							{#if website.domain_name}
								<div class="flex items-center text-sm text-gray-600">
									<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
									</svg>
									Domain: <span class="ml-1 font-medium">{website.domain_name}</span>
								</div>
							{/if}
						</div>
					</div>
					
					<!-- Status Badge -->
					<div>
						{#if website.status === 'registered'}
							<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
								<svg class="mr-1.5 h-2 w-2 fill-current text-gray-400" viewBox="0 0 8 8">
									<circle cx="4" cy="4" r="3" />
								</svg>
								Registered
							</span>
						{:else if website.status === 'processing'}
							<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
								<svg class="mr-1.5 h-2 w-2 fill-current text-blue-400 animate-pulse" viewBox="0 0 8 8">
									<circle cx="4" cy="4" r="3" />
								</svg>
								Processing
							</span>
						{:else if website.status === 'remediated'}
							<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
								<svg class="mr-1.5 h-2 w-2 fill-current text-green-400" viewBox="0 0 8 8">
									<circle cx="4" cy="4" r="3" />
								</svg>
								Remediated
							</span>
						{:else if website.status === 'error'}
							<span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
								<svg class="mr-1.5 h-2 w-2 fill-current text-red-400" viewBox="0 0 8 8">
									<circle cx="4" cy="4" r="3" />
								</svg>
								Error
							</span>
						{/if}
					</div>
				</div>
			</div>

			<!-- Remediation Section -->
			{#if website.status === 'registered' || website.status === 'error'}
				<div class="bg-white shadow rounded-lg p-6 mb-6">
					<h2 class="text-lg font-semibold text-gray-900 mb-4">Start Remediation</h2>
					<p class="text-sm text-gray-600 mb-4">
						Begin the accessibility remediation process for this webpage. This will fetch the HTML,
						run an accessibility audit, and apply code-level fixes.
					</p>
					<button
						onclick={handleStartRemediation}
						disabled={remediating}
						class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{#if remediating}
							<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							Starting Remediation...
						{:else}
							<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Start Remediation
						{/if}
					</button>
				</div>
			{:else if website.status === 'processing'}
				<RemediationProgress status={remediationStatus} />
			{:else if website.status === 'remediated' && previewInfo}
				<!-- Preview Panel -->
				<PreviewPanel 
					previewUrl={previewInfo.preview_url}
					iframeSnippet={previewInfo.iframe_snippet}
					issueStats={previewInfo.issue_stats}
				/>
				
				
			{/if}
		{/if}
	</div>
	</div>
	
	<Footer />
</div>

<AccessibilityToolbar />
