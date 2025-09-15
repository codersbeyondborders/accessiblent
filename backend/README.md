# Accessiblent – Backend

Python backend for the Accessiblent project. Provides APIs for auditing websites, applying accessibility fixes, and powering the AI-based chat system.

---

## 🚀 Features

* Audit webpages for accessibility issues (WCAG-based).
* Auto-fix common issues (alt-text, ARIA labels, contrast).
* AI-powered enhancements (image alt text, remediation suggestions).
* REST API for frontend (Svelte + Tailwind).

---

## ⚙️ Setup

### Prerequisites

* Python 3.10+
* pip or virtualenv

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Server

```bash
uvicorn app.main:app --reload
```

API runs at 👉 `http://localhost:8000`

---

## 🔑 Environment Variables

Create a `.env` file inside `backend/`:

```
OPENAI_API_KEY=your_api_key_here
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
│── app/
│   ├── main.py      # Entry point
│   ├── audit.py     # Accessibility audit logic
│   ├── fix.py       # Auto-fix engine
│   ├── ai.py        # AI integrations
│   └── utils/       # Helpers
│── tests/           # Unit tests
│── requirements.txt # Dependencies
```
