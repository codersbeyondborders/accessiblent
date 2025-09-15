Deliberately Inaccessible Demo Site
===================================
This mini-site is intentionally full of accessibility anti-patterns
to test automated auditing / remediation tools.

Pages:
- index.html
- about.html
- contact.html

Examples of known issues (non-exhaustive):
- Missing lang attribute
- Missing meta viewport
- Generic/non-unique <title>
- Focus outlines removed
- Low color contrast
- Heading levels skipped/out of order
- Image without alt text
- Auto-playing audio without controls
- Vague links ('click here'), empty hrefs
- aria-hidden on interactive link
- Duplicate IDs
- Non-semantic clickable <div> without role/tabindex/keyboard
- Form fields without labels; placeholders only
- Table without headers/semantics
- Duplicate link text, different URLs
- Small touch targets
- Iframe without title
- Color-only status indicators
- Keyboard focus hijacking via JS

IMPORTANT: Do NOT ship this to production.
Use only for testing accessibility tools.