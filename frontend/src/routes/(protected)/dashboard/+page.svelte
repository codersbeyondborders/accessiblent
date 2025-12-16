<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { toastStore } from '$lib/stores/toast';

	const API = import.meta.env.VITE_API_BASE as string;

	let domain: any = null;
	let website: any = null;
	let loading = true;

	$: user = $authStore.user;

	onMount(async () => {
		await loadDashboardData();
	});

	async function loadDashboardData() {
		loading = true;
		try {
			// Fetch domain (only one per org)
			const domainsResponse = await fetch(`${API}/api/domains`, {
				credentials: 'include'
			});

			if (domainsResponse.ok) {
				const domainsData = await domainsResponse.json();
				domain = domainsData.domains?.[0] || null;
			}

			// Fetch website (only one per org)
			const websitesResponse = await fetch(`${API}/api/websites`, {
				credentials: 'include'
			});

			if (websitesResponse.ok) {
				const websitesData = await websitesResponse.json();
				website = websitesData.websites?.[0] || null;
			}
		} catch (error) {
			console.error('Failed to load dashboard data:', error);
			toastStore.error('Failed to load dashboard data');
		} finally {
			loading = false;
		}
	}

	function handleViewWebsite() {
		if (website) {
			goto(`/websites/${website.id}`);
		}
	}
</script>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
			{#if user}
				<p class="mt-1 text-sm text-gray-600">
					{user.full_name}
					{#if user.organization_name}
						· {user.organization_name}
					{/if}
				</p>
			{/if}
		</div>

		{#if loading}
			<div class="flex justify-center items-center py-12">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			</div>
		{:else}
			<!-- Domain Section -->
			<div class="mb-6">
				<h2 class="text-lg font-semibold text-gray-900 mb-3">Your Domain</h2>
				{#if !domain}
					<div class="bg-white rounded-lg border border-gray-200 p-6">
						<p class="text-sm text-gray-600 mb-4">Add your domain to get started with accessibility remediation.</p>
						<a
							href="/domains/add"
							class="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
						>
							Add Domain
						</a>
					</div>
				{:else}
					<div class="bg-white rounded-lg border border-gray-200 p-4">
						<div class="flex items-center justify-between">
							<div>
								<p class="font-medium text-gray-900">{domain.domain_name}</p>
								<p class="text-sm text-gray-500 mt-1">
									{#if domain.is_verified}
										<span class="text-green-600">✓ Verified</span>
									{:else}
										<span class="text-yellow-600">⚠ Pending verification</span>
									{/if}
								</p>
							</div>
							{#if !domain.is_verified}
								<a
									href="/domains/{domain.id}/verify"
									class="text-sm text-blue-600 hover:text-blue-700"
								>
									Verify →
								</a>
							{/if}
						</div>
					</div>
				{/if}
			</div>

			<!-- Webpage Section -->
			<div>
				<h2 class="text-lg font-semibold text-gray-900 mb-3">Your Webpages</h2>
				{#if !website}
					<div class="bg-white rounded-lg border border-gray-200 p-6">
						{#if !domain || !domain.is_verified}
							<p class="text-sm text-gray-600">Verify your domain first to register a webpage.</p>
						{:else}
							<p class="text-sm text-gray-600 mb-4">Register your webpage to start accessibility remediation.</p>
							<a
								href="/websites/register"
								class="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
							>
								Register Webpage
							</a>
						{/if}
					</div>
				{:else}
					<div class="bg-white rounded-lg border border-gray-200 p-4">
						<div class="flex items-center justify-between mb-3">
							<div>
								<p class="font-medium text-gray-900">{website.name || 'Unnamed Webpage'}</p>
								<p class="text-sm text-gray-500">{website.entry_url}</p>
							</div>
							<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
								{website.status === 'remediated' ? 'bg-green-100 text-green-800' : 
								 website.status === 'processing' ? 'bg-blue-100 text-blue-800' : 
								 'bg-gray-100 text-gray-800'}">
								{website.status}
							</span>
						</div>
						<button
							onclick={handleViewWebsite}
							class="text-sm text-blue-600 hover:text-blue-700"
						>
							View Details →
						</button>
					</div>
				{/if}
			</div>
		{/if}
	</div>
