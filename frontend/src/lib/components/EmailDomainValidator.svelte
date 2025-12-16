<script lang="ts">
	// EmailDomainValidator.svelte - Real-time email domain validation component
	
	// Props
	export let email: string = '';
	export let showValidation: boolean = true;
	
	// Public email domains list (matches backend)
	const PUBLIC_EMAIL_DOMAINS = new Set([
		'gmail.com',
		'yahoo.com',
		'outlook.com',
		'hotmail.com',
		'aol.com',
		'icloud.com',
		'mail.com',
		'protonmail.com',
		'zoho.com',
		'yandex.com',
		'gmx.com',
		'live.com',
		'msn.com',
		'me.com',
		'mac.com'
	]);
	
	// Validation state
	let isValid: boolean | null = null;
	let errorMessage: string = '';
	
	// Validate email domain
	function validateEmailDomain(emailValue: string): void {
		if (!emailValue || !emailValue.includes('@')) {
			isValid = null;
			errorMessage = '';
			return;
		}
		
		const domain = emailValue.split('@')[1]?.toLowerCase().trim();
		
		if (!domain) {
			isValid = null;
			errorMessage = '';
			return;
		}
		
		if (PUBLIC_EMAIL_DOMAINS.has(domain)) {
			isValid = false;
			errorMessage = 'Please use your organization email address, not a public email provider';
		} else {
			isValid = true;
			errorMessage = '';
		}
	}
	
	// Reactive validation when email changes
	$: if (showValidation) {
		validateEmailDomain(email);
	}
	
	// Export validation state for parent component
	export { isValid, errorMessage };
</script>

<div class="relative">
	{#if showValidation && email && email.includes('@')}
		{#if isValid === false}
			<div class="mt-1 flex items-start gap-2 text-sm text-red-600" role="alert">
				<svg class="h-5 w-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
					<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
				</svg>
				<span>{errorMessage}</span>
			</div>
		{:else if isValid === true}
			<div class="mt-1 flex items-center gap-2 text-sm text-green-600">
				<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
					<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
				</svg>
				<span>Valid organizational email</span>
			</div>
		{/if}
	{/if}
</div>
