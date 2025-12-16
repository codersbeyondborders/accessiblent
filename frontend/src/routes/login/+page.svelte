<script lang="ts">
	// Login page - User authentication
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	
	// Form state
	let email = '';
	let password = '';
	
	// UI state
	let loading = false;
	let error = '';
	
	// Default redirect destination
	const redirectTo = '/dashboard';
	
	// Handle form submission
	async function handleLogin() {
		error = '';
		
		// Basic validation
		if (!email || !password) {
			error = 'Please enter both email and password';
			return;
		}
		
		loading = true;
		
		const result = await authStore.login(email, password);
		
		loading = false;
		
		if (result.success) {
			// Redirect to original destination or dashboard
			goto(redirectTo);
		} else {
			error = result.error || 'Login failed. Please try again.';
		}
	}
	
	// Handle Enter key in form
	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !loading) {
			e.preventDefault();
			handleLogin();
		}
	}
</script>

<svelte:head>
	<title>Sign In - Accessify</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<Header showAuth={false} />
	
	<div class="flex-grow flex flex-col justify-center py-12 sm:px-6 lg:px-8">
		<div class="sm:mx-auto sm:w-full sm:max-w-md">
			<h2 class="mt-6 text-center text-3xl font-bold text-gray-900">
				Sign in to your account
			</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				Don't have an account?
				<a href="/signup" class="font-medium text-blue-600 hover:text-blue-500">
					Sign up
				</a>
			</p>
		</div>

		<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
			<div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
			<form class="space-y-6" on:submit|preventDefault={handleLogin}>
				{#if error}
					<div class="rounded-lg bg-red-50 border border-red-200 p-3" role="alert">
						<div class="flex">
							<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
							</svg>
							<p class="ml-3 text-sm text-red-700">{error}</p>
						</div>
					</div>
				{/if}

				<!-- Email field -->
				<div>
					<label for="email" class="block text-sm font-medium text-gray-700">
						Email address
					</label>
					<div class="mt-1">
						<input
							id="email"
							name="email"
							type="email"
							autocomplete="email"
							required
							bind:value={email}
							on:keydown={handleKeydown}
							class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
							placeholder="you@organization.com"
						/>
					</div>
				</div>

				<!-- Password field -->
				<div>
					<label for="password" class="block text-sm font-medium text-gray-700">
						Password
					</label>
					<div class="mt-1">
						<input
							id="password"
							name="password"
							type="password"
							autocomplete="current-password"
							required
							bind:value={password}
							on:keydown={handleKeydown}
							class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				<!-- Submit button -->
				<div>
					<button
						type="submit"
						disabled={loading}
						class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{#if loading}
							<span class="flex items-center gap-2">
								<span class="animate-spin h-4 w-4 rounded-full border-2 border-white border-t-transparent"></span>
								Signing in...
							</span>
						{:else}
							Sign in
						{/if}
					</button>
				</div>
			</form>

			<div class="mt-6">
				<div class="relative">
					<div class="absolute inset-0 flex items-center">
						<div class="w-full border-t border-gray-300"></div>
					</div>
					<div class="relative flex justify-center text-sm">
						<span class="px-2 bg-white text-gray-500">
							Need help?
						</span>
					</div>
				</div>

				<div class="mt-6 text-center text-sm text-gray-600">
					<p>
						Haven't verified your email yet? Check your inbox for the verification link.
					</p>
				</div>
			</div>
		</div>
	</div>
	</div>
	
	<Footer />
</div>
