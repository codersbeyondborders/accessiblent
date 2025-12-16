<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	import Toast from '$lib/components/Toast.svelte';
	import AccessibilityToolbar from '$lib/components/AccessibilityToolbar.svelte';
	import { setupGlobalErrorHandlers } from '$lib/utils/errorHandler';
	
	// Set up global error handlers on mount
	onMount(() => {
		setupGlobalErrorHandlers();
	});
</script>

<div class="pb-16">
	<slot />
</div>

<!-- Global toast notifications -->
<Toast />

<!-- Accessibility toolbar -->
<AccessibilityToolbar />
