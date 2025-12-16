<script lang="ts">
	// Website registration page
	// Requirements: 4.1, 4.2, 4.3
	
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { toastStore } from '$lib/stores/toast';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	interface Domain {
		id: number;
		domain_name: string;
		is_verified: boolean | number;
	}
	
	// State
	let domains: Domain[] = [];
	let selectedDomainId: number | null = null;
	let entryUrl = '';
	let websiteName = '';
	let loading = true;
	let submitting = false;
	let error = '';
	let fieldErrors: Record<string, string> = {};
	
	// Computed
	$: selectedDomain = domains.find(d => d.id === selectedDomainId);
	
	onMount(async () => {
		await loadVerifiedDomains();
	});
	
	async function loadVerifiedDomains() {
		loading = true;
		error = '';
		
		try {
			console.log('Fetching domains from:', `${API}/api/domains`);
			const response = await fetch(`${API}/api/domains`, {
				credentials: 'include'
			});
			
			console.log('Domains response status:', response.status);
			
			if (!response.ok) {
				throw new Error('Failed to load domains');
			}
			
			const data = await response.json();
			console.log('Domains data:', data);
			
			// Filter to only verified domains (handle both boolean and number)
			domains = (data.domains || data).filter((d: Domain) => d.is_verified === true || d.is_verified === 1);
			console.log('Verified domains:', domains);
			
			// Auto-select if only one domain
			if (domains.length === 1) {
				selectedDomainId = domains[0].id;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load domains';
			console.error('Domain load error:', err);
			toastStore.error('Failed to load domains');
		} finally {
			loading = false;
			console.log('Loading complete. Domains count:', domains.length);
		}
	}
	
	function validateForm(): boolean {
		fieldErrors = {};
		let isValid = true;
		
		// Validate domain selection
		if (!selectedDomainId) {
			fieldErrors.domain = 'Please select a domain';
			isValid = false;
		}
		
		// Validate entry URL
		if (!entryUrl.trim()) {
			fieldErrors.entryUrl = 'Entry URL is required';
			isValid = false;
		} else {
			// Validate URL format
			try {
				const url = new URL(entryUrl);
				
				// Validate URL matches selected domain
				if (selectedDomain) {
					const urlDomain = url.hostname;
					const selectedDomainName = selectedDomain.domain_name;
					
					// Check if URL domain matches or is subdomain of selected domain
					if (urlDomain !== selectedDomainName && !urlDomain.endsWith('.' + selectedDomainName)) {
						fieldErrors.entryUrl = `URL must be from domain ${selectedDomainName}`;
						isValid = false;
					}
				}
			} catch (err) {
				fieldErrors.entryUrl = 'Please enter a valid URL (including http:// or https://)';
				isValid = false;
			}
		}
		
		return isValid;
	}
	
	async function handleSubmit(e: Event) {
		e.preventDefault();
		
		if (!validateForm()) {
			return;
		}
		
		submitting = true;
		error = '';
		
		try {
			const response = await fetch(`${API}/api/websites`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				credentials: 'include',
				body: JSON.stringify({
					domain_id: selectedDomainId,
					entry_url: entryUrl,
					name: websiteName || null,
				}),
			});
			
			if (!response.ok) {
				const data = await response.json();
				
				// Handle specific error codes
				if (data.detail?.code === 'DOMAIN_NOT_VERIFIED') {
					error = 'The selected domain is not verified.';
				} else if (data.detail?.code === 'INVALID_URL_DOMAIN') {
					fieldErrors.entryUrl = 'URL domain does not match the selected domain';
				} else {
					error = data.detail?.message || data.detail || 'Failed to register webpage';
				}
				return;
			}
			
			const data = await response.json();
			toastStore.success('Webpage registered successfully');
			
			// Redirect to website detail page
			goto(`/websites/${data.website?.id || data.id}`);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to register webpage';
			console.error('Registration error:', err);
			toastStore.error('Failed to register webpage');
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Register Webpage - Accessify</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 py-8">
	<div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
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
			<h1 class="text-3xl font-bold text-gray-900">Register Webpage</h1>
			<p class="mt-2 text-sm text-gray-600">
				Register a webpage from your verified domain for accessibility remediation.
			</p>
		</div>

		{#if loading}
			<div class="bg-white shadow rounded-lg p-8">
				<div class="flex items-center justify-center">
					<div class="flex items-center gap-3">
						<div class="animate-spin h-8 w-8 rounded-full border-4 border-blue-600 border-t-transparent"></div>
						<span class="text-gray-600">Loading...</span>
					</div>
				</div>
			</div>
		{:else if domains.length === 0}
			<!-- No Verified Domains -->
			<div class="bg-white shadow rounded-lg p-8">
				<div class="text-center">
					<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9 3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
					</svg>
					<h3 class="mt-4 text-lg font-medium text-gray-900">No Verified Domains</h3>
					<p class="mt-2 text-sm text-gray-600">
						You need to add and verify a domain before registering a website.
					</p>
					<div class="mt-6">
						<a
							href="/domains/add"
							class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
						>
							<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							Add Domain
						</a>
					</div>
				</div>
			</div>
		{:else}
			<!-- Registration Form -->
			<div class="bg-white shadow rounded-lg p-8">
				{#if error}
					<div class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4" role="alert">
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

				<form on:submit={handleSubmit} class="space-y-6">
					<!-- Domain Selection -->
					<div>
						<label for="domain" class="block text-sm font-medium text-gray-700">
							Domain <span class="text-red-500">*</span>
						</label>
						<select
							id="domain"
							bind:value={selectedDomainId}
							class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
							class:border-red-300={fieldErrors.domain}
							class:text-red-900={fieldErrors.domain}
							required
						>
							<option value={null}>Select a verified domain</option>
							{#each domains as domain (domain.id)}
								<option value={domain.id}>{domain.domain_name}</option>
							{/each}
						</select>
						{#if fieldErrors.domain}
							<p class="mt-2 text-sm text-red-600">{fieldErrors.domain}</p>
						{/if}
						<p class="mt-2 text-sm text-gray-500">
							Select the verified domain that owns the website you want to register.
						</p>
					</div>

					<!-- Entry URL -->
					<div>
						<label for="entryUrl" class="block text-sm font-medium text-gray-700">
							Entry URL <span class="text-red-500">*</span>
						</label>
						<input
							type="url"
							id="entryUrl"
							bind:value={entryUrl}
							placeholder="https://example.org"
							class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
							class:border-red-300={fieldErrors.entryUrl}
							class:text-red-900={fieldErrors.entryUrl}
							required
						/>
						{#if fieldErrors.entryUrl}
							<p class="mt-2 text-sm text-red-600">{fieldErrors.entryUrl}</p>
						{/if}
						<p class="mt-2 text-sm text-gray-500">
							The starting page URL for remediation. Must be from the selected domain.
						</p>
					</div>

					<!-- Website Name (Optional) -->
					<div>
						<label for="websiteName" class="block text-sm font-medium text-gray-700">
							Website Name <span class="text-gray-400">(optional)</span>
						</label>
						<input
							type="text"
							id="websiteName"
							bind:value={websiteName}
							placeholder="My Organization Website"
							class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
						/>
						<p class="mt-2 text-sm text-gray-500">
							A friendly name to help you identify this website.
						</p>
					</div>

					<!-- Submit Button -->
					<div class="flex items-center justify-end gap-3 pt-4">
						<a
							href="/dashboard"
							class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
						>
							Cancel
						</a>
						<button
							type="submit"
							disabled={submitting}
							class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							{#if submitting}
								<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Registering...
							{:else}
								Register Webpage
							{/if}
						</button>
					</div>
				</form>
			</div>
		{/if}
	</div>
</div>
