<script lang="ts">
	// Add Domain page - Form to add a new domain for verification
	// Requirements: 2.1
	
	import { goto } from '$app/navigation';
	import { toastStore } from '$lib/stores/toast';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	// Form state
	let domainName = '';
	
	// UI state
	let loading = false;
	let error = '';
	let fieldErrors: Record<string, string> = {};
	
	// Validate domain format
	function validateDomain(): boolean {
		fieldErrors = {};
		
		if (!domainName) {
			fieldErrors.domainName = 'Domain name is required';
			return false;
		}
		
		// Remove protocol if present
		let cleanDomain = domainName.trim().toLowerCase();
		cleanDomain = cleanDomain.replace(/^https?:\/\//, '');
		cleanDomain = cleanDomain.replace(/^www\./, '');
		cleanDomain = cleanDomain.replace(/\/.*$/, ''); // Remove path
		
		// Basic domain validation
		const domainRegex = /^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,}$/;
		if (!domainRegex.test(cleanDomain)) {
			fieldErrors.domainName = 'Please enter a valid domain name (e.g., example.org)';
			return false;
		}
		
		// Update the domain name to the cleaned version
		domainName = cleanDomain;
		
		return true;
	}
	
	// Handle form submission
	async function handleSubmit() {
		error = '';
		
		if (!validateDomain()) {
			return;
		}
		
		loading = true;
		
		try {
			const response = await fetch(`${API}/api/domains`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({
					domain_name: domainName
				})
			});
			
			if (response.ok) {
				const data = await response.json();
				toastStore.success('Domain added successfully');
				// Redirect to verification instructions page
				goto(`/domains/${data.domain?.id || data.id}/verify`);
			} else {
				const errorData = await response.json().catch(() => ({ detail: 'Failed to add domain' }));
				
				// Handle field-specific errors
				if (errorData.error?.details?.field) {
					fieldErrors[errorData.error.details.field] = errorData.error.message || errorData.detail;
				} else {
					error = errorData.detail || errorData.error?.message || 'Failed to add domain. Please try again.';
				}
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Network error. Please try again.';
			toastStore.error('Failed to add domain');
		} finally {
			loading = false;
		}
	}
	
	// Handle Enter key in form
	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !loading) {
			e.preventDefault();
			handleSubmit();
		}
	}
</script>

<svelte:head>
	<title>Add Domain - Accessify</title>
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
			<h1 class="text-3xl font-bold text-gray-900">Add Domain</h1>
			<p class="mt-2 text-sm text-gray-600">
				Add a domain to verify ownership and enable website remediation
			</p>
		</div>

		<!-- Main Content -->
		<div class="bg-white shadow rounded-lg p-8">
			<form class="space-y-6" on:submit|preventDefault={handleSubmit}>
				{#if error}
					<div class="rounded-lg bg-red-50 border border-red-200 p-4" role="alert">
						<div class="flex">
							<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
							</svg>
							<p class="ml-3 text-sm text-red-700">{error}</p>
						</div>
					</div>
				{/if}

				<!-- Domain name field -->
				<div>
					<label for="domainName" class="block text-sm font-medium text-gray-700">
						Domain Name
					</label>
					<div class="mt-1">
						<input
							id="domainName"
							name="domainName"
							type="text"
							placeholder="example.org"
							required
							bind:value={domainName}
							on:keydown={handleKeydown}
							class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
							class:border-red-500={fieldErrors.domainName}
							aria-invalid={!!fieldErrors.domainName}
							aria-describedby={fieldErrors.domainName ? 'domainName-error' : 'domainName-help'}
						/>
					</div>
					{#if fieldErrors.domainName}
						<p id="domainName-error" class="mt-1 text-sm text-red-600">{fieldErrors.domainName}</p>
					{:else}
						<p id="domainName-help" class="mt-1 text-xs text-gray-500">
							Enter your domain without protocol (e.g., example.org, not https://example.org)
						</p>
					{/if}
				</div>

				<!-- Info box -->
				<div class="rounded-lg bg-blue-50 border border-blue-200 p-4">
					<div class="flex">
						<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h3 class="text-sm font-medium text-blue-800">
								What happens next?
							</h3>
							<div class="mt-2 text-sm text-blue-700">
								<p>
									After adding your domain, you'll receive verification instructions. You'll need to add a meta tag to your website or create a verification file to prove ownership.
								</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Submit button -->
				<div class="flex items-center justify-end gap-3">
					<a
						href="/dashboard"
						class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
					>
						Cancel
					</a>
					<button
						type="submit"
						disabled={loading}
						class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{#if loading}
							<span class="flex items-center gap-2">
								<span class="animate-spin h-4 w-4 rounded-full border-2 border-white border-t-transparent"></span>
								Adding domain...
							</span>
						{:else}
							Add Domain
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
</div>
