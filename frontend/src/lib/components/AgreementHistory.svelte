<script lang="ts">
	// Agreement History Component
	// Requirements: 3.3
	// Display past acceptances with versions and dates
	
	import { onMount } from 'svelte';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	interface AcceptanceRecord {
		id: number;
		agreement_version: string;
		accepted_at: string;
		ip_address?: string;
	}
	
	interface AcceptanceStatus {
		has_agreement: boolean;
		current_version?: string;
		effective_date?: string;
		has_accepted: boolean;
		needs_acceptance: boolean;
	}
	
	// State
	let status = $state<AcceptanceStatus | null>(null);
	let history = $state<AcceptanceRecord[]>([]);
	let loading = $state(true);
	let error = $state('');
	
	onMount(async () => {
		await loadAcceptanceData();
	});
	
	async function loadAcceptanceData() {
		loading = true;
		error = '';
		
		try {
			const response = await fetch(`${API}/api/ethics/status`, {
				credentials: 'include'
			});
			
			if (!response.ok) {
				throw new Error('Failed to load acceptance history');
			}
			
			const data = await response.json();
			status = data.status;
			history = data.history || [];
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load history';
			console.error('History load error:', err);
		} finally {
			loading = false;
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
	
	function formatDateTime(dateString: string): string {
		try {
			const date = new Date(dateString);
			return date.toLocaleString('en-US', {
				year: 'numeric',
				month: 'long',
				day: 'numeric',
				hour: '2-digit',
				minute: '2-digit'
			});
		} catch {
			return dateString;
		}
	}
</script>

<div class="bg-white shadow rounded-lg overflow-hidden">
	<!-- Header -->
	<div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
		<h3 class="text-lg font-semibold text-gray-900">
			Ethics Agreement History
		</h3>
		<p class="mt-1 text-sm text-gray-600">
			Your acceptance history and current status
		</p>
	</div>

	<!-- Content -->
	<div class="px-6 py-6">
		{#if loading}
			<div class="flex items-center justify-center py-8">
				<div class="flex items-center gap-3">
					<div class="animate-spin h-6 w-6 rounded-full border-4 border-blue-600 border-t-transparent"></div>
					<span class="text-gray-600">Loading history...</span>
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
							onclick={loadAcceptanceData}
							class="mt-2 text-sm font-medium text-red-700 hover:text-red-600 underline"
						>
							Try again
						</button>
					</div>
				</div>
			</div>
		{:else}
			<!-- Current Status -->
			{#if status}
				<div class="mb-6">
					<h4 class="text-sm font-medium text-gray-900 mb-3">Current Status</h4>
					
					{#if !status.has_agreement}
						<div class="rounded-lg bg-gray-50 border border-gray-200 p-4">
							<div class="flex">
								<svg class="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
								</svg>
								<div class="ml-3">
									<p class="text-sm text-gray-700">No ethics agreement is currently configured.</p>
								</div>
							</div>
						</div>
					{:else if status.has_accepted}
						<div class="rounded-lg bg-green-50 border border-green-200 p-4">
							<div class="flex">
								<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
								</svg>
								<div class="ml-3">
									<p class="text-sm font-medium text-green-800">
										You have accepted the current ethics agreement
									</p>
									<p class="mt-1 text-sm text-green-700">
										Version {status.current_version}
										{#if status.effective_date}
											<span class="text-green-600">•</span>
											<span>Effective {formatDate(status.effective_date)}</span>
										{/if}
									</p>
								</div>
							</div>
						</div>
					{:else}
						<div class="rounded-lg bg-yellow-50 border border-yellow-200 p-4">
							<div class="flex">
								<svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
								</svg>
								<div class="ml-3">
									<p class="text-sm font-medium text-yellow-800">
										Action required: You need to accept the current ethics agreement
									</p>
									<p class="mt-1 text-sm text-yellow-700">
										Version {status.current_version}
										{#if status.effective_date}
											<span class="text-yellow-600">•</span>
											<span>Effective {formatDate(status.effective_date)}</span>
										{/if}
									</p>
									<div class="mt-3">
										<a
											href="/ethics"
											class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-yellow-700 bg-yellow-100 hover:bg-yellow-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
										>
											Review & Accept Agreement
											<svg class="ml-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
											</svg>
										</a>
									</div>
								</div>
							</div>
						</div>
					{/if}
				</div>
			{/if}

			<!-- Acceptance History -->
			<div>
				<h4 class="text-sm font-medium text-gray-900 mb-3">Acceptance History</h4>
				
				{#if history.length === 0}
					<div class="text-center py-8">
						<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						<p class="mt-2 text-sm text-gray-600">No acceptance history yet</p>
					</div>
				{:else}
					<div class="space-y-3">
						{#each history as record (record.id)}
							<div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
								<div class="flex items-start justify-between">
									<div class="flex-1">
										<div class="flex items-center gap-2">
											<svg class="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
												<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
											</svg>
											<span class="text-sm font-medium text-gray-900">
												Version {record.agreement_version}
											</span>
											{#if status?.current_version === record.agreement_version}
												<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
													Current
												</span>
											{/if}
										</div>
										<p class="mt-1 text-sm text-gray-600">
											Accepted on {formatDateTime(record.accepted_at)}
										</p>
										{#if record.ip_address}
											<p class="mt-0.5 text-xs text-gray-500">
												IP: {record.ip_address}
											</p>
										{/if}
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>
