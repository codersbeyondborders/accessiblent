# Error Handling and Validation Utilities

This directory contains utilities for error handling, validation, and toast notifications.

## Error Handling (`errors.ts`)

Utilities for parsing and handling API errors.

### Usage Examples

```typescript
import { handleApiError, parseApiError, getNetworkErrorMessage } from '$lib/utils/errors';

// Handle API response with both general and field-specific errors
async function submitForm() {
  try {
    const response = await fetch('/api/endpoint', { method: 'POST', body: data });
    
    if (!response.ok) {
      const { message, fieldErrors } = await handleApiError(response);
      
      // Set general error
      error = message;
      
      // Set field-specific errors
      if (Object.keys(fieldErrors).length > 0) {
        fieldErrors = fieldErrors;
      }
    }
  } catch (err) {
    error = getNetworkErrorMessage(err);
  }
}

// Parse just the error message
async function simpleErrorHandling() {
  const response = await fetch('/api/endpoint');
  if (!response.ok) {
    const errorMessage = await parseApiError(response);
    console.error(errorMessage);
  }
}
```

## Form Validation (`validation.ts`)

Utilities for validating form inputs.

### Usage Examples

```typescript
import {
  validateEmail,
  validateEmailDomain,
  validateUrl,
  validateDomain,
  validateRequired,
  validatePassword,
  validatePasswordConfirmation,
  urlMatchesDomain
} from '$lib/utils/validation';

// Validate email format
const emailResult = validateEmail('user@example.com');
if (!emailResult.valid) {
  console.error(emailResult.error);
}

// Validate email domain (reject public providers)
const domainResult = validateEmailDomain('user@gmail.com');
if (!domainResult.valid) {
  console.error(domainResult.error); // "Please use your organization email..."
}

// Validate URL
const urlResult = validateUrl('https://example.com/path');
if (!urlResult.valid) {
  console.error(urlResult.error);
}

// Validate domain
const domainValidation = validateDomain('example.com');
if (!domainValidation.valid) {
  console.error(domainValidation.error);
}

// Validate required field
const nameResult = validateRequired(fullName, 'Full name');
if (!nameResult.valid) {
  console.error(nameResult.error); // "Full name is required"
}

// Validate password
const passwordResult = validatePassword(password, 8);
if (!passwordResult.valid) {
  console.error(passwordResult.error);
}

// Validate password confirmation
const confirmResult = validatePasswordConfirmation(password, confirmPassword);
if (!confirmResult.valid) {
  console.error(confirmResult.error); // "Passwords do not match"
}

// Check if URL matches domain
const matches = urlMatchesDomain('https://example.com/page', 'example.com');
console.log(matches); // true
```

## Toast Notifications (`toast.ts`)

Global toast notification system for displaying messages.

### Usage Examples

```typescript
import { toastStore } from '$lib/stores/toast';

// Show success message
toastStore.success('Account created successfully!');

// Show error message
toastStore.error('Failed to save changes');

// Show warning message
toastStore.warning('Your session will expire soon');

// Show info message
toastStore.info('New features available');

// Custom duration (default is 5000ms)
toastStore.success('Saved!', 3000);

// Remove specific toast
const id = toastStore.error('Error occurred');
toastStore.remove(id);

// Clear all toasts
toastStore.clear();
```

The Toast component is automatically included in the root layout, so toasts will appear globally.

## Error Boundaries

### ErrorBoundary Component

Wrap components that might throw errors:

```svelte
<script>
  import ErrorBoundary from '$lib/components/ErrorBoundary.svelte';
</script>

<ErrorBoundary fallback="Failed to load this section">
  <MyComponent />
</ErrorBoundary>

<!-- With custom error details -->
<ErrorBoundary 
  fallback="Failed to load data" 
  showDetails={true}
>
  <DataComponent />
</ErrorBoundary>
```

### Global Error Handlers

Global error handlers are automatically set up in the root layout. They catch:
- Unhandled promise rejections
- Global JavaScript errors

### Error Page

The `+error.svelte` page handles route-level errors (404, 403, 401, 500, etc.).

## Error Handler Utilities (`errorHandler.ts`)

Additional utilities for error handling.

### Usage Examples

```typescript
import {
  logError,
  withErrorHandling,
  safeJsonParse,
  safeLocalStorageGet,
  safeLocalStorageSet
} from '$lib/utils/errorHandler';

// Log errors in development
logError(error, 'API Call Failed');

// Wrap async functions with error handling
const safeApiCall = withErrorHandling(
  async () => {
    const response = await fetch('/api/data');
    return response.json();
  },
  (error) => {
    toastStore.error('Failed to fetch data');
  }
);

// Safe JSON parsing
const data = safeJsonParse(jsonString, { default: 'value' });

// Safe localStorage access
const user = safeLocalStorageGet('user', null);
safeLocalStorageSet('settings', { theme: 'dark' });
safeLocalStorageRemove('temp-data');
```

## Complete Form Example

Here's a complete example of a form with validation and error handling:

```svelte
<script lang="ts">
  import { toastStore } from '$lib/stores/toast';
  import { handleApiError } from '$lib/utils/errors';
  import { validateEmail, validateRequired } from '$lib/utils/validation';
  
  let email = '';
  let name = '';
  let loading = false;
  let error = '';
  let fieldErrors: Record<string, string> = {};
  
  function validateForm(): boolean {
    fieldErrors = {};
    
    const nameValidation = validateRequired(name, 'Name');
    if (!nameValidation.valid) {
      fieldErrors.name = nameValidation.error!;
    }
    
    const emailValidation = validateEmail(email);
    if (!emailValidation.valid) {
      fieldErrors.email = emailValidation.error!;
    }
    
    return Object.keys(fieldErrors).length === 0;
  }
  
  async function handleSubmit() {
    error = '';
    
    if (!validateForm()) {
      return;
    }
    
    loading = true;
    
    try {
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name })
      });
      
      if (response.ok) {
        toastStore.success('Form submitted successfully!');
        // Reset form
        email = '';
        name = '';
      } else {
        const { message, fieldErrors: apiFieldErrors } = await handleApiError(response);
        error = message;
        fieldErrors = { ...fieldErrors, ...apiFieldErrors };
      }
    } catch (err) {
      error = 'Network error. Please try again.';
      toastStore.error(error);
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  {#if error}
    <div class="error-banner">{error}</div>
  {/if}
  
  <div>
    <label for="name">Name</label>
    <input
      id="name"
      bind:value={name}
      class:error={fieldErrors.name}
    />
    {#if fieldErrors.name}
      <span class="error-text">{fieldErrors.name}</span>
    {/if}
  </div>
  
  <div>
    <label for="email">Email</label>
    <input
      id="email"
      type="email"
      bind:value={email}
      class:error={fieldErrors.email}
    />
    {#if fieldErrors.email}
      <span class="error-text">{fieldErrors.email}</span>
    {/if}
  </div>
  
  <button type="submit" disabled={loading}>
    {loading ? 'Submitting...' : 'Submit'}
  </button>
</form>
```

## Best Practices

1. **Always validate on the client side** before making API calls
2. **Handle both field-specific and general errors** from the API
3. **Use toast notifications** for success messages and non-critical errors
4. **Display inline errors** for form field validation
5. **Wrap risky components** in ErrorBoundary
6. **Log errors in development** for debugging
7. **Provide user-friendly error messages** instead of technical details
8. **Always handle network errors** separately from API errors
