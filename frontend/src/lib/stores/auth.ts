// auth.ts - Authentication store for managing user state and session
import { writable, derived } from 'svelte/store';
import { goto } from '$app/navigation';

const API = import.meta.env.VITE_API_BASE as string;

// User type definition
export interface User {
	id: number;
	organization_id: number;
	email: string;
	full_name: string;
	is_verified: boolean;
	organization_name?: string;
}

// Auth state interface
interface AuthState {
	user: User | null;
	loading: boolean;
	error: string | null;
}

// Create the auth store
function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>({
		user: null,
		loading: false,
		error: null
	});

	return {
		subscribe,

		/**
		 * Check if user is authenticated by calling /api/auth/me
		 */
		async checkAuth(): Promise<boolean> {
			update((state) => ({ ...state, loading: true, error: null }));

			try {
				const response = await fetch(`${API}/api/auth/me`, {
					method: 'GET',
					credentials: 'include' // Include cookies
				});

				if (response.ok) {
					const data = await response.json();
					const user = data.user || data; // Handle both {user: ...} and direct user object
					update((state) => ({ ...state, user, loading: false }));
					return true;
				} else {
					update((state) => ({ ...state, user: null, loading: false }));
					return false;
				}
			} catch (error) {
				update((state) => ({
					...state,
					user: null,
					loading: false,
					error: error instanceof Error ? error.message : 'Failed to check authentication'
				}));
				return false;
			}
		},

		/**
		 * Login with email and password
		 */
		async login(email: string, password: string): Promise<{ success: boolean; error?: string }> {
			update((state) => ({ ...state, loading: true, error: null }));

			try {
				const response = await fetch(`${API}/api/auth/login`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					credentials: 'include', // Include cookies
					body: JSON.stringify({ email, password })
				});

				if (response.ok) {
					const data = await response.json();
					const user = data.user || data; // Handle both {user: ...} and direct user object
					update((state) => ({ ...state, user, loading: false }));
					return { success: true };
				} else {
					const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
					// Handle different error response formats
					let errorMessage = 'Login failed';
					if (typeof errorData.detail === 'string') {
						errorMessage = errorData.detail;
					} else if (typeof errorData.detail === 'object' && errorData.detail?.message) {
						errorMessage = errorData.detail.message;
					} else if (errorData.message) {
						errorMessage = errorData.message;
					} else if (errorData.error?.message) {
						errorMessage = errorData.error.message;
					}
					update((state) => ({ ...state, loading: false, error: errorMessage }));
					return { success: false, error: errorMessage };
				}
			} catch (error) {
				const errorMessage = error instanceof Error ? error.message : 'Network error';
				update((state) => ({ ...state, loading: false, error: errorMessage }));
				return { success: false, error: errorMessage };
			}
		},

		/**
		 * Logout the current user
		 */
		async logout(): Promise<void> {
			update((state) => ({ ...state, loading: true }));

			try {
				await fetch(`${API}/api/auth/logout`, {
					method: 'POST',
					credentials: 'include' // Include cookies
				});
			} catch (error) {
				console.error('Logout error:', error);
			} finally {
				// Clear user state regardless of API response
				set({ user: null, loading: false, error: null });
				goto('/login');
			}
		},

		/**
		 * Clear error message
		 */
		clearError(): void {
			update((state) => ({ ...state, error: null }));
		},

		/**
		 * Set loading state
		 */
		setLoading(loading: boolean): void {
			update((state) => ({ ...state, loading }));
		}
	};
}

// Export the auth store instance
export const authStore = createAuthStore();

// Derived store for checking if user is authenticated
export const isAuthenticated = derived(authStore, ($auth) => $auth.user !== null);

// Derived store for checking if loading
export const isLoading = derived(authStore, ($auth) => $auth.loading);
