<script lang="ts">
	// VerificationStatus component - Real-time status indicator for domain verification
	// Requirements: 2.4, 2.5
	
	interface Props {
		status: 'pending' | 'verifying' | 'verified' | 'failed';
		verifiedAt?: string;
		verificationMethod?: string;
		errorMessage?: string;
		troubleshooting?: {
			meta_tag_found?: boolean;
			wellknown_found?: boolean;
			http_status?: number;
			error_details?: string;
		};
	}
	
	let { 
		status, 
		verifiedAt, 
		verificationMethod,
		errorMessage,
		troubleshooting 
	}: Props = $props();
</script>

<div class="bg-white rounded-lg border border-gray-200 p-6">
	<h3 class="text-lg font-medium text-gray-900 mb-4">Verification Status</h3>
	
	{#if status === 'pending'}
		<!-- Pending State -->
		<div class="flex items-start">
			<div class="flex-shrink-0">
				<svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
			</div>
			<div class="ml-3">
				<h4 class="text-sm font-medium text-gray-900">Awaiting Verification</h4>
				<p class="mt-1 text-sm text-gray-600">
					Add the verification code to your website using one of the methods above, then click "Verify Now" to check.
				</p>
			</div>
		</div>
	{:else if status === 'verifying'}
		<!-- Verifying State -->
		<div class="flex items-start">
			<div class="flex-shrink-0">
				<div class="animate-spin h-6 w-6 rounded-full border-2 border-blue-600 border-t-transparent"></div>
			</div>
			<div class="ml-3">
				<h4 class="text-sm font-medium text-blue-900">Verifying...</h4>
				<p class="mt-1 text-sm text-blue-700">
					Checking your website for the verification code. This may take a few seconds.
				</p>
			</div>
		</div>
	{:else if status === 'verified'}
		<!-- Verified State -->
		<div class="rounded-lg bg-green-50 border border-green-200 p-4">
			<div class="flex">
				<svg class="h-6 w-6 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
				</svg>
				<div class="ml-3">
					<h4 class="text-sm font-medium text-green-800">Domain Verified!</h4>
					<div class="mt-2 text-sm text-green-700">
						<p>
							Your domain has been successfully verified
							{#if verificationMethod}
								using the <strong>{verificationMethod}</strong> method
							{/if}
							{#if verifiedAt}
								on {new Date(verifiedAt).toLocaleDateString()} at {new Date(verifiedAt).toLocaleTimeString()}
							{/if}.
						</p>
						<p class="mt-2">
							You can now register websites under this domain for accessibility remediation.
						</p>
					</div>
				</div>
			</div>
		</div>
	{:else if status === 'failed'}
		<!-- Failed State -->
		<div class="rounded-lg bg-red-50 border border-red-200 p-4">
			<div class="flex">
				<svg class="h-6 w-6 text-red-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
				</svg>
				<div class="ml-3">
					<h4 class="text-sm font-medium text-red-800">Verification Failed</h4>
					<div class="mt-2 text-sm text-red-700">
						{#if errorMessage}
							<p>{errorMessage}</p>
						{:else}
							<p>We couldn't verify your domain. Please check the troubleshooting tips below.</p>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<!-- Troubleshooting Section -->
		{#if troubleshooting}
			<div class="mt-4 space-y-3">
				<h4 class="text-sm font-medium text-gray-900">Troubleshooting</h4>
				
				<div class="bg-gray-50 rounded-lg p-4 space-y-3">
					{#if troubleshooting.http_status}
						<div class="flex items-start">
							<svg class="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<div class="ml-3">
								<p class="text-sm text-gray-700">
									<strong>HTTP Status:</strong> {troubleshooting.http_status}
									{#if troubleshooting.http_status !== 200}
										<span class="text-red-600">(Expected 200)</span>
									{/if}
								</p>
							</div>
						</div>
					{/if}

					{#if troubleshooting.meta_tag_found !== undefined}
						<div class="flex items-start">
							<svg class="h-5 w-5 flex-shrink-0 mt-0.5" class:text-green-500={troubleshooting.meta_tag_found} class:text-red-500={!troubleshooting.meta_tag_found} fill="currentColor" viewBox="0 0 20 20">
								{#if troubleshooting.meta_tag_found}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
								{:else}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
								{/if}
							</svg>
							<div class="ml-3">
								<p class="text-sm text-gray-700">
									<strong>Meta Tag:</strong> 
									{#if troubleshooting.meta_tag_found}
										<span class="text-green-600">Found</span>
									{:else}
										<span class="text-red-600">Not found</span>
									{/if}
								</p>
							</div>
						</div>
					{/if}

					{#if troubleshooting.wellknown_found !== undefined}
						<div class="flex items-start">
							<svg class="h-5 w-5 flex-shrink-0 mt-0.5" class:text-green-500={troubleshooting.wellknown_found} class:text-red-500={!troubleshooting.wellknown_found} fill="currentColor" viewBox="0 0 20 20">
								{#if troubleshooting.wellknown_found}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
								{:else}
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
								{/if}
							</svg>
							<div class="ml-3">
								<p class="text-sm text-gray-700">
									<strong>Well-Known File:</strong> 
									{#if troubleshooting.wellknown_found}
										<span class="text-green-600">Found</span>
									{:else}
										<span class="text-red-600">Not found</span>
									{/if}
								</p>
							</div>
						</div>
					{/if}

					{#if troubleshooting.error_details}
						<div class="flex items-start">
							<svg class="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<div class="ml-3">
								<p class="text-sm text-gray-700">
									<strong>Details:</strong> {troubleshooting.error_details}
								</p>
							</div>
						</div>
					{/if}
				</div>

				<!-- Common Issues -->
				<div class="bg-yellow-50 rounded-lg border border-yellow-200 p-4">
					<h5 class="text-sm font-medium text-yellow-800 mb-2">Common Issues:</h5>
					<ul class="list-disc list-inside space-y-1 text-sm text-yellow-700">
						<li>Make sure you've added the verification code to your <strong>live website</strong>, not a local development version</li>
						<li>If using the meta tag method, ensure it's in the <code class="bg-yellow-100 px-1 rounded">&lt;head&gt;</code> section of your homepage</li>
						<li>If using the well-known file method, ensure the file is accessible via HTTPS and returns a 200 status code</li>
						<li>Check that your web server is configured to serve files from the <code class="bg-yellow-100 px-1 rounded">.well-known</code> directory</li>
						<li>Clear your browser cache and try accessing the verification URL directly to confirm it's working</li>
						<li>Wait a few minutes after making changes for DNS and CDN caches to update</li>
					</ul>
				</div>
			</div>
		{/if}
	{/if}
</div>
