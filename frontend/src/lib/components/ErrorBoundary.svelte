<script lang="ts">
	// Error boundary component to catch and display component errors
	import { onMount } from 'svelte';
	
	// Props
	export let fallback: string = 'Something went wrong. Please try again.';
	export let showDetails: boolean = false;
	
	// State
	let hasError = false;
	let errorMessage = '';
	let errorStack = '';
	
	// Development mode detection
	const isDev = import.meta.env.DEV;
	
	// Error handler
	function handleError(event: ErrorEvent) {
		hasError = true;
		errorMessage = event.error?.message || event.message || 'Unknown error';
		errorStack = event.error?.stack || '';
		
		// Log error in development
		if (isDev) {
			console.error('ErrorBoundary caught error:', {
				message: errorMessage,
				stack: errorStack,
				error: event.error
			});
		}
		
		// Prevent default error handling
		event.preventDefault();
	}
	
	// Reset error state
	function resetError() {
		hasError = false;
		errorMessage = '';
		errorStack = '';
	}
	
	// Set up error listener on mount
	onMount(() => {
		window.addEventListener('error', handleError);
		
		return () => {
			window.removeEventListener('error', handleError);
		};
	});
</script>

{#if hasError}
	<div class="min-h-[200px] flex items-center justify-center p-6">
		<div class="max-w-md w-full bg-red-50 border border-red-200 rounded-lg p-6">
			<div class="flex items-start gap-3">
				<svg
					class="h-6 w-6 text-red-400 flex-shrink-0"
					fill="currentColor"
					viewBox="0 0 20 20"
					aria-hidden="true"
				>
					<path
						fill-rule="evenodd"
						d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
						clip-rule="evenodd"
					/>
				</svg>
				<div class="flex-1">
					<h3 class="text-sm font-medium text-red-800">Error</h3>
					<div class="mt-2 text-sm text-red-700">
						<p>{fallback}</p>
						
						{#if (isDev || showDetails) && errorMessage}
							<details class="mt-3">
								<summary class="cursor-pointer font-medium hover:underline">
									Technical details
								</summary>
								<div class="mt-2 p-3 bg-red-100 rounded text-xs font-mono overflow-auto">
									<p class="font-semibold">Message:</p>
									<p class="mb-2">{errorMessage}</p>
									
									{#if errorStack}
										<p class="font-semibold">Stack trace:</p>
										<pre class="whitespace-pre-wrap">{errorStack}</pre>
									{/if}
								</div>
							</details>
						{/if}
					</div>
					<div class="mt-4">
						<button
							type="button"
							onclick={resetError}
							class="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
						>
							Try again
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
{:else}
	<slot />
{/if}
