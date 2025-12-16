// Protected layout loader - checks authentication status
import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

const API = import.meta.env.VITE_API_BASE as string;

export const load: LayoutLoad = async ({ fetch, url }) => {
	try {
		// Check authentication status
		const response = await fetch(`${API}/api/auth/me`, {
			credentials: 'include'
		});

		if (!response.ok) {
			// Not authenticated, redirect to login
			throw redirect(302, `/login?redirect=${encodeURIComponent(url.pathname)}`);
		}

		const data = await response.json();
		const user = data.user || data;

		return {
			user
		};
	} catch (error) {
		// If it's already a redirect, re-throw it
		if (error instanceof Response && error.status === 302) {
			throw error;
		}
		
		// Otherwise redirect to login
		throw redirect(302, `/login?redirect=${encodeURIComponent(url.pathname)}`);
	}
};
