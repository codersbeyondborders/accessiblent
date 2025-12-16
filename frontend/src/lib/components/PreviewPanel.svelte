<script lang="ts">
	// PreviewPanel component
	// Requirements: 6.1, 6.3, 6.4
	
	import IframeSnippet from './IframeSnippet.svelte';
	
	interface IssueStats {
		total_issues: number;
		critical_issues: number;
		serious_issues: number;
	}
	
	interface Props {
		previewUrl: string;
		iframeSnippet: string;
		issueStats: IssueStats;
	}
	
	let { previewUrl, iframeSnippet, issueStats }: Props = $props();
	
	let copied = $state(false);
	let linkCopied = $state(false);
	let copyTimeout: ReturnType<typeof setTimeout> | null = null;
	let linkCopyTimeout: ReturnType<typeof setTimeout> | null = null;
	let activeTab = $state<'link' | 'embed'>('link');
	
	function copyToClipboard(text: string) {
		navigator.clipboard.writeText(text).then(() => {
			copied = true;
			
			// Clear existing timeout
			if (copyTimeout) {
				clearTimeout(copyTimeout);
			}
			
			// Reset after 2 seconds
			copyTimeout = setTimeout(() => {
				copied = false;
			}, 2000);
		}).catch(err => {
			console.error('Failed to copy:', err);
		});
	}
	
	function copyLinkHTML() {
		const linkHTML = `<a href="${previewUrl}" target="_blank" rel="noopener noreferrer">View Accessible Version</a>`;
		navigator.clipboard.writeText(linkHTML).then(() => {
			linkCopied = true;
			
			// Clear existing timeout
			if (linkCopyTimeout) {
				clearTimeout(linkCopyTimeout);
			}
			
			// Reset after 2 seconds
			linkCopyTimeout = setTimeout(() => {
				linkCopied = false;
			}, 2000);
		}).catch(err => {
			console.error('Failed to copy link HTML:', err);
		});
	}
	
	function handleOpenPreview() {
		window.open(previewUrl, '_blank', 'noopener,noreferrer');
	}
</script>

<div class="bg-white shadow rounded-lg p-6">
	<h2 class="text-lg font-semibold text-gray-900 mb-4">Remediated Content</h2>
	
	<!-- Issue Statistics -->
	<div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
		<div class="bg-gray-50 rounded-lg p-4">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<div class="ml-3">
					<p class="text-sm font-medium text-gray-500">Total Issues Fixed</p>
					<p class="text-2xl font-semibold text-gray-900">{issueStats.total_issues}</p>
				</div>
			</div>
		</div>
		
		<div class="bg-red-50 rounded-lg p-4">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
					</svg>
				</div>
				<div class="ml-3">
					<p class="text-sm font-medium text-red-700">Critical Issues</p>
					<p class="text-2xl font-semibold text-red-900">{issueStats.critical_issues}</p>
				</div>
			</div>
		</div>
		
		<div class="bg-yellow-50 rounded-lg p-4">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
					</svg>
				</div>
				<div class="ml-3">
					<p class="text-sm font-medium text-yellow-700">Serious Issues</p>
					<p class="text-2xl font-semibold text-yellow-900">{issueStats.serious_issues}</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Preview URL Section -->
	<div class="mb-6">
		<h3 class="text-sm font-medium text-gray-900 mb-2">Preview URL</h3>
		<p class="text-sm text-gray-600 mb-3">
			Use this URL to view the remediated version of your website.
		</p>
		<div class="flex items-center gap-2">
			<div class="flex-1 bg-gray-50 rounded-md px-3 py-2 border border-gray-300">
				<code class="text-sm text-gray-900 break-all">{previewUrl}</code>
			</div>
			<button
				onclick={() => copyToClipboard(previewUrl)}
				class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
				title="Copy to clipboard"
			>
				{#if copied}
					<svg class="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
				{:else}
					<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
					</svg>
				{/if}
			</button>
			<button
				onclick={handleOpenPreview}
				class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
			>
				<svg class="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
				</svg>
				Open Preview
			</button>
		</div>
	</div>

	<!-- Integration Options Tabs -->
	<div>
		<h3 class="text-sm font-medium text-gray-900 mb-3">Integration Options</h3>
		
		<!-- Tab Navigation -->
		<div class="border-b border-gray-200 mb-4">
			<nav class="-mb-px flex gap-6" aria-label="Integration tabs">
				<button
					onclick={() => activeTab = 'link'}
					class="py-2 px-1 border-b-2 font-medium text-sm transition-colors"
					class:border-blue-600={activeTab === 'link'}
					class:text-blue-600={activeTab === 'link'}
					class:border-transparent={activeTab !== 'link'}
					class:text-gray-500={activeTab !== 'link'}
					class:hover:text-gray-700={activeTab !== 'link'}
					class:hover:border-gray-300={activeTab !== 'link'}
					aria-current={activeTab === 'link' ? 'page' : undefined}
				>
					Link to Accessible Version
				</button>
				<button
					onclick={() => activeTab = 'embed'}
					class="py-2 px-1 border-b-2 font-medium text-sm transition-colors"
					class:border-blue-600={activeTab === 'embed'}
					class:text-blue-600={activeTab === 'embed'}
					class:border-transparent={activeTab !== 'embed'}
					class:text-gray-500={activeTab !== 'embed'}
					class:hover:text-gray-700={activeTab !== 'embed'}
					class:hover:border-gray-300={activeTab !== 'embed'}
					aria-current={activeTab === 'embed' ? 'page' : undefined}
				>
					Embed Code
				</button>
			</nav>
		</div>

		<!-- Tab Content -->
		{#if activeTab === 'link'}
			<!-- Link HTML Section -->
			<div>
				<p class="text-sm text-gray-600 mb-3">
					Copy this HTML link code to add a link to the accessible version on your website.
				</p>
				<div class="flex items-start gap-2 mb-4">
					<div class="flex-1 bg-gray-50 rounded-md px-3 py-2 border border-gray-300 font-mono text-sm overflow-x-auto">
						<code class="text-gray-900 whitespace-nowrap">&lt;a href="{previewUrl}" target="_blank" rel="noopener noreferrer"&gt;View Accessible Version&lt;/a&gt;</code>
					</div>
					<button
						onclick={copyLinkHTML}
						class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
						title="Copy link HTML to clipboard"
					>
						{#if linkCopied}
							<svg class="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
						{:else}
							<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
							</svg>
						{/if}
					</button>
				</div>

				<!-- Link Usage Instructions -->
				<div class="rounded-lg bg-blue-50 border border-blue-200 p-4">
					<div class="flex">
						<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h4 class="text-sm font-medium text-blue-800">How to use</h4>
							<div class="mt-2 text-sm text-blue-700">
								<ul class="list-disc list-inside space-y-1">
									<li>Add this link to your navigation menu, footer, or anywhere on your site</li>
									<li>Users can click the link to view the fully accessible version in a new tab</li>
									<li>Customize the link text (e.g., "Accessible Version", "Screen Reader Friendly")</li>
									<li>The link opens in a new window with proper security attributes</li>
								</ul>
							</div>
						</div>
					</div>
				</div>
			</div>
		{:else}
			<!-- Iframe Snippet Section -->
			<div>
				<p class="text-sm text-gray-600 mb-3">
					Copy this iframe snippet to embed the accessible version on your website.
				</p>
				<div class="mb-4">
					<IframeSnippet snippet={iframeSnippet} />
				</div>

				<!-- Embed Usage Instructions -->
				<div class="rounded-lg bg-blue-50 border border-blue-200 p-4">
					<div class="flex">
						<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h4 class="text-sm font-medium text-blue-800">How to use</h4>
							<div class="mt-2 text-sm text-blue-700">
								<ul class="list-disc list-inside space-y-1">
									<li>Paste the iframe code directly into your HTML where you want the content to appear</li>
									<li>The iframe displays the remediated content inline on your page</li>
									<li>Includes proper sandbox attributes for security</li>
									<li>CORS headers are configured to allow embedding from your verified domain</li>
									<li>Adjust the width and height attributes as needed for your layout</li>
								</ul>
							</div>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
