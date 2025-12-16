// Ethics-required layout loader - checks ethics acceptance status
import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

const API = import.meta.env.VITE_API_BASE as string;

export const load: LayoutLoad = async ({ fetch, parent }) => {
	// Wait for parent layout to load (ensures authentication)
	await parent();

	try {
		// Check ethics acceptance status
		const response = await fetch(`${API}/api/ethics/status`, {
			credentials: 'include'
		});

		if (!response.ok) {
			throw new Error('Failed to check ethics status');
		}

		const data = await response.json();
		
		// If user hasn't accepted current version, redirect to ethics page
		if (!data.status?.has_accepted) {
			throw redirect(302, '/ethics');
		}

		return {
			ethicsAccepted: true
		};
	} catch (error) {
		// If it's already a redirect, re-throw it
		if (error instanceof Response && error.status === 302) {
			throw error;
		}
		
		// Otherwise redirect to ethics page
		throw redirect(302, '/ethics');
	}
};
