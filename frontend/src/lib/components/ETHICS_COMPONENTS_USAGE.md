# Ethics Agreement Components Usage Guide

This document describes how to use the ethics agreement components implemented for task 15.

## Components Overview

### 1. Ethics Agreement Page (`/ethics`)
**Location:** `frontend/src/routes/ethics/+page.svelte`  
**Requirements:** 3.1, 3.2, 3.3

A standalone page where users can view and accept the ethics agreement.

**Features:**
- Displays full agreement text with version and effective date
- Shows acceptance checkbox (must be checked to enable accept button)
- Accept button (disabled until checkbox is checked)
- Shows success message and redirects to dashboard after acceptance
- Displays notice if user has already accepted the current version
- Handles loading and error states

**Usage:**
Users can navigate to `/ethics` to view and accept the agreement.

---

### 2. EthicsAgreementModal Component
**Location:** `frontend/src/lib/components/EthicsAgreementModal.svelte`  
**Requirements:** 3.1, 3.4

A modal dialog that blocks actions requiring ethics agreement acceptance.

**Props:**
- `isOpen` (bindable boolean) - Controls modal visibility
- `onClose` (optional function) - Callback when modal is closed/declined
- `onAccept` (optional function) - Callback when agreement is accepted
- `redirectAfterAccept` (optional string) - URL to redirect to after acceptance (default: '/dashboard')

**Features:**
- Modal overlay that blocks interaction with page content
- Displays full agreement text in scrollable area
- Shows informational message about requirement
- Acceptance checkbox and action buttons (Accept/Decline)
- Prevents body scroll when open
- Handles loading and error states

**Example Usage:**

```svelte
<script lang="ts">
  import EthicsAgreementModal from '$lib/components/EthicsAgreementModal.svelte';
  
  let showEthicsModal = $state(false);
  
  async function handleWebsiteRegistration() {
    // Check if user has accepted ethics agreement
    const response = await fetch(`${API}/api/ethics/status`, {
      credentials: 'include'
    });
    
    const data = await response.json();
    
    if (data.status?.needs_acceptance) {
      // Show modal to require acceptance
      showEthicsModal = true;
      return;
    }
    
    // Proceed with registration...
  }
  
  function handleEthicsAccepted() {
    // Called after user accepts agreement
    console.log('Ethics agreement accepted!');
    // Continue with the blocked action...
  }
</script>

<button onclick={handleWebsiteRegistration}>
  Register Website
</button>

<EthicsAgreementModal 
  bind:isOpen={showEthicsModal}
  onAccept={handleEthicsAccepted}
  redirectAfterAccept="/websites/register"
/>
```

---

### 3. AgreementHistory Component
**Location:** `frontend/src/lib/components/AgreementHistory.svelte`  
**Requirements:** 3.3

Displays the user's ethics agreement acceptance history and current status.

**Features:**
- Shows current acceptance status with visual indicators:
  - Green: User has accepted current version
  - Yellow: User needs to accept current version (with link to ethics page)
  - Gray: No agreement configured
- Lists all past acceptances with:
  - Agreement version
  - Acceptance date and time
  - IP address (if available)
  - "Current" badge for the active version
- Handles loading and error states
- Auto-loads data on mount

**Example Usage:**

```svelte
<script lang="ts">
  import AgreementHistory from '$lib/components/AgreementHistory.svelte';
</script>

<div class="container">
  <h1>My Account</h1>
  
  <!-- Display ethics agreement history -->
  <AgreementHistory />
</div>
```

---

## API Endpoints Used

All components interact with these backend endpoints:

### GET `/api/ethics/current`
Returns the current ethics agreement.

**Response:**
```json
{
  "agreement": {
    "version": "1.0",
    "content": "Full agreement text...",
    "effective_date": "2024-12-13T00:00:00"
  }
}
```

### POST `/api/ethics/accept`
Accepts the ethics agreement.

**Request Body:**
```json
{
  "agreement_version": "1.0",
  "ip_address": null
}
```

**Response:**
```json
{
  "message": "Ethics agreement accepted successfully",
  "acceptance": {
    "id": 1,
    "agreement_version": "1.0",
    "accepted_at": "2024-12-13T10:30:00"
  }
}
```

### GET `/api/ethics/status`
Returns the user's acceptance status and history.

**Response:**
```json
{
  "status": {
    "has_agreement": true,
    "current_version": "1.0",
    "effective_date": "2024-12-13T00:00:00",
    "has_accepted": true,
    "needs_acceptance": false
  },
  "history": [
    {
      "id": 1,
      "agreement_version": "1.0",
      "accepted_at": "2024-12-13T10:30:00",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

---

## Integration Points

### Where to Use EthicsAgreementModal

The modal should be integrated into any action that requires ethics agreement acceptance:

1. **Website Registration** (Task 16.1)
   - Check acceptance status before allowing registration
   - Show modal if not accepted

2. **Website Remediation** (Task 9)
   - Check acceptance status before starting remediation
   - Show modal if not accepted

3. **Any Future Protected Actions**
   - Follow the same pattern: check status, show modal if needed

### Where to Display AgreementHistory

The history component can be displayed in:

1. **User Profile/Settings Page**
   - Show as part of account information

2. **Ethics Agreement Page**
   - Show below the main agreement content

3. **Dashboard** (optional)
   - Show in a dedicated section for compliance tracking

---

## Styling

All components use Tailwind CSS classes consistent with the existing application design:

- **Colors:** Blue for primary actions, green for success, yellow for warnings, red for errors
- **Spacing:** Consistent padding and margins using Tailwind's spacing scale
- **Typography:** Clear hierarchy with appropriate font sizes and weights
- **Accessibility:** Proper ARIA labels, semantic HTML, keyboard navigation support

---

## Testing Checklist

When testing these components:

- [ ] Ethics page loads and displays agreement correctly
- [ ] Checkbox must be checked before accept button is enabled
- [ ] Accept button shows loading state during submission
- [ ] Success message appears and redirects to dashboard
- [ ] Already accepted notice shows for users who have accepted
- [ ] Modal opens and closes correctly
- [ ] Modal blocks page interaction when open
- [ ] Modal accept/decline buttons work correctly
- [ ] Modal redirects to specified page after acceptance
- [ ] History component loads and displays status correctly
- [ ] History shows all past acceptances with correct data
- [ ] Current version is highlighted in history
- [ ] Error states display helpful messages
- [ ] All components are responsive on mobile devices

---

## Notes

- All components require authentication (user must be logged in)
- Components automatically redirect to login if not authenticated
- IP address is captured by backend, not sent from frontend
- Agreement content supports markdown-style formatting
- Components handle missing or null data gracefully
