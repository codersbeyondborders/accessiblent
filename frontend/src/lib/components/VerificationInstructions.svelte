<script lang="ts">
	// VerificationInstructions component - Tabbed interface for domain verification methods
	// Requirements: 2.2
	
	interface VerificationMethod {
		method: string;
		description: string;
		code: string;
		location: string;
	}
	
	interface Props {
		metaTag: VerificationMethod;
		wellknown: VerificationMethod;
	}
	
	let { metaTag, wellknown }: Props = $props();
	
	// State
	let activeTab = $state<'meta' | 'wellknown'>('meta');
	let copiedMeta = $state(false);
	let copiedWellknown = $state(false);
	
	// Copy to clipboard
	async function copyToClipboard(text: string, type: 'meta' | 'wellknown') {
		try {
			await navigator.clipboard.writeText(text);
			
			if (type === 'meta') {
				copiedMeta = true;
				setTimeout(() => copiedMeta = false, 2000);
			} else {
				copiedWellknown = true;
				setTimeout(() => copiedWellknown = false, 2000);
			}
		} catch (err) {
			console.error('Failed to copy:', err);
		}
	}
</script>

<div class="bg-white rounded-lg border border-gray-200">
	<!-- Tab Headers -->
	<div class="border-b border-gray-200">
		<nav class="flex -mb-px" aria-label="Verification methods">
			<button
				type="button"
				onclick={() => activeTab = 'meta'}
				class="flex-1 py-4 px-6 text-center border-b-2 font-medium text-sm transition-colors"
				class:border-blue-500={activeTab === 'meta'}
				class:text-blue-600={activeTab === 'meta'}
				class:border-transparent={activeTab !== 'meta'}
				class:text-gray-500={activeTab !== 'meta'}
				class:hover:text-gray-700={activeTab !== 'meta'}
				class:hover:border-gray-300={activeTab !== 'meta'}
				aria-current={activeTab === 'meta' ? 'page' : undefined}
			>
				<svg class="inline-block w-5 h-5 mr-2 -mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
				</svg>
				HTML Meta Tag
			</button>
			<button
				type="button"
				onclick={() => activeTab = 'wellknown'}
				class="flex-1 py-4 px-6 text-center border-b-2 font-medium text-sm transition-colors"
				class:border-blue-500={activeTab === 'wellknown'}
				class:text-blue-600={activeTab === 'wellknown'}
				class:border-transparent={activeTab !== 'wellknown'}
				class:text-gray-500={activeTab !== 'wellknown'}
				class:hover:text-gray-700={activeTab !== 'wellknown'}
				class:hover:border-gray-300={activeTab !== 'wellknown'}
				aria-current={activeTab === 'wellknown' ? 'page' : undefined}
			>
				<svg class="inline-block w-5 h-5 mr-2 -mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
				</svg>
				Well-Known File
			</button>
		</nav>
	</div>

	<!-- Tab Content -->
	<div class="p-6">
		{#if activeTab === 'meta'}
			<!-- Meta Tag Instructions -->
			<div class="space-y-4">
				<div>
					<h3 class="text-lg font-medium text-gray-900">{metaTag.method}</h3>
					<p class="mt-1 text-sm text-gray-600">{metaTag.description}</p>
				</div>

				<div>
					<div class="flex items-center justify-between mb-2">
						<span class="block text-sm font-medium text-gray-700">
							Code to add:
						</span>
						<button
							type="button"
							onclick={() => copyToClipboard(metaTag.code, 'meta')}
							class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
						>
							{#if copiedMeta}
								<svg class="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
								</svg>
								<span class="ml-1">Copied!</span>
							{:else}
								<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
								</svg>
								<span class="ml-1">Copy</span>
							{/if}
						</button>
					</div>
					<pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm"><code>{metaTag.code}</code></pre>
				</div>

				<div class="rounded-lg bg-blue-50 border border-blue-200 p-4">
					<div class="flex">
						<svg class="h-5 w-5 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h4 class="text-sm font-medium text-blue-800">Location</h4>
							<p class="mt-1 text-sm text-blue-700">
								Add this meta tag inside the <code class="bg-blue-100 px-1 rounded">&lt;head&gt;</code> section of your homepage at:
							</p>
							<p class="mt-1 text-sm font-mono text-blue-900 break-all">
								{metaTag.location}
							</p>
						</div>
					</div>
				</div>

				<div class="rounded-lg bg-yellow-50 border border-yellow-200 p-4">
					<div class="flex">
						<svg class="h-5 w-5 text-yellow-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h4 class="text-sm font-medium text-yellow-800">Important</h4>
							<p class="mt-1 text-sm text-yellow-700">
								Make sure the meta tag is added to your live website, not just a local development version.
							</p>
						</div>
					</div>
				</div>
			</div>
		{:else}
			<!-- Well-Known File Instructions -->
			<div class="space-y-4">
				<div>
					<h3 class="text-lg font-medium text-gray-900">{wellknown.method}</h3>
					<p class="mt-1 text-sm text-gray-600">{wellknown.description}</p>
				</div>

				<div>
					<div class="flex items-center justify-between mb-2">
						<span class="block text-sm font-medium text-gray-700">
							File content:
						</span>
						<button
							type="button"
							onclick={() => copyToClipboard(wellknown.code, 'wellknown')}
							class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
						>
							{#if copiedWellknown}
								<svg class="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
									<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
								</svg>
								<span class="ml-1">Copied!</span>
							{:else}
								<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
								</svg>
								<span class="ml-1">Copy</span>
							{/if}
						</button>
					</div>
					<pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm"><code>{wellknown.code}</code></pre>
				</div>

				<div class="rounded-lg bg-blue-50 border border-blue-200 p-4">
					<div class="flex">
						<svg class="h-5 w-5 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h4 class="text-sm font-medium text-blue-800">File Location</h4>
							<p class="mt-1 text-sm text-blue-700">
								Create a text file with the content above and upload it to:
							</p>
							<p class="mt-1 text-sm font-mono text-blue-900 break-all">
								{wellknown.location}
							</p>
						</div>
					</div>
				</div>

				<div class="space-y-3">
					<h4 class="text-sm font-medium text-gray-900">Steps:</h4>
					<ol class="list-decimal list-inside space-y-2 text-sm text-gray-700">
						<li>Create a directory named <code class="bg-gray-100 px-1 rounded">.well-known</code> in your website's root directory</li>
						<li>Create a text file named <code class="bg-gray-100 px-1 rounded">accessify-verification.txt</code> in that directory</li>
						<li>Paste the verification token (shown above) as the only content in the file</li>
						<li>Upload the file to your web server</li>
						<li>Ensure the file is accessible at the URL shown above</li>
					</ol>
				</div>

				<div class="rounded-lg bg-yellow-50 border border-yellow-200 p-4">
					<div class="flex">
						<svg class="h-5 w-5 text-yellow-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h4 class="text-sm font-medium text-yellow-800">Important</h4>
							<p class="mt-1 text-sm text-yellow-700">
								The file must be accessible via HTTPS and return a 200 status code. Make sure your web server is configured to serve files from the <code class="bg-yellow-100 px-1 rounded">.well-known</code> directory.
							</p>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
