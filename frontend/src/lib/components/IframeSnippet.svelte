<script lang="ts">
	// IframeSnippet component
	// Requirements: 6.3, 6.4
	
	interface Props {
		snippet: string;
	}
	
	let { snippet }: Props = $props();
	
	let copied = $state(false);
	let copyTimeout: ReturnType<typeof setTimeout> | null = null;
	
	function copyToClipboard() {
		navigator.clipboard.writeText(snippet).then(() => {
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
	
	// Format the snippet for display with proper indentation
	let formattedSnippet = $derived(() => {
		// Basic formatting - add line breaks for readability
		return snippet
			.replace(/></g, '>\n<')
			.split('\n')
			.map(line => line.trim())
			.filter(line => line.length > 0)
			.join('\n');
	});
</script>

<div class="relative">
	<!-- Code Block -->
	<div class="bg-gray-900 rounded-lg overflow-hidden">
		<div class="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
			<span class="text-xs font-medium text-gray-300">HTML</span>
			<button
				onclick={copyToClipboard}
				class="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-blue-500 transition-colors"
			>
				{#if copied}
					<svg class="mr-1 h-3 w-3 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
					Copied!
				{:else}
					<svg class="mr-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
					</svg>
					Copy
				{/if}
			</button>
		</div>
		<div class="p-4 overflow-x-auto">
			<pre class="text-sm text-gray-100 font-mono"><code>{formattedSnippet()}</code></pre>
		</div>
	</div>
	
	<!-- Helper Text -->
	<p class="mt-2 text-xs text-gray-500">
		Paste this code into your HTML where you want the accessible content to appear.
	</p>
</div>

<style>
	pre {
		margin: 0;
		white-space: pre-wrap;
		word-wrap: break-word;
	}
	
	code {
		font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
	}
</style>
