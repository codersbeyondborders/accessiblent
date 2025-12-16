<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
</script>

<svelte:head>
	<title>Privacy Policy - Accessify</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<Header showAuth={true} />

	<main class="flex-grow">
		<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
			<h1 class="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
			<p class="text-gray-600 mb-8">Last Updated: December 15, 2025</p>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Introduction</h2>
				<p class="text-gray-700">
					Accessify ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy 
					explains how we collect, use, disclose, and safeguard your information when you use our accessibility 
					remediation platform.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Information We Collect</h2>
				
				<h3 class="text-xl font-semibold text-gray-900 mb-3 mt-4">Account Information</h3>
				<p class="text-gray-700 mb-4">
					When you create an account, we collect:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2 mb-4">
					<li>Email address and organization email domain</li>
					<li>Name and organization details</li>
					<li>Password (encrypted and securely stored)</li>
					<li>Account preferences and settings</li>
				</ul>

				<h3 class="text-xl font-semibold text-gray-900 mb-3 mt-4">Website Data</h3>
				<p class="text-gray-700 mb-4">
					To provide our services, we collect:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2 mb-4">
					<li>Domain names and website URLs you register</li>
					<li>Website content and HTML structure for accessibility analysis</li>
					<li>Accessibility scan results and remediation data</li>
					<li>Chat interactions with our AI assistant</li>
				</ul>

				<h3 class="text-xl font-semibold text-gray-900 mb-3 mt-4">Usage Information</h3>
				<p class="text-gray-700 mb-4">
					We automatically collect:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Log data (IP address, browser type, access times)</li>
					<li>Device information and operating system</li>
					<li>Usage patterns and feature interactions</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">How We Use Your Information</h2>
				<p class="text-gray-700 mb-4">We use collected information to:</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Provide and maintain our accessibility remediation services</li>
					<li>Verify domain ownership and authenticate users</li>
					<li>Analyze website accessibility and generate remediation recommendations</li>
					<li>Improve our AI models and detection capabilities</li>
					<li>Send service-related notifications and updates</li>
					<li>Respond to support requests and communications</li>
					<li>Detect and prevent fraud or security issues</li>
					<li>Comply with legal obligations</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Data Sharing and Disclosure</h2>
				<p class="text-gray-700 mb-4">
					We do not sell your personal information. We may share your information only in these circumstances:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li><strong>Service Providers:</strong> Third-party vendors who assist in operating our platform</li>
					<li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
					<li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
					<li><strong>With Your Consent:</strong> When you explicitly authorize sharing</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Data Security</h2>
				<p class="text-gray-700 mb-4">
					We implement industry-standard security measures to protect your information:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Encryption of data in transit and at rest</li>
					<li>Secure password hashing with bcrypt</li>
					<li>Domain verification to prevent unauthorized access</li>
					<li>Regular security audits and updates</li>
					<li>Access controls and authentication mechanisms</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Your Rights</h2>
				<p class="text-gray-700 mb-4">You have the right to:</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Access and review your personal information</li>
					<li>Request correction of inaccurate data</li>
					<li>Request deletion of your account and data</li>
					<li>Opt-out of marketing communications</li>
					<li>Export your data in a portable format</li>
					<li>Object to certain data processing activities</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Data Retention</h2>
				<p class="text-gray-700">
					We retain your information for as long as your account is active or as needed to provide services. 
					When you delete your account, we will delete or anonymize your personal information within 30 days, 
					except where retention is required by law.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Cookies and Tracking</h2>
				<p class="text-gray-700">
					We use cookies and similar technologies to maintain sessions, remember preferences, and analyze usage. 
					You can control cookie settings through your browser preferences.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Children's Privacy</h2>
				<p class="text-gray-700">
					Our services are not intended for users under 18 years of age. We do not knowingly collect 
					information from children.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">Contact Us</h2>
				<p class="text-gray-700 mb-4">
					If you have questions about this Privacy Policy or our data practices, please contact us:
				</p>
				<p class="text-gray-700">
					Email: <a href="mailto:privacy@accessify.com" class="text-blue-600 hover:underline">privacy@accessify.com</a>
				</p>
			</div>
		</div>
	</main>

	<Footer />
</div>
