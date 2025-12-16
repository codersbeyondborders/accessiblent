<script lang="ts">
	// Domain Verification page - Display verification instructions and trigger verification
	// Requirements: 2.2, 2.3, 2.4, 2.5
	
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import Header from '$lib/components/Header.svelte';
	import VerificationInstructions from '$lib/components/VerificationInstructions.svelte';
	import VerificationStatus from '$lib/components/VerificationStatus.svelte';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	interface Domain {
		id: number;
		domain_name: string;
		verification_token: string;
		is_verified: boolean;
		verification_method?: string;
		verified_at?: string;
		created_at?: string;
	}
	
	interface VerificationInstructionsData {
		meta_tag: {
			method: string;
			description: string;
			code: string;
			location: string;
		};
		wellknown: {
			method: string;
			description: string;
			code: string;
			location: string;
		};
	}
	
	// Get domain ID from page data
	interface Props {
		data: {
			domainId: string;
		};
	}
	
	let { data }: Props = $props();
	let domainId = $derived(data.domainId);
	
	// State
	let domain = $state<Domain | null>(null);
	let instructions = $state<VerificationInstructionsData | null>(null);
	let loading = $state(true);
	let verifying = $state(false);
	let error = $state('');
	let verificationStatus = $state<'pending' | 'verifying' | 'verified' | 'failed'>('pending');
	let verificationError = $state('');
	let troubleshooting = $state<any>(null);
	
	onMount(async () => {
		// Check authentication
		const isAuth = await authStore.checkAuth();
		if (!isAuth) {
			goto('/login');
			return;
		}
		
		// Load domain details
		await loadDomainDetails();
	});
	
	async function loadDomainDetails() {
		loading = true;
		error = '';
		
		try {
			const response = await fetch(`${API}/api/domains/${domainId}`, {
				credentials: 'include'
			});
			
			if (!response.ok) {
				if (response.status === 404) {
					error = 'Domain not found';
				} else {
					error = 'Failed to load domain details';
				}
				return;
			}
			
			const data = await response.json();
			domain = data.domain;
			instructions = data.verification_instructions;
			
			// Set initial verification status
			if (domain?.is_verified) {
				verificationStatus = 'verified';
			} else {
				verificationStatus = 'pending';
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load domain details';
			console.error('Domain load error:', err);
		} finally {
			loading = false;
		}
	}
	
	async function handleVerify() {
		if (!domain) return;
		
		verifying = true;
		verificationStatus = 'verifying';
		verificationError = '';
		troubleshooting = null;
		
		try {
			const response = await fetch(`${API}/api/domains/${domainId}/verify`, {
				method: 'POST',
				credentials: 'include'
			});
			
			const data = await response.json();
			
			if (response.ok && data.verified) {
				// Verification successful
				verificationStatus = 'verified';
				domain = {
					...domain,
					is_verified: true,
					verification_method: data.method,
					verified_at: data.verified_at
				};
			} else {
				// Verification failed
				verificationStatus = 'failed';
				verificationError = data.message || 'Verification failed';
				troubleshooting = data.troubleshooting || null;
			}
		} catch (err) {
			verificationStatus = 'failed';
			verificationError = err instanceof Error ? err.message : 'Network error during verification';
		} finally {
			verifying = false;
		}
	}
	
	function handleBackToDashboard() {
		goto('/dashboard');
	}
</script>

<svelte:head>
	<title>Verify Domain - Accessify</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<Header showAuth={false} />
	
	<!-- Page Header -->
	<div class="bg-white shadow">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-2xl font-bold text-gray-900">Verify Domain</h1>
					{#if domain}
						<p class="mt-1 text-sm text-gray-600">
							{domain.domain_name}
						</p>
					{/if}
				</div>
				<button
					onclick={handleBackToDashboard}
					class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
				>
					<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
					</svg>
					Back to Dashboard
				</button>
			</div>
		</div>
	</div>

	<!-- Main Content -->
	<main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="flex items-center gap-3">
					<div class="animate-spin h-8 w-8 rounded-full border-4 border-blue-600 border-t-transparent"></div>
					<span class="text-gray-600">Loading domain details...</span>
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
						<button
							onclick={handleBackToDashboard}
							class="mt-2 text-sm font-medium text-red-700 hover:text-red-600 underline"
						>
							Go to Dashboard
						</button>
					</div>
				</div>
			</div>
		{:else if domain && instructions}
			<div class="space-y-6">
				<!-- Verification Token Display -->
				<div class="bg-white rounded-lg border border-gray-200 p-6">
					<h2 class="text-lg font-medium text-gray-900 mb-2">Your Verification Token</h2>
					<p class="text-sm text-gray-600 mb-4">
						Use this token to verify ownership of your domain. Choose one of the verification methods below.
					</p>
					<div class="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm break-all">
						{domain.verification_token}
					</div>
				</div>

				<!-- Verification Instructions -->
				<VerificationInstructions 
					metaTag={instructions.meta_tag}
					wellknown={instructions.wellknown}
				/>

				<!-- Verification Status -->
				<VerificationStatus 
					status={verificationStatus}
					verifiedAt={domain.verified_at}
					verificationMethod={domain.verification_method}
					errorMessage={verificationError}
					{troubleshooting}
				/>

				<!-- Verify Button -->
				{#if !domain.is_verified}
					<div class="flex items-center justify-between bg-white rounded-lg border border-gray-200 p-6">
						<div>
							<h3 class="text-sm font-medium text-gray-900">Ready to verify?</h3>
							<p class="mt-1 text-sm text-gray-600">
								Once you've added the verification code to your website, click the button to verify.
							</p>
						</div>
						<button
							onclick={handleVerify}
							disabled={verifying}
							class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							{#if verifying}
								<span class="flex items-center gap-2">
									<span class="animate-spin h-5 w-5 rounded-full border-2 border-white border-t-transparent"></span>
									Verifying...
								</span>
							{:else}
								<svg class="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								Verify Now
							{/if}
						</button>
					</div>
				{:else}
					<!-- Domain is verified - show next steps -->
					<div class="bg-white rounded-lg border border-gray-200 p-6">
						<h3 class="text-lg font-medium text-gray-900 mb-4">Next Steps</h3>
						<p class="text-sm text-gray-600 mb-4">
							Your domain is now verified! You can register websites under this domain for accessibility remediation.
						</p>
						<div class="flex items-center gap-3">
							<a
								href="/websites/register"
								class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
							>
								<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
								</svg>
								Register a Website
							</a>
							<a
								href="/dashboard"
								class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
							>
								Go to Dashboard
							</a>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</main>
</div>
