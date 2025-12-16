# Accessify – Backend

Python backend for the Accessify project. Provides APIs for auditing websites, applying accessibility fixes, and powering the AI-based chat system.

---

## 🚀 Features

* Multi-tenant SaaS platform for nonprofit organizations
* Organization-based authentication with email domain verification
* Domain ownership verification (meta tag / well-known file)
* Ethics agreement management with audit trails
* Audit webpages for accessibility issues (WCAG-based)
* Auto-fix common issues (alt-text, ARIA labels, contrast)
* AI-powered enhancements (image alt text, remediation suggestions)
* RAG-based chat system for accessible content
* REST API for frontend (SvelteKit + Tailwind)

---

## ⚙️ Setup

### Prerequisites

* Python 3.9+
* TiDB Cloud database or local TiDB instance
* pip or virtualenv

### Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Database Setup

1. Configure your database credentials in `.env` (see Environment Variables below)

2. Run database migrations:
```bash
python migrate.py
```

3. Seed test data (optional, for development):
```bash
python seed_data.py
```

4. Verify setup:
```bash
python verify_schema.py
```

For detailed database setup instructions, see [DATABASE_SETUP.md](./DATABASE_SETUP.md)

### Run Server

```bash
uvicorn app:app --reload
```

API runs at 👉 `http://localhost:8000`

---

## 🔑 Environment Variables

Create a `.env` file inside `backend/`:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
EMBED_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
EMBED_TOPK=24

# Database Configuration (TiDB Cloud)
TIDB_HOST=your-tidb-host.com
TIDB_PORT=4000
TIDB_USER=your-username
TIDB_PASSWORD=your-password
TIDB_DB=accessibility

# Optional: SSL Certificate for TiDB Cloud
# TIDB_SSL_CA=/path/to/ca-cert.pem

# Optional: Database Connection Pool
# DB_POOL_SIZE=5

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173
```

---

## 🧪 Testing

```bash
pytest
```

---

## 📂 Key Files

```
backend/
├── app.py              # FastAPI application entry point
├── db.py               # Database connection and query utilities
├── a11y.py             # Accessibility audit logic
├── fixer.py            # Auto-fix engine
├── models.sql          # Base database schema
├── migrate.py          # Database migration runner
├── seed_data.py        # Test data seeding script
├── verify_schema.py    # Schema verification utility
├── migrations/         # SQL migration files
│   ├── 001_add_auth_and_org_tables.sql
│   └── README.md
├── requirements.txt    # Python dependencies
├── DATABASE_SETUP.md   # Detailed database setup guide
└── README.md           # This file
```

## 🗄️ Database Schema

The application uses the following main tables:

- **organization** - Nonprofit organizations using the platform
- **user** - User accounts linked to organizations
- **session** - Active user sessions with JWT tokens
- **domain** - Verified domains owned by organizations
- **website** - Registered websites for remediation
- **page** - Remediated HTML pages with accessibility fixes
- **chunk** - Text chunks for RAG-based chat
- **issue** - Accessibility issues found during audits
- **ethics_agreement** - Versioned ethics agreements
- **ethics_acceptance** - User acceptance tracking
- **audit_log** - Audit trail of all significant actions

See [DATABASE_SETUP.md](./DATABASE_SETUP.md) for complete schema details.

## 🧑‍💻 Development

### Test Credentials

After running `seed_data.py`, you can use these test accounts:

**Email:** admin@a11yfirst.org  
**Password:** TestPassword123!

Other test users:
- developer@a11yfirst.org
- coordinator@disabilityrights.org
- tech@inclusivetech.org

All use the same password.

### Database Migrations

Create a new migration:
1. Add a new `.sql` file in `migrations/` with format `NNN_description.sql`
2. Run `python migrate.py` to apply

Reset database (development only):
```bash
python migrate.py --reset
```

**WARNING:** This drops all tables and data!
