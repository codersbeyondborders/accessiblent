<script lang="ts">
	import Header from '$lib/components/Header.svelte';
	import Footer from '$lib/components/Footer.svelte';
</script>

<svelte:head>
	<title>Terms of Service - Accessify</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<Header showAuth={true} />

	<main class="flex-grow">
		<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
			<h1 class="text-4xl font-bold text-gray-900 mb-4">Terms of Service</h1>
			<p class="text-gray-600 mb-8">Last Updated: December 15, 2025</p>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
				<p class="text-gray-700">
					By accessing or using Accessify's services, you agree to be bound by these Terms of Service 
					and our Privacy Policy. If you do not agree to these terms, you may not use our services.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">2. Description of Service</h2>
				<p class="text-gray-700 mb-4">
					Accessify provides an AI-powered platform for detecting and remediating web accessibility issues. 
					Our services include:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Automated accessibility scanning and analysis</li>
					<li>AI-generated remediation recommendations and code fixes</li>
					<li>Interactive accessibility assistance through our AI chat agent</li>
					<li>Domain verification and management tools</li>
					<li>Website registration and monitoring capabilities</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">3. Account Registration</h2>
				<p class="text-gray-700 mb-4">
					To use our services, you must:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Provide accurate and complete registration information</li>
					<li>Use a valid organization email address</li>
					<li>Maintain the security of your account credentials</li>
					<li>Verify your email address</li>
					<li>Accept our Ethics Agreement before using remediation features</li>
					<li>Be at least 18 years of age</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">4. Domain Verification</h2>
				<p class="text-gray-700 mb-4">
					Before registering websites for remediation, you must:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Verify ownership of the domain through DNS TXT records or meta tags</li>
					<li>Have authorization to modify the websites you register</li>
					<li>Ensure your email domain matches or is authorized for the registered domains</li>
				</ul>
				<p class="text-gray-700 mt-4">
					You are solely responsible for ensuring you have proper authorization to use our services 
					on any domain or website.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">5. Ethics Agreement</h2>
				<p class="text-gray-700 mb-4">
					By using our remediation services, you agree to:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Use our services only for legitimate accessibility improvement purposes</li>
					<li>Not use our services to harm, deceive, or exploit users</li>
					<li>Review and test all AI-generated fixes before deploying to production</li>
					<li>Maintain responsibility for the final implementation and quality of fixes</li>
					<li>Comply with all applicable accessibility laws and regulations</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">6. Acceptable Use</h2>
				<p class="text-gray-700 mb-4">You agree not to:</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Use our services for any illegal or unauthorized purpose</li>
					<li>Attempt to gain unauthorized access to our systems or other users' accounts</li>
					<li>Interfere with or disrupt our services or servers</li>
					<li>Use automated tools to access our services without permission</li>
					<li>Reverse engineer or attempt to extract our AI models or algorithms</li>
					<li>Register domains or websites you do not own or have authorization to modify</li>
					<li>Violate any applicable laws or regulations</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">7. Intellectual Property</h2>
				<p class="text-gray-700 mb-4">
					Accessify retains all rights to our platform, software, AI models, and related intellectual property. 
					You retain ownership of your website content and data.
				</p>
				<p class="text-gray-700">
					We grant you a limited, non-exclusive, non-transferable license to use our services in accordance 
					with these terms.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">8. AI-Generated Content</h2>
				<p class="text-gray-700 mb-4">
					Our services use AI to generate accessibility fixes and recommendations. You acknowledge that:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>AI-generated content may contain errors or inaccuracies</li>
					<li>You are responsible for reviewing and testing all fixes before implementation</li>
					<li>We do not guarantee that fixes will resolve all accessibility issues</li>
					<li>Final responsibility for website accessibility remains with you</li>
				</ul>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">9. Disclaimers and Limitations</h2>
				<p class="text-gray-700 mb-4">
					Our services are provided "as is" without warranties of any kind. We do not guarantee:
				</p>
				<ul class="list-disc list-inside text-gray-700 space-y-2">
					<li>Complete WCAG compliance or accessibility certification</li>
					<li>Uninterrupted or error-free service</li>
					<li>That our services will meet all your requirements</li>
					<li>The accuracy or completeness of AI-generated recommendations</li>
				</ul>
				<p class="text-gray-700 mt-4">
					To the maximum extent permitted by law, we shall not be liable for any indirect, incidental, 
					special, or consequential damages arising from your use of our services.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">10. Termination</h2>
				<p class="text-gray-700">
					We reserve the right to suspend or terminate your account if you violate these terms or engage 
					in conduct we deem harmful to our services or other users. You may terminate your account at 
					any time through your account settings.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">11. Changes to Terms</h2>
				<p class="text-gray-700">
					We may modify these terms at any time. We will notify you of significant changes via email 
					or through our platform. Continued use of our services after changes constitutes acceptance 
					of the modified terms.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8 mb-6">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">12. Governing Law</h2>
				<p class="text-gray-700">
					These terms shall be governed by and construed in accordance with applicable laws, without 
					regard to conflict of law principles.
				</p>
			</div>

			<div class="bg-white rounded-lg shadow-sm p-8">
				<h2 class="text-2xl font-semibold text-gray-900 mb-4">13. Contact Information</h2>
				<p class="text-gray-700 mb-4">
					For questions about these Terms of Service, please contact us:
				</p>
				<p class="text-gray-700">
					Email: <a href="mailto:legal@accessify.com" class="text-blue-600 hover:underline">legal@accessify.com</a>
				</p>
			</div>
		</div>
	</main>

	<Footer />
</div>
