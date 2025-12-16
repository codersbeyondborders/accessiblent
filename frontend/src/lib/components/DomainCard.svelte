<script lang="ts">
	// DomainCard component - Display domain information with verification status
	// Requirements: 10.1, 10.3
	
	interface Domain {
		id: number;
		domain_name: string;
		is_verified: boolean;
		verification_method?: string;
		verified_at?: string;
		created_at?: string;
	}
	
	interface Props {
		domain: Domain;
	}
	
	let { domain }: Props = $props();
	
	// Format date for display
	function formatDate(dateString?: string): string {
		if (!dateString) return '';
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { 
			year: 'numeric', 
			month: 'short', 
			day: 'numeric' 
		});
	}
</script>

<div class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
	<div class="p-5">
		<div class="flex items-center justify-between">
			<div class="flex-1 min-w-0">
				<div class="flex items-center gap-2">
					<svg class="h-5 w-5 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
					</svg>
					<h3 class="text-lg font-medium text-gray-900 truncate">
						{domain.domain_name}
					</h3>
				</div>
				
				<div class="mt-2 flex items-center gap-4">
					{#if domain.is_verified}
						<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
							<svg class="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
							</svg>
							Verified
						</span>
					{:else}
						<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
							<svg class="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
							</svg>
							Not Verified
						</span>
					{/if}
					
					{#if domain.is_verified && domain.verification_method}
						<span class="text-xs text-gray-500">
							via {domain.verification_method}
						</span>
					{/if}
				</div>
				
				{#if domain.is_verified && domain.verified_at}
					<p class="mt-1 text-sm text-gray-500">
						Verified on {formatDate(domain.verified_at)}
					</p>
				{/if}
			</div>
			
			<div class="ml-4 flex-shrink-0">
				{#if domain.is_verified}
					<a 
						href="/domains/{domain.id}"
						class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
					>
						View Details
					</a>
				{:else}
					<a 
						href="/domains/{domain.id}/verify"
						class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
					>
						Verify Now
					</a>
				{/if}
			</div>
		</div>
	</div>
</div>
