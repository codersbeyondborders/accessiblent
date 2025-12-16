<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
</script>

<svelte:head>
	<title>About Us - Accessify</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<Header showAuth={true} />

	<main class="flex-grow">
		<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
			<h1 class="text-4xl font-bold text-gray-900 mb-8">About Accessify</h1>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-8">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Our Mission</h2>
				<p class="text-gray-700 mb-4">
					At Accessify, we believe the web should be accessible to everyone, regardless of their abilities. 
					Our mission is to make web accessibility simple, automated, and achievable for organizations of all sizes.
				</p>
				<p class="text-gray-700">
					We leverage cutting-edge AI technology to detect and remediate accessibility issues, helping you create 
					inclusive digital experiences that comply with WCAG standards and reach a wider audience.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-8">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">What We Do</h2>
				<p class="text-gray-700 mb-4">
					Accessify is an AI-powered accessibility agent that automatically scans your websites for 
					accessibility barriers and provides intelligent remediation solutions. Our platform:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2 mb-4">
					<li>Detects WCAG compliance issues across your web properties</li>
					<li>Generates code-level fixes for accessibility problems</li>
					<li>Provides an interactive AI assistant for accessibility guidance</li>
					<li>Offers domain verification to ensure secure access control</li>
					<li>Maintains ethical standards through our Ethics Agreement framework</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-8">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Why Accessibility Matters</h2>
				<p class="text-gray-700 mb-4">
					Over 1 billion people worldwide live with some form of disability. Web accessibility isn't just 
					about compliance—it's about creating equal access to information, services, and opportunities for everyone.
				</p>
				<p class="text-gray-700">
					By making your website accessible, you expand your reach, improve user experience for all visitors, 
					enhance SEO, and demonstrate your commitment to inclusivity and social responsibility.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Our Commitment</h2>
				<p class="text-gray-700 mb-4">
					We're committed to maintaining the highest standards of security, privacy, and ethical AI use. 
					Our platform requires domain verification to ensure only authorized users can modify websites, 
					and we require acceptance of our Ethics Agreement to promote responsible use of our technology.
				</p>
				<p class="text-gray-700">
					We continuously improve our AI models and detection capabilities to stay current with evolving 
					accessibility standards and best practices.
				</p>
			</div>
		</div>
	</main>

	<Footer />
</div>
