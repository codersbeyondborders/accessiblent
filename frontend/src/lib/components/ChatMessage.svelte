<script lang="ts">
	export let role: 'user' | 'assistant';
	export let text: string;
	export let onSpeak: ((text: string) => void) | undefined = undefined;
	export let onPause: (() => void) | undefined = undefined;
	export let onResume: (() => void) | undefined = undefined;
	export let onStop: (() => void) | undefined = undefined;

	// Highlight accessibility-related keywords in assistant messages
	function highlightAccessibilityTerms(text: string): string {
		if (role !== 'assistant') return text;

		// Keywords to highlight
		const keywords = [
			'accessibility',
			'accessible',
			'WCAG',
			'aria',
			'alt text',
			'contrast',
			'keyboard',
			'screen reader',
			'semantic',
			'heading',
			'label',
			'focus',
			'color contrast',
			'text alternative',
			'landmark',
			'skip link',
			'issue',
			'fix',
			'improvement',
			'remediation'
		];

		let highlighted = text;

		// Create a case-insensitive regex for each keyword
		keywords.forEach((keyword) => {
			const regex = new RegExp(`\\b(${keyword}(?:s|es)?)\\b`, 'gi');
			highlighted = highlighted.replace(
				regex,
				'<mark class="bg-blue-100 text-blue-900 px-1 rounded">$1</mark>'
			);
		});

		return highlighted;
	}

	// Detect if message contains fix references (e.g., "3 color-contrast issue(s)")
	function containsFixReferences(text: string): boolean {
		const fixPatterns = [
			/\d+\s+\w+[-\w]*\s+issue\(s\)/i,
			/accessibility improvements/i,
			/fixes? applied/i,
			/remediation/i
		];

		return fixPatterns.some((pattern) => pattern.test(text));
	}

	$: hasFixReferences = containsFixReferences(text);
	$: highlightedText = highlightAccessibilityTerms(text);
</script>

<div class="flex {role === 'user' ? 'justify-end' : 'justify-start'}">
	<div
		class="{role === 'user'
			? 'bg-blue-600 text-white'
			: 'bg-gray-100 text-gray-900'} rounded-2xl px-4 py-3 max-w-[80%]"
	>
		{#if role === 'assistant' && hasFixReferences}
			<div class="flex items-start gap-2 mb-2">
				<svg
					class="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5"
					fill="currentColor"
					viewBox="0 0 20 20"
				>
					<path
						fill-rule="evenodd"
						d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
						clip-rule="evenodd"
					/>
				</svg>
				<span class="text-xs font-medium text-blue-700">Contains accessibility fix information</span>
			</div>
		{/if}

		<div class="whitespace-pre-wrap text-sm">
			{@html highlightedText}
		</div>

		{#if role === 'assistant' && onSpeak && onPause && onResume && onStop}
			<div class="mt-3 flex gap-2 pt-2 border-t border-gray-200">
				<button
					onclick={() => onSpeak && onSpeak(text)}
					class="rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100 transition-colors"
					aria-label="Play this answer"
				>
					<span class="flex items-center gap-1">
						<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
								clip-rule="evenodd"
							/>
						</svg>
						Play
					</span>
				</button>
				<button
					onclick={() => onPause && onPause()}
					class="rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100 transition-colors"
					aria-label="Pause reading"
				>
					<span class="flex items-center gap-1">
						<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z"
								clip-rule="evenodd"
							/>
						</svg>
						Pause
					</span>
				</button>
				<button
					onclick={() => onResume && onResume()}
					class="rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100 transition-colors"
					aria-label="Resume reading"
				>
					<span class="flex items-center gap-1">
						<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
								clip-rule="evenodd"
							/>
						</svg>
						Resume
					</span>
				</button>
				<button
					onclick={() => onStop && onStop()}
					class="rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100 transition-colors"
					aria-label="Stop reading"
				>
					<span class="flex items-center gap-1">
						<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z"
								clip-rule="evenodd"
							/>
						</svg>
						Stop
					</span>
				</button>
			</div>
		{/if}
	</div>
</div>
