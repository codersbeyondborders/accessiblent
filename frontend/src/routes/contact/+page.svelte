<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import { toastStore } from '$lib/stores/toast';

	let formData = {
		name: '',
		email: '',
		subject: '',
		message: ''
	};

	let isSubmitting = false;

	async function handleSubmit(e: Event) {
		e.preventDefault();
		isSubmitting = true;

		// Simulate form submission
		await new Promise(resolve => setTimeout(resolve, 1000));

		toastStore.success('Thank you for your message! We will get back to you soon.');

		// Reset form
		formData = { name: '', email: '', subject: '', message: '' };
		isSubmitting = false;
	}
</script>

<svelte:head>
	<title>Contact Us - Accessify</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<Header showAuth={true} />

	<main class="flex-grow">
		<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
			<h1 class="text-4xl font-bold text-gray-900 mb-4">Contact Us</h1>
			<p class="text-gray-600 mb-8">
				Have questions or need support? We're here to help.
			</p>

			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
				<!-- Contact Information -->
				<div>
					<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
						<h2 class="text-2xl font-semibold text-gray-900 mb-4">Get in Touch</h2>
						<div class="space-y-4">
							<div class="flex items-start gap-3">
								<svg class="w-6 h-6 text-blue-600 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
								</svg>
								<div>
									<h3 class="font-semibold text-gray-900">Email</h3>
									<a href="mailto:support@accessify.com" class="text-blue-600 hover:underline">
										support@accessify.com
									</a>
								</div>
							</div>

							<div class="flex items-start gap-3">
								<svg class="w-6 h-6 text-blue-600 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<div>
									<h3 class="font-semibold text-gray-900">Support</h3>
									<p class="text-gray-600">
										For technical support and account issues
									</p>
								</div>
							</div>

							<div class="flex items-start gap-3">
								<svg class="w-6 h-6 text-blue-600 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
								</svg>
								<div>
									<h3 class="font-semibold text-gray-900">Sales</h3>
									<a href="mailto:sales@accessify.com" class="text-blue-600 hover:underline">
										sales@accessify.com
									</a>
								</div>
							</div>

							<div class="flex items-start gap-3">
								<svg class="w-6 h-6 text-blue-600 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
								</svg>
								<div>
									<h3 class="font-semibold text-gray-900">Privacy & Legal</h3>
									<a href="mailto:legal@accessify.com" class="text-blue-600 hover:underline">
										legal@accessify.com
									</a>
								</div>
							</div>
						</div>
					</div>

					<div class="bg-blue-50 rounded-lg p-6">
						<h3 class="font-semibold text-gray-900 mb-2">Need Help Getting Started?</h3>
						<p class="text-gray-700 mb-4">
							Check out our documentation and guides to learn how to use Accessify effectively.
						</p>
						<a 
							href="/signup" 
							class="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium"
						>
							Get Started
							<svg class="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
							</svg>
						</a>
					</div>
				</div>

				<!-- Contact Form -->
				<div class="bg-white rounded-lg shadow-sm p-8">
					<h2 class="text-2xl font-semibold text-gray-900 mb-4">Send Us a Message</h2>
					<form on:submit={handleSubmit} class="space-y-4">
						<div>
							<label for="name" class="block text-sm font-medium text-gray-700 mb-1">
								Name
							</label>
							<input
								type="text"
								id="name"
								bind:value={formData.name}
								required
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="Your name"
							/>
						</div>

						<div>
							<label for="email" class="block text-sm font-medium text-gray-700 mb-1">
								Email
							</label>
							<input
								type="email"
								id="email"
								bind:value={formData.email}
								required
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="your.email@example.com"
							/>
						</div>

						<div>
							<label for="subject" class="block text-sm font-medium text-gray-700 mb-1">
								Subject
							</label>
							<input
								type="text"
								id="subject"
								bind:value={formData.subject}
								required
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="How can we help?"
							/>
						</div>

						<div>
							<label for="message" class="block text-sm font-medium text-gray-700 mb-1">
								Message
							</label>
							<textarea
								id="message"
								bind:value={formData.message}
								required
								rows="6"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
								placeholder="Tell us more about your inquiry..."
							></textarea>
						</div>

						<button
							type="submit"
							disabled={isSubmitting}
							class="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
						>
							{isSubmitting ? 'Sending...' : 'Send Message'}
						</button>
					</form>
				</div>
			</div>
		</div>
	</main>

	<Footer />
</div>
