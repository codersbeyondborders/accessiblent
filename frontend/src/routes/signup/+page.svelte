<script lang="ts">
	// Signup page - User registration with organization email validation
	import EmailDomainValidator from '$lib/components/EmailDomainValidator.svelte';
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	
	const API = import.meta.env.VITE_API_BASE as string;
	
	// Form state
	let email = '';
	let password = '';
	let confirmPassword = '';
	let fullName = '';
	let organizationName = '';
	
	// UI state
	let loading = false;
	let error = '';
	let success = false;
	let fieldErrors: Record<string, string> = {};
	
	// Email validation state from child component
	let emailIsValid: boolean | null = null;
	let emailErrorMessage = '';
	
	// Form validation
	function validateForm(): boolean {
		fieldErrors = {};
		
		if (!email) {
			fieldErrors.email = 'Email is required';
		} else if (!email.includes('@')) {
			fieldErrors.email = 'Please enter a valid email address';
		} else if (emailIsValid === false) {
			fieldErrors.email = emailErrorMessage;
		}
		
		if (!password) {
			fieldErrors.password = 'Password is required';
		} else if (password.length < 8) {
			fieldErrors.password = 'Password must be at least 8 characters';
		}
		
		if (!confirmPassword) {
			fieldErrors.confirmPassword = 'Please confirm your password';
		} else if (password !== confirmPassword) {
			fieldErrors.confirmPassword = 'Passwords do not match';
		}
		
		if (!fullName) {
			fieldErrors.fullName = 'Full name is required';
		}
		
		if (!organizationName) {
			fieldErrors.organizationName = 'Organization name is required';
		}
		
		return Object.keys(fieldErrors).length === 0;
	}
	
	// Handle form submission
	async function handleSignup() {
		error = '';
		
		if (!validateForm()) {
			return;
		}
		
		loading = true;
		
		try {
			const response = await fetch(`${API}/api/auth/signup`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					email,
					password,
					full_name: fullName,
					organization_name: organizationName
				})
			});
			
			if (response.ok) {
				success = true;
			} else {
				const errorData = await response.json().catch(() => ({ detail: 'Signup failed' }));
				
				// Handle field-specific errors
				if (errorData.error?.details?.field) {
					fieldErrors[errorData.error.details.field] = errorData.error.message || errorData.detail;
				} else {
					error = errorData.error?.message || errorData.detail || 'Signup failed. Please try again.';
				}
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Network error. Please try again.';
		} finally {
			loading = false;
		}
	}
	
	// Handle Enter key in form
	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !loading) {
			e.preventDefault();
			handleSignup();
		}
	}
</script>

<svelte:head>
	<title>Sign Up - Accessify</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<Header showAuth={false} />
	
	<div class="flex-grow flex flex-col justify-center py-12 sm:px-6 lg:px-8">
		<div class="sm:mx-auto sm:w-full sm:max-w-md">
			<h2 class="mt-6 text-center text-3xl font-bold text-gray-900">
				Create your account
			</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				Already have an account?
				<a href="/login" class="font-medium text-blue-600 hover:text-blue-500">
					Sign in
				</a>
			</p>
		</div>

		<div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
			<div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
			{#if success}
				<div class="rounded-lg bg-green-50 border border-green-200 p-4" role="alert">
					<div class="flex">
						<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
						</svg>
						<div class="ml-3">
							<h3 class="text-sm font-medium text-green-800">
								Account created successfully!
							</h3>
							<div class="mt-2 text-sm text-green-700">
								<p>
									We've sent a verification email to <strong>{email}</strong>.
									Please check your inbox and click the verification link to activate your account.
								</p>
								<p class="mt-2">
									After verifying your email, you can <a href="/login" class="font-medium underline">sign in</a>.
								</p>
							</div>
						</div>
					</div>
				</div>
			{:else}
				<form class="space-y-6" on:submit|preventDefault={handleSignup}>
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
								class:border-red-500={fieldErrors.email}
								aria-invalid={!!fieldErrors.email}
								aria-describedby={fieldErrors.email ? 'email-error' : 'email-help'}
							/>
						</div>
						<EmailDomainValidator bind:email bind:isValid={emailIsValid} bind:errorMessage={emailErrorMessage} />
						{#if fieldErrors.email}
							<p id="email-error" class="mt-1 text-sm text-red-600">{fieldErrors.email}</p>
						{:else}
							<p id="email-help" class="mt-1 text-xs text-gray-500">
								Use your organization email (not Gmail, Yahoo, etc.)
							</p>
						{/if}
					</div>

					<!-- Full name field -->
					<div>
						<label for="fullName" class="block text-sm font-medium text-gray-700">
							Full name
						</label>
						<div class="mt-1">
							<input
								id="fullName"
								name="fullName"
								type="text"
								autocomplete="name"
								required
								bind:value={fullName}
								on:keydown={handleKeydown}
								class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
								class:border-red-500={fieldErrors.fullName}
								aria-invalid={!!fieldErrors.fullName}
								aria-describedby={fieldErrors.fullName ? 'fullName-error' : undefined}
							/>
						</div>
						{#if fieldErrors.fullName}
							<p id="fullName-error" class="mt-1 text-sm text-red-600">{fieldErrors.fullName}</p>
						{/if}
					</div>

					<!-- Organization name field -->
					<div>
						<label for="organizationName" class="block text-sm font-medium text-gray-700">
							Organization name
						</label>
						<div class="mt-1">
							<input
								id="organizationName"
								name="organizationName"
								type="text"
								autocomplete="organization"
								required
								bind:value={organizationName}
								on:keydown={handleKeydown}
								class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
								class:border-red-500={fieldErrors.organizationName}
								aria-invalid={!!fieldErrors.organizationName}
								aria-describedby={fieldErrors.organizationName ? 'organizationName-error' : undefined}
							/>
						</div>
						{#if fieldErrors.organizationName}
							<p id="organizationName-error" class="mt-1 text-sm text-red-600">{fieldErrors.organizationName}</p>
						{/if}
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
								autocomplete="new-password"
								required
								bind:value={password}
								on:keydown={handleKeydown}
								class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
								class:border-red-500={fieldErrors.password}
								aria-invalid={!!fieldErrors.password}
								aria-describedby={fieldErrors.password ? 'password-error' : 'password-help'}
							/>
						</div>
						{#if fieldErrors.password}
							<p id="password-error" class="mt-1 text-sm text-red-600">{fieldErrors.password}</p>
						{:else}
							<p id="password-help" class="mt-1 text-xs text-gray-500">
								Must be at least 8 characters
							</p>
						{/if}
					</div>

					<!-- Confirm password field -->
					<div>
						<label for="confirmPassword" class="block text-sm font-medium text-gray-700">
							Confirm password
						</label>
						<div class="mt-1">
							<input
								id="confirmPassword"
								name="confirmPassword"
								type="password"
								autocomplete="new-password"
								required
								bind:value={confirmPassword}
								on:keydown={handleKeydown}
								class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
								class:border-red-500={fieldErrors.confirmPassword}
								aria-invalid={!!fieldErrors.confirmPassword}
								aria-describedby={fieldErrors.confirmPassword ? 'confirmPassword-error' : undefined}
							/>
						</div>
						{#if fieldErrors.confirmPassword}
							<p id="confirmPassword-error" class="mt-1 text-sm text-red-600">{fieldErrors.confirmPassword}</p>
						{/if}
					</div>

					<!-- Submit button -->
					<div>
						<button
							type="submit"
							disabled={loading || emailIsValid === false}
							class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							{#if loading}
								<span class="flex items-center gap-2">
									<span class="animate-spin h-4 w-4 rounded-full border-2 border-white border-t-transparent"></span>
									Creating account...
								</span>
							{:else}
								Sign up
							{/if}
						</button>
					</div>
				</form>
			{/if}
		</div>
	</div>
	</div>
	
	<Footer />
</div>
