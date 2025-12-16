<script lang="ts">
	// RemediationProgress component
	// Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
	
	interface RemediationStatus {
		website_id: number;
		status: string;
		last_remediation_at?: string;
		page?: {
			page_id: number;
			page_status: string;
			created_at?: string;
		};
		issues_found?: number;
	}
	
	interface Props {
		status: RemediationStatus | null;
	}
	
	let { status }: Props = $props();
	
	// Determine current stage based on status
	let currentStage = $derived(() => {
		if (!status) return 'fetching';
		
		const pageStatus = status.page?.page_status;
		
		if (status.status === 'error') return 'error';
		if (status.status === 'remediated') return 'complete';
		
		if (!pageStatus || pageStatus === 'NEW') return 'fetching';
		if (pageStatus === 'AUDITED') return 'auditing';
		if (pageStatus === 'FIXED') return 'fixing';
		
		return 'fetching';
	});
	
	// Stage definitions
	const stages = [
		{
			id: 'fetching',
			label: 'Fetching HTML',
			description: 'Downloading the webpage content',
		},
		{
			id: 'auditing',
			label: 'Running Audit',
			description: 'Analyzing accessibility issues',
		},
		{
			id: 'fixing',
			label: 'Applying Fixes',
			description: 'Generating remediated HTML',
		},
		{
			id: 'complete',
			label: 'Complete',
			description: 'Remediation finished successfully',
		},
	];
	
	// Calculate progress percentage
	let progressPercentage = $derived(() => {
		const stage = currentStage();
		if (stage === 'error') return 0;
		
		const stageIndex = stages.findIndex(s => s.id === stage);
		if (stageIndex === -1) return 0;
		
		return ((stageIndex + 1) / stages.length) * 100;
	});
	
	// Check if stage is complete
	function isStageComplete(stageId: string): boolean {
		const stage = currentStage();
		if (stage === 'error') return false;
		
		const currentIndex = stages.findIndex(s => s.id === stage);
		const stageIndex = stages.findIndex(s => s.id === stageId);
		
		return stageIndex < currentIndex || stage === 'complete';
	}
	
	// Check if stage is current
	function isStageCurrent(stageId: string): boolean {
		return currentStage() === stageId;
	}
</script>

<div class="bg-white shadow rounded-lg p-6">
	<h2 class="text-lg font-semibold text-gray-900 mb-4">Remediation Progress</h2>
	
	{#if currentStage() === 'error'}
		<!-- Error State -->
		<div class="rounded-lg bg-red-50 border border-red-200 p-4" role="alert">
			<div class="flex">
				<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
				</svg>
				<div class="ml-3">
					<h3 class="text-sm font-medium text-red-800">Remediation Failed</h3>
					<p class="mt-1 text-sm text-red-700">
						An error occurred during the remediation process. Please try again or contact support if the issue persists.
					</p>
				</div>
			</div>
		</div>
	{:else}
		<!-- Progress Bar -->
		<div class="mb-6">
			<div class="flex items-center justify-between mb-2">
				<span class="text-sm font-medium text-gray-700">
					{#if currentStage() === 'complete'}
						Remediation Complete
					{:else}
						Processing...
					{/if}
				</span>
				<span class="text-sm font-medium text-gray-700">
					{Math.round(progressPercentage())}%
				</span>
			</div>
			<div class="w-full bg-gray-200 rounded-full h-2.5">
				<div
					class="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out"
					style="width: {progressPercentage()}%"
				></div>
			</div>
		</div>

		<!-- Stage List -->
		<div class="space-y-4">
			{#each stages as stage, index (stage.id)}
				<div class="flex items-start">
					<!-- Stage Icon -->
					<div class="flex-shrink-0">
						{#if isStageComplete(stage.id)}
							<!-- Complete -->
							<div class="flex items-center justify-center w-8 h-8 rounded-full bg-green-100">
								<svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
								</svg>
							</div>
						{:else if isStageCurrent(stage.id)}
							<!-- Current -->
							<div class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100">
								<div class="w-4 h-4 rounded-full border-2 border-blue-600 border-t-transparent animate-spin"></div>
							</div>
						{:else}
							<!-- Pending -->
							<div class="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100">
								<div class="w-3 h-3 rounded-full bg-gray-400"></div>
							</div>
						{/if}
					</div>

					<!-- Stage Content -->
					<div class="ml-4 flex-1">
						<h3 class="text-sm font-medium text-gray-900">
							{stage.label}
						</h3>
						<p class="mt-1 text-sm text-gray-500">
							{stage.description}
						</p>
						
						{#if isStageCurrent(stage.id) && stage.id === 'auditing' && status?.issues_found}
							<p class="mt-1 text-sm text-blue-600">
								Found {status.issues_found} accessibility {status.issues_found === 1 ? 'issue' : 'issues'}
							</p>
						{/if}
					</div>

					<!-- Connector Line -->
					{#if index < stages.length - 1}
						<div class="absolute left-4 top-8 w-0.5 h-12 -ml-px" 
						     class:bg-green-200={isStageComplete(stage.id)}
						     class:bg-gray-200={!isStageComplete(stage.id)}>
						</div>
					{/if}
				</div>
			{/each}
		</div>

		<!-- Status Message -->
		{#if currentStage() === 'complete'}
			<div class="mt-6 rounded-lg bg-green-50 border border-green-200 p-4">
				<div class="flex">
					<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
					</svg>
					<div class="ml-3">
						<h3 class="text-sm font-medium text-green-800">Success!</h3>
						<p class="mt-1 text-sm text-green-700">
							Your website has been successfully remediated. You can now preview the accessible version and embed it on your site.
						</p>
					</div>
				</div>
			</div>
		{:else}
			<div class="mt-6 rounded-lg bg-blue-50 border border-blue-200 p-4">
				<div class="flex">
					<svg class="h-5 w-5 text-blue-400 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
					</svg>
					<div class="ml-3">
						<p class="text-sm text-blue-700">
							Remediation is in progress. This may take a few moments depending on the size of your website.
						</p>
					</div>
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.absolute {
		position: absolute;
	}
</style>
