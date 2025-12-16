<script lang="ts">
	import { onMount } from 'svelte';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	interface Website {
		id: number;
		entry_url: string;
		name?: string;
		domain_name?: string;
		status: string;
		last_remediation_at?: string;
		created_at?: string;
	}
	
	let websites = $state<Website[]>([]);
	let loading = $state(true);
	let error = $state('');
	
	onMount(() => {
		loadRemediatedWebsites();
	});
	
	async function loadRemediatedWebsites() {
		loading = true;
		error = '';
		
		try {
			const response = await fetch(`${API}/api/websites/public/remediated`);
			
			if (!response.ok) {
				throw new Error('Failed to load remediated websites');
			}
			
			const data = await response.json();
			websites = data.websites || [];
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load websites';
			console.error('Load error:', err);
		} finally {
			loading = false;
		}
	}
	
	function formatDate(dateString?: string): string {
		if (!dateString) return 'N/A';
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { 
			year: 'numeric', 
			month: 'short', 
			day: 'numeric' 
		});
	}
</script>

<svelte:head>
	<title>Remediated Webpages - Accessify</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<Header showAuth={true} />
	
	<main class="flex-grow py-12">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<!-- Header -->
			<div class="mb-8">
				<h1 class="text-3xl font-bold text-gray-900 mb-2">
					Remediated Webpages
				</h1>
				<p class="text-lg text-gray-600">
					Browse webpages that have been made accessible through our AI-powered remediation
				</p>
			</div>

			{#if loading}
				<div class="bg-white shadow rounded-lg p-12">
					<div class="flex items-center justify-center">
						<div class="flex items-center gap-3">
							<div class="animate-spin h-8 w-8 rounded-full border-4 border-blue-600 border-t-transparent"></div>
							<span class="text-gray-600">Loading remediated webpages...</span>
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
			{:else if websites.length === 0}
				<div class="bg-white shadow rounded-lg p-12 text-center">
					<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
					</svg>
					<h3 class="mt-2 text-lg font-medium text-gray-900">No remediated webpages yet</h3>
					<p class="mt-1 text-sm text-gray-500">
						Check back soon to see webpages that have been made accessible
					</p>
				</div>
			{:else}
				<!-- Webpages Grid -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{#each websites as website}
						<a
							href="/websites/{website.id}"
							class="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow duration-200 border border-gray-200 hover:border-blue-500"
						>
							<div class="flex items-start justify-between mb-4">
								<div class="flex-1 min-w-0">
									<h3 class="text-lg font-semibold text-gray-900 truncate">
										{website.name || 'Unnamed Webpage'}
									</h3>
									{#if website.domain_name}
										<p class="text-sm text-gray-500 mt-1">
											{website.domain_name}
										</p>
									{/if}
								</div>
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 ml-2">
									<svg class="mr-1 h-2 w-2 fill-current text-green-400" viewBox="0 0 8 8">
										<circle cx="4" cy="4" r="3" />
									</svg>
									Remediated
								</span>
							</div>
							
							<div class="space-y-2">
								<div class="flex items-center text-sm text-gray-600">
									<svg class="mr-2 h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
									</svg>
									<span class="truncate">{website.entry_url}</span>
								</div>
								
								{#if website.last_remediation_at}
									<div class="flex items-center text-sm text-gray-500">
										<svg class="mr-2 h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
										</svg>
										<span>Remediated {formatDate(website.last_remediation_at)}</span>
									</div>
								{/if}
							</div>
							
							<div class="mt-4 pt-4 border-t border-gray-200">
								<span class="text-sm font-medium text-blue-600 hover:text-blue-700">
									View Remediated Site →
								</span>
							</div>
						</a>
					{/each}
				</div>
			{/if}
		</div>
	</main>
	
	<Footer />
</div>
