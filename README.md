# Accessify
### Your Smart Accessibility Agent

A multi-tenant SaaS platform that enables nonprofit organizations to generate remediated, accessible HTML versions of their websites. Built with a **Python FastAPI backend** and a **SvelteKit + Tailwind frontend**, Accessify provides organization-based authentication, domain verification, ethics agreements, and automated accessibility remediation.

---

## 🚀 Features

### Multi-Tenant Platform
* **Organization Authentication**: Sign up with organizational email domains (public email providers blocked)
* **Domain Verification**: Prove domain ownership via meta tag or well-known file
* **Ethics Agreements**: Versioned agreements with audit trail tracking
* **User Management**: Secure JWT-based sessions with HTTP-only cookies

### Accessibility Remediation
* **Website Audit**: Analyze webpages for accessibility issues using axe-core
* **Automated Fixes**: Apply code-level remediations (alt-text, ARIA attributes, color contrast)
* **Preview URLs**: Unique URLs for viewing remediated HTML
* **Iframe Embedding**: Generate embeddable snippets with proper CORS configuration

### AI-Powered Features
* **Interactive Chat**: Ask questions about remediated content with RAG-based responses
* **Context-Aware**: Chat references specific accessibility fixes applied
* **Text-to-Speech**: Read responses aloud with play, pause, and stop controls

### Compliance & Security
* **Audit Trail**: Comprehensive logging of all significant actions
* **Session Security**: 24-hour expiration, secure cookies, CSRF protection
* **Data Isolation**: Multi-tenant architecture with organization-level separation

---

## 🛠️ Tech Stack

### Frontend
* [SvelteKit](https://kit.svelte.dev/) – Full-stack web framework
* [TypeScript](https://www.typescriptlang.org/) – Type-safe JavaScript
* [Tailwind CSS](https://tailwindcss.com/) – Utility-first CSS framework
* Accessible form controls, responsive layouts, and error handling

### Backend
* [FastAPI](https://fastapi.tiangolo.com/) – Modern Python web framework
* [TiDB](https://www.pingcap.com/tidb/) – MySQL-compatible distributed database
* [axe-core](https://github.com/dequelabs/axe-core) – Accessibility testing engine
* [OpenAI API](https://openai.com/) – Embeddings and chat completions
* [bcrypt](https://github.com/pyca/bcrypt/) – Password hashing
* [PyJWT](https://pyjwt.readthedocs.io/) – JWT token management

### Infrastructure
* **Database**: TiDB Cloud (MySQL-compatible)
* **Email**: SMTP with mock mode for development
* **Storage**: Database-backed HTML storage with vector embeddings

---

## 📂 Project Structure

```
accessify/
│
├── backend/                    # Python FastAPI backend
│   ├── app.py                  # Main application entry point
│   ├── auth.py                 # Authentication service
│   ├── domains.py              # Domain verification service
│   ├── websites.py             # Website management service
│   ├── ethics.py               # Ethics agreement service
│   ├── email_service.py        # Email notification service
│   ├── audit_trail.py          # Audit logging service
│   ├── a11y.py                 # Accessibility auditing
│   ├── fixer.py                # HTML remediation engine
│   ├── db.py                   # Database utilities
│   ├── models.sql              # Base database schema
│   ├── migrate.py              # Migration runner
│   ├── seed_data.py            # Test data seeding
│   ├── migrations/             # SQL migration files
│   │   └── 001_add_auth_and_org_tables.sql
│   ├── test_*.py               # Test files
│   ├── requirements.txt        # Python dependencies
│   └── README.md               # Backend documentation
│
├── frontend/                   # SvelteKit + TypeScript frontend
│   ├── src/
│   │   ├── routes/             # Pages and layouts
│   │   │   ├── (protected)/    # Authenticated routes
│   │   │   ├── signup/         # User registration
│   │   │   ├── login/          # User login
│   │   │   └── verify-email/   # Email verification
│   │   ├── lib/
│   │   │   ├── components/     # Reusable UI components
│   │   │   ├── stores/         # Svelte stores (auth, toast)
│   │   │   └── utils/          # Utilities (validation, errors)
│   │   └── app.css             # Global styles
│   ├── static/                 # Static assets
│   ├── package.json            # Frontend dependencies
│   └── README.md               # Frontend documentation
│
├── .kiro/                      # Kiro spec files
│   └── specs/
│       └── org-auth-domain-verification/
│           ├── requirements.md # Feature requirements
│           ├── design.md       # Design document
│           └── tasks.md        # Implementation tasks
│
├── README.md                   # This file
└── LICENSE                     # MIT License
```

---

## ⚙️ Installation & Setup

### Prerequisites

* **Node.js** 18+ ([Download](https://nodejs.org/))
* **Python** 3.9+ ([Download](https://www.python.org/downloads/))
* **TiDB Cloud Account** ([Sign up](https://tidbcloud.com/)) or local TiDB instance
* **OpenAI API Key** ([Get key](https://platform.openai.com/api-keys))

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/accessify.git
cd accessify
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your actual values
# Required variables:
#   - OPENAI_API_KEY: Your OpenAI API key
#   - TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DB: TiDB connection details
#   - JWT_SECRET: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Important Configuration Notes:**
- **JWT_SECRET**: Generate a strong random secret for production
- **EMAIL_MODE**: Use `mock` for development (logs to console), `smtp` for production
- **CORS_ORIGINS**: Set to your frontend URL (default: `http://localhost:5173`)

#### Database Setup

```bash
# Run migrations to create tables
python migrate.py

# Seed test data (optional, for development)
python seed_data.py

# Verify database schema
python verify_schema.py
```

**Test Credentials** (after seeding):
- Email: `admin@a11yfirst.org`
- Password: `TestPassword123!`

Other test users: `developer@a11yfirst.org`, `coordinator@disabilityrights.org`, `tech@inclusivetech.org` (same password)

#### Start Backend Server

```bash
uvicorn app:app --reload
```

Backend runs at 👉 `http://localhost:8000`

API documentation available at 👉 `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your backend API URL
# Default: VITE_API_BASE=http://localhost:8000
```

#### Start Development Server

```bash
npm run dev
```

Frontend runs at 👉 `http://localhost:5173`

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
source .venv/bin/activate   # Activate virtual environment
pytest                       # Run all tests
pytest -v                    # Verbose output
pytest test_auth.py          # Run specific test file
```

**Test Coverage:**
- Authentication and session management
- Domain verification logic
- Ethics agreement tracking
- Website registration and remediation
- Audit trail logging
- Email service (mock mode)

### Frontend Tests

```bash
cd frontend
npm run test              # Run tests
npm run test:ui           # Run tests with UI
```

---

## 📖 End-to-End User Flow

This section provides a complete walkthrough of the platform from signup to remediation.

### Quick Overview

1. **Sign Up** → Register with organizational email
2. **Verify Email** → Click verification link in email
3. **Log In** → Authenticate with credentials
4. **Add Domain** → Register your organization's domain
5. **Verify Domain** → Place verification token on your website
6. **Accept Ethics Agreement** → Review and accept terms
7. **Register Website** → Add entry URL for remediation
8. **Remediate** → Generate accessible HTML version
9. **Preview & Embed** → View results and get iframe snippet
10. **Chat** → Ask questions about remediated content

### Detailed Testing Guide

#### Step 1: Sign Up with Organizational Email

**Action:** Navigate to signup page and create an account

```bash
# Navigate to frontend
http://localhost:5173/signup
```

**Test Data:**
- Email: `testuser@mynonprofit.org` (use any organizational domain, NOT gmail.com)
- Password: `SecurePass123!`
- Full Name: `Test User`
- Organization Name: `My Nonprofit Organization`

**Expected Outcome:**
- ✓ Form validates email is not a public domain
- ✓ Account is created
- ✓ Verification email is sent (check console logs in mock mode)
- ✓ Success message displayed with instructions to check email

**Verification:**
```bash
# Check database for new user
cd backend
source .venv/bin/activate
python -c "from db import q; print(q('SELECT email, is_verified FROM user WHERE email=%s', ('testuser@mynonprofit.org',)))"
```

**Common Issues:**
- "Public email domain" error → Use organizational email, not gmail/yahoo/outlook
- Email not received → Check `EMAIL_MODE=mock` in backend/.env, verification link logged to console

---

#### Step 2: Verify Email Address

**Action:** Click verification link from email

**Using Seed Data (Quick Test):**
```bash
# Use pre-verified account
Email: admin@a11yfirst.org
Password: TestPassword123!
# Skip to Step 3
```

**Using New Account:**
```bash
# Find verification token in backend console logs (mock mode)
# Or in database:
python -c "from db import q; print(q('SELECT verification_token FROM user WHERE email=%s', ('testuser@mynonprofit.org',)))"

# Navigate to verification URL
http://localhost:5173/verify-email/{TOKEN}
```

**Expected Outcome:**
- ✓ Account is activated (`is_verified=true`)
- ✓ Success message displayed
- ✓ Redirect to login page

**Verification:**
```bash
python -c "from db import q; print(q('SELECT email, is_verified FROM user WHERE email=%s', ('testuser@mynonprofit.org',)))"
# Should show is_verified=1
```

---

#### Step 3: Log In

**Action:** Authenticate with credentials

```bash
http://localhost:5173/login
```

**Test Data:**
- Email: `admin@a11yfirst.org` (or your verified email)
- Password: `TestPassword123!`

**Expected Outcome:**
- ✓ Session created with JWT token
- ✓ HTTP-only cookie set
- ✓ Redirect to dashboard
- ✓ User info displayed in header

**Verification:**
```bash
# Check browser DevTools → Application → Cookies
# Should see 'session' cookie with HttpOnly flag

# Check database for active session
python -c "from db import q; import datetime; print(q('SELECT user_id, expires_at FROM session WHERE expires_at > %s', (datetime.datetime.now(),)))"
```

**Common Issues:**
- "Invalid credentials" → Ensure account is verified (Step 2)
- Session not persisting → Check browser allows cookies

---

#### Step 4: Add Domain

**Action:** Register your organization's domain

```bash
# From dashboard, click "Add Domain" or navigate to:
http://localhost:5173/domains/add
```

**Test Data:**
- Domain Name: `mynonprofit.org` (without http:// or www)

**Expected Outcome:**
- ✓ Domain record created with verification token
- ✓ Redirect to verification instructions page
- ✓ Token displayed for both meta tag and well-known file methods

**Verification:**
```bash
python -c "from db import q; print(q('SELECT domain_name, verification_token, is_verified FROM domain WHERE domain_name=%s', ('mynonprofit.org',)))"
```

**Common Issues:**
- Domain already exists → Use a different domain or delete existing one
- Invalid format → Remove http://, https://, www, and trailing slashes

---

#### Step 5: Verify Domain Ownership

**Action:** Place verification token on your website

**Method A: Meta Tag (Recommended for Testing)**

```html
<!-- Add to <head> section of your domain's homepage -->
<meta name="accessify-verification" content="YOUR_VERIFICATION_TOKEN_HERE">
```

**Method B: Well-Known File**

```bash
# Create file at: https://mynonprofit.org/.well-known/accessify-verification.txt
# Content: YOUR_VERIFICATION_TOKEN_HERE
```

**For Local Testing (Mock Domain):**

Since you likely don't control a real domain for testing, use the seed data which includes pre-verified domains:

```bash
# Use seed data account with verified domain
Email: admin@a11yfirst.org
Password: TestPassword123!
Domain: a11yfirst.org (already verified)
```

**Trigger Verification:**
```bash
# Click "Verify Now" button on verification instructions page
# Or navigate to:
http://localhost:5173/domains/{DOMAIN_ID}/verify
```

**Expected Outcome:**
- ✓ System fetches domain homepage
- ✓ Token found in meta tag or well-known file
- ✓ Domain marked as verified
- ✓ Verification timestamp recorded
- ✓ Success message displayed

**Verification:**
```bash
python -c "from db import q; print(q('SELECT domain_name, is_verified, verification_method, verified_at FROM domain WHERE domain_name=%s', ('a11yfirst.org',)))"
```

**Common Issues:**
- Verification fails → Ensure token is placed correctly, domain is accessible via HTTPS
- Timeout error → Check `DOMAIN_VERIFICATION_TIMEOUT` in backend/.env
- Token not found → Clear CDN cache, wait for DNS propagation

---

#### Step 6: Accept Ethics Agreement

**Action:** Review and accept terms of service

```bash
# Navigate to ethics agreement page
http://localhost:5173/ethics
```

**Expected Outcome:**
- ✓ Full agreement text displayed with version number
- ✓ Checkbox to confirm acceptance
- ✓ Accept button enabled after checkbox checked
- ✓ Acceptance recorded in audit trail with timestamp and IP

**Verification:**
```bash
python -c "from db import q; print(q('SELECT user_id, agreement_version, accepted_at FROM ethics_acceptance ORDER BY accepted_at DESC LIMIT 5'))"
```

**Note:** Ethics acceptance is required before registering websites. If you try to register a website without accepting, you'll be prompted with a modal.

---

#### Step 7: Register Website for Remediation

**Action:** Add entry URL for a website to remediate

```bash
# From dashboard, click "Register Website" or navigate to:
http://localhost:5173/websites/register
```

**Test Data:**
- Domain: Select `a11yfirst.org` (or your verified domain)
- Entry URL: `https://a11yfirst.org` (must match selected domain)
- Website Name: `Main Website` (optional)

**Expected Outcome:**
- ✓ URL validated against verified domain
- ✓ Website record created
- ✓ Redirect to website detail page
- ✓ Status shows "registered"

**Verification:**
```bash
python -c "from db import q; print(q('SELECT id, entry_url, name, status FROM website ORDER BY created_at DESC LIMIT 5'))"
```

**Common Issues:**
- "Domain not verified" → Complete Step 5 first
- "Ethics agreement required" → Complete Step 6 first
- URL validation fails → Ensure URL domain matches selected domain exactly

---

#### Step 8: Trigger Remediation

**Action:** Start accessibility audit and remediation

```bash
# From website detail page, click "Start Remediation"
# Or navigate to:
http://localhost:5173/websites/{WEBSITE_ID}
```

**Expected Outcome:**
- ✓ HTML fetched from entry URL
- ✓ Accessibility audit runs (axe-core)
- ✓ Issues identified and stored
- ✓ Code-level fixes applied (no overlay scripts)
- ✓ Remediated HTML stored
- ✓ Preview URL generated
- ✓ Status updates: fetching → auditing → fixing → complete

**Verification:**
```bash
# Check page record
python -c "from db import q; print(q('SELECT id, url, status FROM page ORDER BY created_at DESC LIMIT 1'))"

# Check issues found
python -c "from db import q; page_id = q('SELECT id FROM page ORDER BY created_at DESC LIMIT 1')[0]['id']; print(q('SELECT COUNT(*) as count FROM issue WHERE page_id=%s', (page_id,)))"

# Check audit log
python -c "from db import q; print(q('SELECT event_type, details FROM audit_log WHERE event_type=%s ORDER BY created_at DESC LIMIT 1', ('remediation_completed',)))"
```

**Common Issues:**
- Fetch fails → Ensure entry URL is accessible, not behind authentication
- Timeout → Check network connectivity, increase timeout in backend/.env
- No issues found → URL may already be highly accessible (good!)

---

#### Step 9: View Preview and Get Iframe Snippet

**Action:** Access remediated content

**Preview URL:**
```bash
# Copy preview URL from website detail page
http://localhost:8000/output/{PAGE_ID}

# Open in new tab to view remediated HTML
```

**Iframe Snippet:**
```html
<!-- Copy from website detail page -->
<iframe 
  src="http://localhost:8000/output/{PAGE_ID}"
  sandbox="allow-same-origin allow-forms"
  style="width: 100%; height: 600px; border: 1px solid #ccc;"
  title="Accessible version of {WEBSITE_NAME}">
</iframe>
```

**Expected Outcome:**
- ✓ Preview URL serves remediated HTML
- ✓ Proper content-type headers (text/html)
- ✓ CORS headers allow embedding from verified domain
- ✓ Iframe snippet includes sandbox attributes
- ✓ Copy-to-clipboard functionality works

**Verification:**
```bash
# Test preview URL
curl -I http://localhost:8000/output/{PAGE_ID}
# Should return 200 OK with Content-Type: text/html

# Check CORS headers
curl -H "Origin: https://a11yfirst.org" -I http://localhost:8000/output/{PAGE_ID}
# Should include Access-Control-Allow-Origin header
```

---

#### Step 10: Chat About Remediated Content

**Action:** Ask questions about accessibility improvements

```bash
# From website detail page, click "Chat" or navigate to:
http://localhost:5173/websites/{WEBSITE_ID}/chat
```

**Test Questions:**
- "What accessibility issues were found?"
- "What fixes were applied?"
- "Tell me about the color contrast improvements"
- "What ARIA attributes were added?"

**Expected Outcome:**
- ✓ Remediated HTML loaded for retrieval
- ✓ Question submitted to backend
- ✓ Relevant chunks retrieved from content
- ✓ AI response generated with context
- ✓ Response references specific fixes applied
- ✓ Text-to-speech available for responses

**Verification:**
```bash
# Check chunks were created
python -c "from db import q; page_id = q('SELECT id FROM page ORDER BY created_at DESC LIMIT 1')[0]['id']; print(q('SELECT COUNT(*) as count FROM chunk WHERE page_id=%s', (page_id,)))"

# Check chat works
# Should see response in UI referencing accessibility improvements
```

**Common Issues:**
- No context in responses → Ensure chunks were created during remediation
- Generic responses → Check OpenAI API key is valid
- TTS not working → Check browser permissions for audio

---

### Complete Test Flow Summary

**Using Seed Data (Fastest):**

```bash
# 1. Start backend and frontend
cd backend && source .venv/bin/activate && uvicorn app:app --reload &
cd frontend && npm run dev &

# 2. Seed database
cd backend && python seed_data.py

# 3. Log in
# Navigate to: http://localhost:5173/login
# Email: admin@a11yfirst.org
# Password: TestPassword123!

# 4. View dashboard
# See pre-verified domain: a11yfirst.org
# See sample websites

# 5. Register new website
# Navigate to: http://localhost:5173/websites/register
# Domain: a11yfirst.org
# Entry URL: https://example.com (or any accessible URL)

# 6. Remediate
# Click "Start Remediation"
# Wait for completion

# 7. View results
# Preview URL and iframe snippet displayed
# Click "Chat" to ask questions
```

**Expected Time:** 5-10 minutes for complete flow

---

### Testing Checklist

- [ ] Sign up with organizational email (public domains rejected)
- [ ] Verify email address (account activated)
- [ ] Log in (session created, dashboard accessible)
- [ ] Add domain (verification token generated)
- [ ] Verify domain (token detected, domain marked verified)
- [ ] Accept ethics agreement (acceptance recorded in audit trail)
- [ ] Register website (URL validated against verified domain)
- [ ] Trigger remediation (HTML fetched, audited, fixed)
- [ ] View preview URL (remediated HTML served)
- [ ] Copy iframe snippet (embeddable code generated)
- [ ] Chat about content (AI responses reference fixes)
- [ ] Log out (session invalidated, cookies cleared)

---

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

See `backend/.env.example` for complete documentation. Key variables:

```env
# OpenAI
OPENAI_API_KEY=sk-your-key-here
EMBED_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini

# Database (TiDB)
TIDB_HOST=gateway01.region.prod.aws.tidbcloud.com
TIDB_PORT=4000
TIDB_USER=your-username
TIDB_PASSWORD=your-password
TIDB_DB=accessibility

# Authentication
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24

# Email
EMAIL_MODE=mock  # Use 'smtp' for production
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password

# Application
BASE_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
```

### Frontend (`frontend/.env`)

```env
# API Configuration
VITE_API_BASE=http://localhost:8000

# Application
VITE_APP_NAME=Accessify
VITE_APP_ENV=development
```

---

## 📦 Deployment

### Production Checklist

- [ ] Generate strong `JWT_SECRET` (32+ bytes)
- [ ] Configure production database credentials
- [ ] Set `EMAIL_MODE=smtp` with valid SMTP credentials
- [ ] Update `BASE_URL` to production frontend URL
- [ ] Update `CORS_ORIGINS` to production frontend domain
- [ ] Set `DEBUG=false` and `LOG_LEVEL=INFO`
- [ ] Enable HTTPS for both frontend and backend
- [ ] Configure proper SSL certificates
- [ ] Set up database backups
- [ ] Configure monitoring and logging

### Deployment Options

**Backend:**
- AWS (EC2, ECS, Lambda)
- Google Cloud (Cloud Run, App Engine)
- Azure (App Service, Container Instances)
- DigitalOcean (App Platform, Droplets)

**Frontend:**
- Vercel (recommended for SvelteKit)
- Netlify
- Cloudflare Pages
- AWS Amplify

**Database:**
- TiDB Cloud (recommended)
- AWS RDS (MySQL)
- Google Cloud SQL
- Azure Database for MySQL

---

## 🔒 Security Considerations

* **Password Security**: bcrypt with cost factor 12
* **Session Management**: JWT tokens with 24-hour expiration, HTTP-only cookies
* **CSRF Protection**: SameSite=Strict cookie attribute
* **Rate Limiting**: 5 login attempts per 15 minutes per IP
* **Domain Verification**: Cryptographically random tokens (32 bytes)
* **Input Validation**: All user inputs validated and sanitized
* **SQL Injection Prevention**: Parameterized queries throughout
* **XSS Prevention**: Content escaping in frontend
* **CORS**: Restricted to verified domains

---

## 📚 Documentation

* **Backend**: See `backend/README.md` for API documentation
* **Frontend**: See `frontend/README.md` for component documentation
* **Database**: See `backend/DATABASE_SETUP.md` for schema details
* **Spec**: See `.kiro/specs/org-auth-domain-verification/` for requirements and design

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

## 🆘 Troubleshooting

### Backend Issues

**Database connection fails:**
- Verify TiDB credentials in `.env`
- Check network connectivity to TiDB Cloud
- Ensure database exists and migrations have run

**OpenAI API errors:**
- Verify `OPENAI_API_KEY` is valid
- Check API quota and billing status
- Ensure models specified in `.env` are available

**Email not sending:**
- In development, use `EMAIL_MODE=mock` (logs to console)
- For production, verify SMTP credentials
- Check firewall rules for SMTP port (587)

### Frontend Issues

**API connection fails:**
- Verify `VITE_API_BASE` matches backend URL
- Check CORS configuration in backend `.env`
- Ensure backend server is running

**Build errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear SvelteKit cache: `rm -rf .svelte-kit`
- Verify Node.js version (18+)

### Common Issues

**"Public email domain" error on signup:**
- Use an organizational email domain (not gmail.com, yahoo.com, etc.)
- For testing, use seed data accounts

**Domain verification fails:**
- Ensure verification token is placed correctly
- Check that domain is accessible via HTTPS
- Verify no caching is interfering with token detection
- Wait a few minutes for DNS/CDN propagation

**Session expires immediately:**
- Check system clock synchronization
- Verify `JWT_SECRET` is set correctly
- Clear browser cookies and try again

---
