<script lang="ts">
	// Email verification page - Verify user email with token
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import logo from '$lib/assets/logo.png';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	// Get token from URL params
	$: token = $page.params.token;
	
	// UI state
	let loading = true;
	let success = false;
	let error = '';
	let redirectCountdown = 5;
	
	// Verify email on mount
	onMount(async () => {
		if (!token) {
			error = 'Invalid verification link';
			loading = false;
			return;
		}
		
		try {
			const response = await fetch(`${API}/api/auth/verify-email/${token}`, {
				method: 'POST'
			});
			
			if (response.ok) {
				success = true;
				
				// Start countdown to redirect
				const interval = setInterval(() => {
					redirectCountdown--;
					if (redirectCountdown <= 0) {
						clearInterval(interval);
						goto('/login');
					}
				}, 1000);
			} else {
				const errorData = await response.json().catch(() => ({ detail: 'Verification failed' }));
				error = errorData.error?.message || errorData.detail || 'Verification failed. The link may be invalid or expired.';
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Network error. Please try again.';
		} finally {
			loading = false;
		}
	});
	
	// Manual redirect to login
	function redirectToLogin() {
		goto('/login');
	}
</script>

<svelte:head>
	<title>Verify Email - Accessify</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<Header showAuth={false} />
	
	<div class="flex-grow flex flex-col justify-center py-12 sm:px-6 lg:px-8">
		<div class="sm:mx-auto sm:w-full sm:max-w-md">
		<h2 class="mt-6 text-center text-3xl font-bold text-gray-900">
			Email Verification
		</h2>
	</div>

	<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
		<div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
			{#if loading}
				<div class="text-center">
					<div class="inline-flex items-center gap-3">
						<span class="animate-spin h-8 w-8 rounded-full border-4 border-blue-600 border-t-transparent"></span>
						<span class="text-lg text-gray-700">Verifying your email...</span>
					</div>
				</div>
			{:else if success}
				<div class="rounded-lg bg-green-50 border border-green-200 p-4" role="alert">
					<div class="flex">
						<svg class="h-6 w-6 text-green-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h3 class="text-lg font-medium text-green-800">
								Email verified successfully!
							</h3>
							<div class="mt-2 text-sm text-green-700">
								<p>
									Your account has been activated. You can now sign in to access your dashboard.
								</p>
								<p class="mt-3">
									Redirecting to login in <strong>{redirectCountdown}</strong> seconds...
								</p>
							</div>
							<div class="mt-4">
								<button
									on:click={redirectToLogin}
									class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
								>
									Go to login now
								</button>
							</div>
						</div>
					</div>
				</div>
			{:else if error}
				<div class="rounded-lg bg-red-50 border border-red-200 p-4" role="alert">
					<div class="flex">
						<svg class="h-6 w-6 text-red-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h3 class="text-lg font-medium text-red-800">
								Verification failed
							</h3>
							<div class="mt-2 text-sm text-red-700">
								<p>{error}</p>
								<p class="mt-3">
									Please try signing up again or contact support if the problem persists.
								</p>
							</div>
							<div class="mt-4 flex gap-3">
								<a
									href="/signup"
									class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
								>
									Sign up again
								</a>
								<a
									href="/login"
									class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
								>
									Go to login
								</a>
							</div>
						</div>
					</div>
				</div>
			{/if}
		</div>
	</div>
	
	<Footer />
</div>
