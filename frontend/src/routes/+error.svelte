<script lang="ts">
	// Global error page for route-level errors
	import { page } from '$app/stores';
	import logo from '$lib/assets/logo.png';
	
	$: error = $page.error;
	$: status = $page.status;
	
	function getErrorMessage(status: number): string {
		switch (status) {
			case 404:
				return 'Page not found';
			case 403:
				return 'Access denied';
			case 401:
				return 'Authentication required';
			case 500:
				return 'Internal server error';
			default:
				return 'An error occurred';
		}
	}
	
	function getErrorDescription(status: number): string {
		switch (status) {
			case 404:
				return "The page you're looking for doesn't exist or has been moved.";
			case 403:
				return "You don't have permission to access this page.";
			case 401:
				return 'Please sign in to access this page.';
			case 500:
				return 'Something went wrong on our end. Please try again later.';
			default:
				return 'Something unexpected happened. Please try again.';
		}
	}
</script>

<svelte:head>
	<title>{getErrorMessage(status)} - Accessify</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full mx-auto">
		<div class="text-center">
			<a href="/" class="inline-block">
				<img src={logo} alt="Accessify Logo" class="h-16 w-auto mx-auto" />
			</a>
			
			<div class="mt-8">
				<div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
					<svg
						class="h-8 w-8 text-red-600"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
						/>
					</svg>
				</div>
				
				<h1 class="text-3xl font-bold text-gray-900 mb-2">
					{status} - {getErrorMessage(status)}
				</h1>
				
				<p class="text-gray-600 mb-8">
					{getErrorDescription(status)}
				</p>
				
				{#if import.meta.env.DEV && error}
					<details class="text-left mb-8 p-4 bg-red-50 border border-red-200 rounded-lg">
						<summary class="cursor-pointer font-medium text-red-800 hover:underline">
							Technical details (dev mode)
						</summary>
						<div class="mt-2 text-sm text-red-700 font-mono overflow-auto">
							<pre class="whitespace-pre-wrap">{error.message || String(error)}</pre>
						</div>
					</details>
				{/if}
				
				<div class="flex flex-col sm:flex-row gap-3 justify-center">
					<a
						href="/"
						class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
					>
						Go to homepage
					</a>
					
					{#if status === 401}
						<a
							href="/login"
							class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
						>
							Sign in
						</a>
					{:else}
						<button
							type="button"
							onclick={() => window.history.back()}
							class="inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
						>
							Go back
						</button>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>
