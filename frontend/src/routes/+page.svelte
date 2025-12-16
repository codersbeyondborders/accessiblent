<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
</script>

<svelte:head>
	<title>Accessify - Your Smart Accessibility Agent</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<!-- Header -->
	<Header showAuth={true} />

	<!-- Main Content -->
	<main class="flex-grow">
		<!-- Hero Section -->
		<section class="bg-gradient-to-b from-blue-50 to-white py-16">
			<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="text-center">
					<h1 class="text-4xl font-bold text-gray-900 mb-4">
						Make Your Website Accessible
					</h1>
					<p class="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
						Automatically detect and fix accessibility issues on your website with AI.
					</p>
					<div class="flex justify-center gap-3">
						<a 
							href="/signup" 
							class="inline-flex items-center px-6 py-3 text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700"
						>
							Get Started
						</a>
						<a 
							href="/websites" 
							class="inline-flex items-center px-6 py-3 text-base font-medium rounded-lg text-gray-700 bg-white border border-gray-300 hover:bg-gray-50"
						>
							View Examples
						</a>
					</div>
				</div>
			</div>
		</section>

		<!-- Features and How It Works Section -->
		<section class="py-12 bg-white">
			<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
					<!-- Left Column: Features -->
					<div>
						<h2 class="text-2xl font-bold text-gray-900 mb-6">
							Key Features
						</h2>
						<div class="space-y-6">
							<div class="flex gap-4">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-blue-100">
										<svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
										</svg>
									</div>
								</div>
								<div>
									<h3 class="text-base font-semibold text-gray-900 mb-1">Automated Detection</h3>
									<p class="text-sm text-gray-600">
										Automatically scan your websites for WCAG compliance issues
									</p>
								</div>
							</div>

							<div class="flex gap-4">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-green-100">
										<svg class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
										</svg>
									</div>
								</div>
								<div>
									<h3 class="text-base font-semibold text-gray-900 mb-1">AI-Powered Fixes</h3>
									<p class="text-sm text-gray-600">
										Get intelligent code-level fixes applied automatically
									</p>
								</div>
							</div>

							<div class="flex gap-4">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-purple-100">
										<svg class="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
										</svg>
									</div>
								</div>
								<div>
									<h3 class="text-base font-semibold text-gray-900 mb-1">Interactive Chat</h3>
									<p class="text-sm text-gray-600">
										Ask questions and get expert guidance from our AI assistant
									</p>
								</div>
							</div>

							<div class="flex gap-4">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-orange-100">
										<svg class="w-5 h-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
										</svg>
									</div>
								</div>
								<div>
									<h3 class="text-base font-semibold text-gray-900 mb-1">No Addons Layover</h3>
									<p class="text-sm text-gray-600">
										Pure HTML remediation without intrusive overlays or widgets
									</p>
								</div>
							</div>

							<div class="flex gap-4">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-indigo-100">
										<svg class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
										</svg>
									</div>
								</div>
								<div>
									<h3 class="text-base font-semibold text-gray-900 mb-1">Data Privacy via Ethics</h3>
									<p class="text-sm text-gray-600">
										Ethics agreement ensures responsible use and data protection
									</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Right Column: How It Works -->
					<div>
						<h2 class="text-2xl font-bold text-gray-900 mb-6">
							How It Works
						</h2>
						<div class="space-y-6">
							<!-- Step 1 -->
							<div class="flex gap-3">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-bold text-sm">
										1
									</div>
								</div>
								<div>
									<h3 class="font-semibold text-gray-900 mb-1">Sign Up</h3>
									<p class="text-sm text-gray-600">
										Create your account with organization email
									</p>
								</div>
							</div>

							<!-- Step 2 -->
							<div class="flex gap-3">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-bold text-sm">
										2
									</div>
								</div>
								<div>
									<h3 class="font-semibold text-gray-900 mb-1">Accept Ethics Agreement</h3>
									<p class="text-sm text-gray-600">
										Review and accept our ethics agreement
									</p>
								</div>
							</div>

							<!-- Step 3 -->
							<div class="flex gap-3">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-bold text-sm">
										3
									</div>
								</div>
								<div>
									<h3 class="font-semibold text-gray-900 mb-1">Verify Domain</h3>
									<p class="text-sm text-gray-600">
										Add and verify your domain ownership
									</p>
								</div>
							</div>

							<!-- Step 4 -->
							<div class="flex gap-3">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-bold text-sm">
										4
									</div>
								</div>
								<div>
									<h3 class="font-semibold text-gray-900 mb-1">Register & Remediate</h3>
									<p class="text-sm text-gray-600">
										Add your website and start remediation
									</p>
								</div>
							</div>

							<!-- Step 5 -->
							<div class="flex gap-3">
								<div class="flex-shrink-0">
									<div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-bold text-sm">
										5
									</div>
								</div>
								<div>
									<h3 class="font-semibold text-gray-900 mb-1">View & Chat</h3>
									<p class="text-sm text-gray-600">
										Preview accessible site and ask AI questions
									</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>

	</main>

	<!-- Footer -->
	<Footer />
</div>
