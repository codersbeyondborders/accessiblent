<script lang="ts">
	// StatsOverview component - Display summary statistics
	// Requirements: 10.2
	
	interface Props {
		totalDomains: number;
		verifiedDomains: number;
		totalWebsites: number;
		remediatedWebsites: number;
		totalIssuesFixed: number;
	}
	
	let { 
		totalDomains, 
		verifiedDomains, 
		totalWebsites, 
		remediatedWebsites, 
		totalIssuesFixed 
	}: Props = $props();
</script>

<div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
	<!-- Total Domains -->
	<div class="bg-white overflow-hidden shadow rounded-lg">
		<div class="p-5">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
					</svg>
				</div>
				<div class="ml-5 w-0 flex-1">
					<dl>
						<dt class="text-sm font-medium text-gray-500 truncate">
							Total Domains
						</dt>
						<dd class="flex items-baseline">
							<div class="text-2xl font-semibold text-gray-900">
								{totalDomains}
							</div>
							<div class="ml-2 text-sm text-gray-600">
								({verifiedDomains} verified)
							</div>
						</dd>
					</dl>
				</div>
			</div>
		</div>
	</div>

	<!-- Total Websites -->
	<div class="bg-white overflow-hidden shadow rounded-lg">
		<div class="p-5">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
				</div>
				<div class="ml-5 w-0 flex-1">
					<dl>
						<dt class="text-sm font-medium text-gray-500 truncate">
							Total Websites
						</dt>
						<dd class="flex items-baseline">
							<div class="text-2xl font-semibold text-gray-900">
								{totalWebsites}
							</div>
							<div class="ml-2 text-sm text-gray-600">
								({remediatedWebsites} remediated)
							</div>
						</dd>
					</dl>
				</div>
			</div>
		</div>
	</div>

	<!-- Total Issues Fixed -->
	<div class="bg-white overflow-hidden shadow rounded-lg">
		<div class="p-5">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<div class="ml-5 w-0 flex-1">
					<dl>
						<dt class="text-sm font-medium text-gray-500 truncate">
							Issues Fixed
						</dt>
						<dd>
							<div class="text-2xl font-semibold text-gray-900">
								{totalIssuesFixed}
							</div>
						</dd>
					</dl>
				</div>
			</div>
		</div>
	</div>
</div>
