<script lang="ts">
	import { onMount } from 'svelte';
	
	let fontSize = $state(100); // percentage
	let highContrast = $state(false);
	let grayscale = $state(false);
	let letterSpacing = $state(0); // pixels
	let isMinimized = $state(false);
	
	onMount(() => {
		// Load saved preferences
		const saved = localStorage.getItem('a11y-preferences');
		if (saved) {
			const prefs = JSON.parse(saved);
			fontSize = prefs.fontSize || 100;
			highContrast = prefs.highContrast || false;
			grayscale = prefs.grayscale || false;
			letterSpacing = prefs.letterSpacing || 0;
			applySettings();
		}
	});
	
	function applySettings() {
		const root = document.documentElement;
		root.style.fontSize = `${fontSize}%`;
		root.style.letterSpacing = `${letterSpacing}px`;
		
		if (highContrast) {
			root.classList.add('high-contrast');
		} else {
			root.classList.remove('high-contrast');
		}
		
		if (grayscale) {
			root.classList.add('grayscale');
		} else {
			root.classList.remove('grayscale');
		}
		
		// Save preferences
		localStorage.setItem('a11y-preferences', JSON.stringify({
			fontSize,
			highContrast,
			grayscale,
			letterSpacing
		}));
	}
	
	function increaseFontSize() {
		fontSize = Math.min(fontSize + 10, 150);
		applySettings();
	}
	
	function decreaseFontSize() {
		fontSize = Math.max(fontSize - 10, 80);
		applySettings();
	}
	
	function toggleContrast() {
		highContrast = !highContrast;
		applySettings();
	}
	
	function toggleGrayscale() {
		grayscale = !grayscale;
		applySettings();
	}
	
	function increaseSpacing() {
		letterSpacing = Math.min(letterSpacing + 1, 5);
		applySettings();
	}
	
	function decreaseSpacing() {
		letterSpacing = Math.max(letterSpacing - 1, 0);
		applySettings();
	}
	
	function resetAll() {
		fontSize = 100;
		highContrast = false;
		grayscale = false;
		letterSpacing = 0;
		applySettings();
	}
	

</script>

<svelte:head>
	<style>
		.high-contrast {
			filter: contrast(1.5);
		}
		.grayscale {
			filter: grayscale(100%);
		}
		.high-contrast.grayscale {
			filter: contrast(1.5) grayscale(100%);
		}
	</style>
</svelte:head>

<!-- Accessibility Toolbar -->
<div class="fixed bottom-0 left-0 right-0 bg-gray-900 text-white shadow-lg z-40 transition-all duration-300"
     style:transform={isMinimized ? 'translateY(calc(100% - 2.5rem))' : 'translateY(0)'}>
	<div class="max-w-7xl mx-auto px-4 py-3">
		<div class="flex items-center justify-between gap-4">
			<!-- Minimize/Maximize Button -->
			<button
				onclick={() => isMinimized = !isMinimized}
				class="text-white hover:text-gray-300 p-1 transition-transform duration-200"
				aria-label={isMinimized ? 'Show accessibility toolbar' : 'Hide accessibility toolbar'}
			>
				<svg class="w-5 h-5 transition-transform duration-200" 
				     style:transform={isMinimized ? 'rotate(180deg)' : 'rotate(0deg)'}
				     fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</button>
			
			<div class="flex items-center gap-6 flex-wrap">
				<!-- Font Size -->
				<div class="flex items-center gap-2">
					<span class="text-xs font-medium">Font Size</span>
					<button
						onclick={decreaseFontSize}
						class="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-sm"
						aria-label="Decrease font size"
					>
						A-
					</button>
					<span class="text-xs">{fontSize}%</span>
					<button
						onclick={increaseFontSize}
						class="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-sm"
						aria-label="Increase font size"
					>
						A+
					</button>
				</div>
				
				<!-- Contrast -->
				<button
					onclick={toggleContrast}
					class="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-sm"
					class:bg-blue-600={highContrast}
					class:hover:bg-blue-700={highContrast}
					aria-pressed={highContrast}
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
					</svg>
					Contrast
				</button>
				
				<!-- Grayscale -->
				<button
					onclick={toggleGrayscale}
					class="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded text-sm"
					class:bg-blue-600={grayscale}
					class:hover:bg-blue-700={grayscale}
					aria-pressed={grayscale}
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
					</svg>
					Grayscale
				</button>
				
				<!-- Letter Spacing -->
				<div class="flex items-center gap-2">
					<span class="text-xs font-medium">Spacing</span>
					<button
						onclick={decreaseSpacing}
						class="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-sm"
						aria-label="Decrease letter spacing"
					>
						-
					</button>
					<span class="text-xs">{letterSpacing}px</span>
					<button
						onclick={increaseSpacing}
						class="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-sm"
						aria-label="Increase letter spacing"
					>
						+
					</button>
				</div>
				
				<!-- Reset -->
				<button
					onclick={resetAll}
					class="text-xs text-gray-400 hover:text-white underline"
					aria-label="Reset all accessibility settings"
				>
					Reset
				</button>
			</div>
		</div>
	</div>
</div>
