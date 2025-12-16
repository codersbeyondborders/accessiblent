// Toast notification store for displaying global messages

import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
	id: string;
	type: ToastType;
	message: string;
	duration?: number;
}

interface ToastStore {
	toasts: Toast[];
}

function createToastStore() {
	const { subscribe, update } = writable<ToastStore>({ toasts: [] });
	
	let idCounter = 0;
	
	function addToast(type: ToastType, message: string, duration = 5000) {
		const id = `toast-${++idCounter}`;
		const toast: Toast = { id, type, message, duration };
		
		update(store => ({
			toasts: [...store.toasts, toast]
		}));
		
		// Auto-remove after duration
		if (duration > 0) {
			setTimeout(() => {
				removeToast(id);
			}, duration);
		}
		
		return id;
	}
	
	function removeToast(id: string) {
		update(store => ({
			toasts: store.toasts.filter(t => t.id !== id)
		}));
	}
	
	return {
		subscribe,
		success: (message: string, duration?: number) => addToast('success', message, duration),
		error: (message: string, duration?: number) => addToast('error', message, duration),
		warning: (message: string, duration?: number) => addToast('warning', message, duration),
		info: (message: string, duration?: number) => addToast('info', message, duration),
		remove: removeToast,
		clear: () => update(() => ({ toasts: [] }))
	};
}

export const toastStore = createToastStore();
