// Error handling utilities for API responses and field-specific errors

/**
 * Standard API error response structure
 */
export interface ApiError {
	error?: {
		code?: string;
		message: string;
		details?: {
			field?: string;
			[key: string]: unknown;
		};
	};
	detail?: string;
	message?: string;
}

/**
 * Field-specific error map
 */
export type FieldErrors = Record<string, string>;

/**
 * Parse API error response and extract error message
 * @param response - Fetch Response object
 * @returns Promise resolving to error message string
 */
export async function parseApiError(response: Response): Promise<string> {
	try {
		const data: ApiError = await response.json();
		
		// Try to extract error message from various possible structures
		if (data.error?.message) {
			return data.error.message;
		}
		
		if (data.detail) {
			return data.detail;
		}
		
		if (data.message) {
			return data.message;
		}
		
		// Fallback to status text
		return response.statusText || 'An error occurred';
	} catch {
		// If JSON parsing fails, return status text
		return response.statusText || 'An error occurred';
	}
}

/**
 * Parse API error response and extract field-specific errors
 * @param response - Fetch Response object
 * @returns Promise resolving to FieldErrors object
 */
export async function parseFieldErrors(response: Response): Promise<FieldErrors> {
	try {
		const data: ApiError = await response.json();
		const fieldErrors: FieldErrors = {};
		
		// Check if there's a field-specific error
		if (data.error?.details?.field && data.error?.message) {
			fieldErrors[data.error.details.field] = data.error.message;
		}
		
		return fieldErrors;
	} catch {
		return {};
	}
}

/**
 * Handle API response and extract errors
 * @param response - Fetch Response object
 * @returns Promise resolving to object with error message and field errors
 */
export async function handleApiError(response: Response): Promise<{
	message: string;
	fieldErrors: FieldErrors;
}> {
	try {
		const data: ApiError = await response.json();
		const fieldErrors: FieldErrors = {};
		let message = '';
		
		// Extract field-specific error
		if (data.error?.details?.field && data.error?.message) {
			fieldErrors[data.error.details.field] = data.error.message;
		}
		
		// Extract general error message
		if (data.error?.message) {
			message = data.error.message;
		} else if (data.detail) {
			message = data.detail;
		} else if (data.message) {
			message = data.message;
		} else {
			message = response.statusText || 'An error occurred';
		}
		
		return { message, fieldErrors };
	} catch {
		return {
			message: response.statusText || 'An error occurred',
			fieldErrors: {}
		};
	}
}

/**
 * Get user-friendly error message for network errors
 * @param error - Error object
 * @returns User-friendly error message
 */
export function getNetworkErrorMessage(error: unknown): string {
	if (error instanceof TypeError && error.message.includes('fetch')) {
		return 'Network error. Please check your connection and try again.';
	}
	
	if (error instanceof Error) {
		return error.message;
	}
	
	return 'An unexpected error occurred. Please try again.';
}

/**
 * Get user-friendly error message based on HTTP status code
 * @param status - HTTP status code
 * @returns User-friendly error message
 */
export function getStatusErrorMessage(status: number): string {
	switch (status) {
		case 400:
			return 'Invalid request. Please check your input.';
		case 401:
			return 'Authentication required. Please sign in.';
		case 403:
			return 'Access denied. You do not have permission to perform this action.';
		case 404:
			return 'Resource not found.';
		case 409:
			return 'Conflict. This resource already exists.';
		case 422:
			return 'Validation error. Please check your input.';
		case 429:
			return 'Too many requests. Please try again later.';
		case 500:
			return 'Server error. Please try again later.';
		case 502:
		case 503:
			return 'Service temporarily unavailable. Please try again later.';
		case 504:
			return 'Request timeout. Please try again.';
		default:
			return 'An error occurred. Please try again.';
	}
}
