<script lang="ts">
	// WebsiteCard component - Display website information with remediation status
	// Requirements: 10.2, 10.4
	
	interface Website {
		id: number;
		entry_url: string;
		name?: string;
		domain_name?: string;
		status: string;
		last_remediation_at?: string;
		created_at?: string;
		issues_fixed?: number;
	}
	
	interface Props {
		website: Website;
	}
	
	let { website }: Props = $props();
	
	// Format date for display
	function formatDate(dateString?: string): string {
		if (!dateString) return '';
		const date = new Date(dateString);
		return date.toLocaleDateString('en-US', { 
			year: 'numeric', 
			month: 'short', 
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
	
	// Get status badge color
	function getStatusColor(status: string): string {
		switch (status.toLowerCase()) {
			case 'remediated':
			case 'complete':
				return 'bg-green-100 text-green-800';
			case 'processing':
			case 'in_progress':
				return 'bg-blue-100 text-blue-800';
			case 'failed':
			case 'error':
				return 'bg-red-100 text-red-800';
			default:
				return 'bg-gray-100 text-gray-800';
		}
	}
	
	// Format status text
	function formatStatus(status: string): string {
		return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
	}
</script>

<div class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
	<div class="p-5">
		<div class="flex items-start justify-between">
			<div class="flex-1 min-w-0">
				<div class="flex items-center gap-2">
					<svg class="h-5 w-5 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					<h3 class="text-lg font-medium text-gray-900 truncate">
						{website.name || 'Unnamed Website'}
					</h3>
				</div>
				
				<p class="mt-1 text-sm text-gray-500 truncate" title={website.entry_url}>
					{website.entry_url}
				</p>
				
				{#if website.domain_name}
					<p class="mt-1 text-xs text-gray-400">
						Domain: {website.domain_name}
					</p>
				{/if}
				
				<div class="mt-3 flex items-center gap-3">
					<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(website.status)}">
						{formatStatus(website.status)}
					</span>
					
					{#if website.issues_fixed !== undefined && website.issues_fixed > 0}
						<span class="text-xs text-gray-600">
							<span class="font-semibold text-green-600">{website.issues_fixed}</span> issues fixed
						</span>
					{/if}
				</div>
				
				{#if website.last_remediation_at}
					<p class="mt-2 text-xs text-gray-500">
						Last updated: {formatDate(website.last_remediation_at)}
					</p>
				{:else if website.created_at}
					<p class="mt-2 text-xs text-gray-500">
						Created: {formatDate(website.created_at)}
					</p>
				{/if}
			</div>
			
			<div class="ml-4 flex-shrink-0">
				<a 
					href="/websites/{website.id}"
					class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
				>
					View Details
				</a>
			</div>
		</div>
	</div>
</div>
