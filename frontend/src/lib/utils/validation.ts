// Form validation utilities

/**
 * Public email domains that should be rejected for organizational signup
 */
export const PUBLIC_EMAIL_DOMAINS = new Set([
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

/**
 * Validation result
 */
export interface ValidationResult {
	valid: boolean;
	error?: string;
}

/**
 * Validate email format
 * @param email - Email address to validate
 * @returns Validation result
 */
export function validateEmail(email: string): ValidationResult {
	if (!email) {
		return { valid: false, error: 'Email is required' };
	}
	
	// Basic email format validation
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	if (!emailRegex.test(email)) {
		return { valid: false, error: 'Please enter a valid email address' };
	}
	
	return { valid: true };
}

/**
 * Validate email domain (check if it's not a public provider)
 * @param email - Email address to validate
 * @returns Validation result
 */
export function validateEmailDomain(email: string): ValidationResult {
	const emailValidation = validateEmail(email);
	if (!emailValidation.valid) {
		return emailValidation;
	}
	
	const domain = email.split('@')[1]?.toLowerCase().trim();
	
	if (!domain) {
		return { valid: false, error: 'Invalid email format' };
	}
	
	if (PUBLIC_EMAIL_DOMAINS.has(domain)) {
		return {
			valid: false,
			error: 'Please use your organization email address, not a public email provider'
		};
	}
	
	return { valid: true };
}

/**
 * Validate URL format
 * @param url - URL to validate
 * @returns Validation result
 */
export function validateUrl(url: string): ValidationResult {
	if (!url) {
		return { valid: false, error: 'URL is required' };
	}
	
	try {
		const urlObj = new URL(url);
		
		// Check if protocol is http or https
		if (!['http:', 'https:'].includes(urlObj.protocol)) {
			return { valid: false, error: 'URL must use HTTP or HTTPS protocol' };
		}
		
		// Check if hostname exists
		if (!urlObj.hostname) {
			return { valid: false, error: 'URL must include a valid domain' };
		}
		
		return { valid: true };
	} catch {
		return { valid: false, error: 'Please enter a valid URL (e.g., https://example.com)' };
	}
}

/**
 * Validate domain format
 * @param domain - Domain to validate
 * @returns Validation result
 */
export function validateDomain(domain: string): ValidationResult {
	if (!domain) {
		return { valid: false, error: 'Domain is required' };
	}
	
	// Remove protocol if present
	let cleanDomain = domain.toLowerCase().trim();
	cleanDomain = cleanDomain.replace(/^https?:\/\//, '');
	cleanDomain = cleanDomain.replace(/^www\./, '');
	cleanDomain = cleanDomain.split('/')[0]; // Remove path
	
	// Basic domain format validation
	const domainRegex = /^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$/;
	
	if (!domainRegex.test(cleanDomain)) {
		return { valid: false, error: 'Please enter a valid domain (e.g., example.com)' };
	}
	
	// Check if domain has at least one dot
	if (!cleanDomain.includes('.')) {
		return { valid: false, error: 'Domain must include a top-level domain (e.g., .com, .org)' };
	}
	
	return { valid: true };
}

/**
 * Validate required field
 * @param value - Value to validate
 * @param fieldName - Name of the field for error message
 * @returns Validation result
 */
export function validateRequired(value: string, fieldName: string): ValidationResult {
	if (!value || value.trim() === '') {
		return { valid: false, error: `${fieldName} is required` };
	}
	
	return { valid: true };
}

/**
 * Validate password strength
 * @param password - Password to validate
 * @param minLength - Minimum password length (default: 8)
 * @returns Validation result
 */
export function validatePassword(password: string, minLength = 8): ValidationResult {
	if (!password) {
		return { valid: false, error: 'Password is required' };
	}
	
	if (password.length < minLength) {
		return { valid: false, error: `Password must be at least ${minLength} characters` };
	}
	
	return { valid: true };
}

/**
 * Validate password confirmation
 * @param password - Original password
 * @param confirmPassword - Confirmation password
 * @returns Validation result
 */
export function validatePasswordConfirmation(
	password: string,
	confirmPassword: string
): ValidationResult {
	if (!confirmPassword) {
		return { valid: false, error: 'Please confirm your password' };
	}
	
	if (password !== confirmPassword) {
		return { valid: false, error: 'Passwords do not match' };
	}
	
	return { valid: true };
}

/**
 * Extract domain from URL
 * @param url - URL to extract domain from
 * @returns Domain string or null if invalid
 */
export function extractDomain(url: string): string | null {
	try {
		const urlObj = new URL(url);
		return urlObj.hostname;
	} catch {
		return null;
	}
}

/**
 * Normalize domain (remove protocol, www, and path)
 * @param domain - Domain to normalize
 * @returns Normalized domain
 */
export function normalizeDomain(domain: string): string {
	let normalized = domain.toLowerCase().trim();
	normalized = normalized.replace(/^https?:\/\//, '');
	normalized = normalized.replace(/^www\./, '');
	normalized = normalized.split('/')[0];
	return normalized;
}

/**
 * Check if URL matches domain
 * @param url - URL to check
 * @param domain - Domain to match against
 * @returns True if URL matches domain
 */
export function urlMatchesDomain(url: string, domain: string): boolean {
	const urlDomain = extractDomain(url);
	if (!urlDomain) return false;
	
	const normalizedUrlDomain = normalizeDomain(urlDomain);
	const normalizedDomain = normalizeDomain(domain);
	
	return normalizedUrlDomain === normalizedDomain;
}
