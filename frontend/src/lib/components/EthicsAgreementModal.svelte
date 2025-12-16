<script lang="ts">
	// Ethics Agreement Modal Component
	// Requirements: 3.1, 3.4
	// Modal that blocks actions requiring acceptance
	
	import { goto } from '$app/navigation';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	interface EthicsAgreement {
		version: string;
		content: string;
		effective_date: string;
	}
	
	interface Props {
		isOpen: boolean;
		onClose?: () => void;
		onAccept?: () => void;
		redirectAfterAccept?: string;
	}
	
	let { 
		isOpen = $bindable(false),
		onClose,
		onAccept,
		redirectAfterAccept = '/dashboard'
	}: Props = $props();
	
	// State
	let agreement = $state<EthicsAgreement | null>(null);
	let loading = $state(true);
	let accepting = $state(false);
	let error = $state('');
	let acceptanceChecked = $state(false);
	
	// Load agreement when modal opens
	$effect(() => {
		if (isOpen && !agreement) {
			loadAgreement();
		}
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
		
		try {
			const response = await fetch(`${API}/api/ethics/accept`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({
					agreement_version: agreement.version,
					ip_address: null
				})
			});
			
			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.error?.message || 'Failed to accept agreement');
			}
			
			// Call onAccept callback if provided
			if (onAccept) {
				onAccept();
			}
			
			// Close modal
			isOpen = false;
			
			// Redirect if specified
			if (redirectAfterAccept) {
				goto(redirectAfterAccept);
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to accept agreement';
			console.error('Accept error:', err);
		} finally {
			accepting = false;
		}
	}
	
	function handleDecline() {
		acceptanceChecked = false;
		if (onClose) {
			onClose();
		} else {
			isOpen = false;
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
	
	// Prevent body scroll when modal is open
	$effect(() => {
		if (isOpen) {
			document.body.style.overflow = 'hidden';
		} else {
			document.body.style.overflow = '';
		}
		
		return () => {
			document.body.style.overflow = '';
		};
	});
</script>

{#if isOpen}
	<!-- Modal Overlay -->
	<div 
		class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity z-40"
		onclick={handleDecline}
		role="presentation"
	></div>

	<!-- Modal Dialog -->
	<div class="fixed inset-0 z-50 overflow-y-auto">
		<div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
			<div 
				class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-3xl"
				role="dialog"
				aria-modal="true"
				aria-labelledby="modal-title"
			>
				{#if loading}
					<div class="px-6 py-12">
						<div class="flex items-center justify-center">
							<div class="flex items-center gap-3">
								<div class="animate-spin h-8 w-8 rounded-full border-4 border-blue-600 border-t-transparent"></div>
								<span class="text-gray-600">Loading agreement...</span>
							</div>
						</div>
					</div>
				{:else if error && !agreement}
					<div class="px-6 py-6">
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
						<div class="mt-4 flex justify-end">
							<button
								onclick={handleDecline}
								class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
							>
								Close
							</button>
						</div>
					</div>
				{:else if agreement}
					<!-- Modal Header -->
					<div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
						<div class="flex items-center justify-between">
							<div>
								<h3 class="text-lg font-semibold text-gray-900" id="modal-title">
									Ethics Agreement Required
								</h3>
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

					<!-- Modal Body -->
					<div class="px-6 py-4 max-h-96 overflow-y-auto">
						<div class="mb-4 rounded-lg bg-blue-50 border border-blue-200 p-3">
							<div class="flex">
								<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
								</svg>
								<div class="ml-3">
									<p class="text-sm text-blue-700">
										You must accept the ethics agreement before you can continue with this action.
									</p>
								</div>
							</div>
						</div>

						<div class="prose prose-sm max-w-none">
							<div class="whitespace-pre-wrap text-gray-700 leading-relaxed text-sm">
								{agreement.content}
							</div>
						</div>
					</div>

					<!-- Modal Footer -->
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
									id="modal-acceptance-checkbox"
									type="checkbox"
									bind:checked={acceptanceChecked}
									class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
									disabled={accepting}
								/>
							</div>
							<div class="ml-3">
								<label for="modal-acceptance-checkbox" class="text-sm text-gray-700">
									I have read and agree to the terms of this ethics agreement
								</label>
							</div>
						</div>

						<!-- Action Buttons -->
						<div class="flex items-center justify-end gap-3">
							<button
								onclick={handleDecline}
								disabled={accepting}
								class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Decline
							</button>
							<button
								onclick={handleAccept}
								disabled={!acceptanceChecked || accepting}
								class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600"
							>
								{#if accepting}
									<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
										<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
										<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
									</svg>
									Accepting...
								{:else}
									Accept & Continue
								{/if}
							</button>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
