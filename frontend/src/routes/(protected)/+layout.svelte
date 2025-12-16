<script lang="ts">
	import { authStore } from '$lib/stores/auth';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import Footer from '$lib/components/Footer.svelte';
	import logo from '$lib/assets/logo.png';

	export let data: { user: any };

	let mobileMenuOpen = false;

	// Update auth store with user data from layout
	onMount(() => {
		if (data.user) {
			authStore.checkAuth();
		}
	});

	$: user = $authStore.user;
	$: currentPath = $page.url.pathname;

	function isActive(path: string): boolean {
		if (path === '/dashboard') {
			return currentPath === path;
		}
		return currentPath.startsWith(path);
	}

	async function handleLogout() {
		await authStore.logout();
	}

	function toggleMobileMenu() {
		mobileMenuOpen = !mobileMenuOpen;
	}
</script>

<div class="min-h-screen flex flex-col bg-gray-50">
	<!-- Navigation Header -->
	<nav class="bg-white shadow-sm">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between h-16">
				<!-- Logo and Navigation Links -->
				<div class="flex">
					<!-- Logo -->
					<div class="flex-shrink-0 flex items-center">
						<a href="/dashboard" class="flex items-center">
							<img src={logo} alt="Accessify Logo" class="h-12 w-auto" />
						</a>
					</div>

					<!-- Desktop Navigation -->
					<div class="hidden sm:ml-8 sm:flex sm:space-x-8">
						<a
							href="/dashboard"
							class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
							class:border-blue-500={isActive('/dashboard')}
							class:text-gray-900={isActive('/dashboard')}
							class:border-transparent={!isActive('/dashboard')}
							class:text-gray-500={!isActive('/dashboard')}
							class:hover:text-gray-700={!isActive('/dashboard')}
							class:hover:border-gray-300={!isActive('/dashboard')}
						>
							Dashboard
						</a>
						<a
							href="/domains/add"
							class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
							class:border-blue-500={isActive('/domains')}
							class:text-gray-900={isActive('/domains')}
							class:border-transparent={!isActive('/domains')}
							class:text-gray-500={!isActive('/domains')}
							class:hover:text-gray-700={!isActive('/domains')}
							class:hover:border-gray-300={!isActive('/domains')}
						>
							Domains
						</a>
						<a
							href="/websites/register"
							class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
							class:border-blue-500={isActive('/websites')}
							class:text-gray-900={isActive('/websites')}
							class:border-transparent={!isActive('/websites')}
							class:text-gray-500={!isActive('/websites')}
							class:hover:text-gray-700={!isActive('/websites')}
							class:hover:border-gray-300={!isActive('/websites')}
						>
							Websites
						</a>
					</div>
				</div>

				<!-- User Menu -->
				<div class="hidden sm:ml-6 sm:flex sm:items-center">
					<!-- User Info -->
					{#if user}
						<div class="flex items-center gap-4">
							<div class="text-right">
								<p class="text-sm font-medium text-gray-900">{user.full_name}</p>
								<p class="text-xs text-gray-500">{user.email}</p>
							</div>
							<button
								onclick={handleLogout}
								class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
							>
								<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
								</svg>
								Logout
							</button>
						</div>
					{/if}
				</div>

				<!-- Mobile menu button -->
				<div class="flex items-center sm:hidden">
					<button
						onclick={toggleMobileMenu}
						type="button"
						class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
						aria-expanded={mobileMenuOpen}
					>
						<span class="sr-only">Open main menu</span>
						{#if !mobileMenuOpen}
							<svg class="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
							</svg>
						{:else}
							<svg class="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						{/if}
					</button>
				</div>
			</div>
		</div>

		<!-- Mobile menu -->
		{#if mobileMenuOpen}
			<div class="sm:hidden">
				<div class="pt-2 pb-3 space-y-1">
					<a
						href="/dashboard"
						class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
						class:border-blue-500={isActive('/dashboard')}
						class:bg-blue-50={isActive('/dashboard')}
						class:text-blue-700={isActive('/dashboard')}
						class:border-transparent={!isActive('/dashboard')}
						class:text-gray-600={!isActive('/dashboard')}
						class:hover:bg-gray-50={!isActive('/dashboard')}
						class:hover:border-gray-300={!isActive('/dashboard')}
						class:hover:text-gray-800={!isActive('/dashboard')}
					>
						Dashboard
					</a>
					<a
						href="/domains/add"
						class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
						class:border-blue-500={isActive('/domains')}
						class:bg-blue-50={isActive('/domains')}
						class:text-blue-700={isActive('/domains')}
						class:border-transparent={!isActive('/domains')}
						class:text-gray-600={!isActive('/domains')}
						class:hover:bg-gray-50={!isActive('/domains')}
						class:hover:border-gray-300={!isActive('/domains')}
						class:hover:text-gray-800={!isActive('/domains')}
					>
						Domains
					</a>
					<a
						href="/websites/register"
						class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
						class:border-blue-500={isActive('/websites')}
						class:bg-blue-50={isActive('/websites')}
						class:text-blue-700={isActive('/websites')}
						class:border-transparent={!isActive('/websites')}
						class:text-gray-600={!isActive('/websites')}
						class:hover:bg-gray-50={!isActive('/websites')}
						class:hover:border-gray-300={!isActive('/websites')}
						class:hover:text-gray-800={!isActive('/websites')}
					>
						Websites
					</a>
				</div>
				{#if user}
					<div class="pt-4 pb-3 border-t border-gray-200">
						<div class="px-4">
							<div class="text-base font-medium text-gray-800">{user.full_name}</div>
							<div class="text-sm font-medium text-gray-500">{user.email}</div>
						</div>
						<div class="mt-3 px-2">
							<button
								onclick={handleLogout}
								class="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-50"
							>
								Logout
							</button>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</nav>

	<!-- Main Content -->
	<main class="flex-grow">
		<slot />
	</main>
	
	<!-- Footer -->
	<Footer />
</div>
