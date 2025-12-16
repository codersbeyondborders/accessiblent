<script lang="ts">
	import logo from '$lib/assets/logo.png';
	
	export let showAuth = true;
</script>

<header class="bg-white shadow-sm">
	<nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
		<div class="flex justify-between items-center">
			<a href="/" class="flex items-center">
				<img src={logo} alt="Accessify Logo" class="h-12 w-auto" />
			</a>
			{#if showAuth}
				<div class="flex gap-4 items-center">
					<a 
						href="/login" 
						class="text-gray-600 hover:text-gray-900 font-medium transition-colors"
					>
						Sign In
					</a>
					<a 
						href="/signup" 
						class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
					>
						Sign Up
					</a>
				</div>
			{/if}
		</div>
	</nav>
</header>
