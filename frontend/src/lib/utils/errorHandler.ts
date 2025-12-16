// Global error handler utilities

/**
 * Log error in development mode
 * @param error - Error to log
 * @param context - Additional context
 */
export function logError(error: unknown, context?: string): void {
	if (import.meta.env.DEV) {
		console.error(`[Error${context ? ` - ${context}` : ''}]:`, error);
		
		if (error instanceof Error && error.stack) {
			console.error('Stack trace:', error.stack);
		}
	}
}

/**
 * Handle unhandled promise rejections
 */
export function setupGlobalErrorHandlers(): void {
	// Handle unhandled promise rejections
	window.addEventListener('unhandledrejection', (event) => {
		logError(event.reason, 'Unhandled Promise Rejection');
		
		// Prevent default browser error handling
		event.preventDefault();
	});
	
	// Handle global errors
	window.addEventListener('error', (event) => {
		logError(event.error || event.message, 'Global Error');
	});
}

/**
 * Wrap async function with error handling
 * @param fn - Async function to wrap
 * @param onError - Error callback
 * @returns Wrapped function
 */
export function withErrorHandling<T extends (...args: unknown[]) => Promise<unknown>>(
	fn: T,
	onError?: (error: unknown) => void
): T {
	return (async (...args: Parameters<T>) => {
		try {
			return await fn(...args);
		} catch (error) {
			logError(error, fn.name);
			if (onError) {
				onError(error);
			}
			throw error;
		}
	}) as T;
}

/**
 * Safe JSON parse with error handling
 * @param json - JSON string to parse
 * @param fallback - Fallback value if parsing fails
 * @returns Parsed object or fallback
 */
export function safeJsonParse<T>(json: string, fallback: T): T {
	try {
		return JSON.parse(json) as T;
	} catch (error) {
		logError(error, 'JSON Parse Error');
		return fallback;
	}
}

/**
 * Safe localStorage access with error handling
 * @param key - Storage key
 * @param fallback - Fallback value if access fails
 * @returns Stored value or fallback
 */
export function safeLocalStorageGet<T>(key: string, fallback: T): T {
	try {
		const item = localStorage.getItem(key);
		if (item === null) return fallback;
		return JSON.parse(item) as T;
	} catch (error) {
		logError(error, 'LocalStorage Get Error');
		return fallback;
	}
}

/**
 * Safe localStorage set with error handling
 * @param key - Storage key
 * @param value - Value to store
 * @returns True if successful
 */
export function safeLocalStorageSet(key: string, value: unknown): boolean {
	try {
		localStorage.setItem(key, JSON.stringify(value));
		return true;
	} catch (error) {
		logError(error, 'LocalStorage Set Error');
		return false;
	}
}

/**
 * Safe localStorage remove with error handling
 * @param key - Storage key
 * @returns True if successful
 */
export function safeLocalStorageRemove(key: string): boolean {
	try {
		localStorage.removeItem(key);
		return true;
	} catch (error) {
		logError(error, 'LocalStorage Remove Error');
		return false;
	}
}
