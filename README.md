# Accessiblent
### Your Smart Accessibility Agent

An AI-powered web application that audits websites for accessibility issues and automatically suggests or applies fixes. Built with a **Python backend** (for auditing, AI-powered remediation, and orchestration) and a **Svelte + Tailwind frontend** (for user interaction and visualization).

---

## 🚀 Features

* **Website Audit**: Analyze any webpage for accessibility issues using WCAG guidelines.
* **Automated Fixes**: Apply quick remediations such as alt-text generation, ARIA attributes, and color contrast improvements.
* **Interactive Chat**: Ask questions about the audited site and get contextual answers powered by AI.
* **Text-to-Speech**: Read accessibility summaries and chat responses aloud with controls for play, pause, and stop.
* **Multi-View Interface**: Toggle between Summary, Inline Iframe, New Tab, and Chat modes.
* **Validation**: Input validation for URLs (supports entries with or without `http/https`).
* **Session Limits**: Restrict chat to 3 questions per website per session.

---

## 🛠️ Tech Stack

### Frontend

* [Svelte](https://svelte.dev/) – Reactive UI framework
* [Tailwind CSS](https://tailwindcss.com/) – Utility-first CSS framework
* Accessible form controls, toggle views, and responsive layouts

### Backend

* **Python** (FastAPI/Flask style REST API)
* **axe-core / Puppeteer (or Playwright)** – For accessibility auditing
* **BeautifulSoup / Cheerio-like parsing** – For HTML fixes
* **AI models (e.g., OpenAI, HuggingFace)** – For alt-text generation and remediation suggestions

### Other

* **Text-to-Speech (TTS)** integration
* **Session management** for chat
* **Deployment ready** with Docker and/or cloud hosting

---

## 📂 Project Structure

```
accessibility-agent/
│
├── backend/                # Python backend
│   ├── app/                # Core application
│   │   ├── main.py         # Entry point (FastAPI/Flask server)
│   │   ├── audit.py        # Website audit logic
│   │   ├── fix.py          # Auto-fix and remediation
│   │   ├── ai.py           # AI-powered features
│   │   └── utils/          # Helper functions
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Svelte + Tailwind frontend
│   ├── src/
│   │   ├── routes/         # Pages and components
│   │   ├── lib/            # UI helpers
│   │   └── styles/         # Tailwind config
│   └── package.json        # Frontend dependencies
│
├── docker-compose.yml      # Optional deployment setup
├── README.md               # Project overview (this file)
└── LICENSE                 # License file
```

---

## ⚙️ Installation

### Prerequisites

* Node.js (>= 18)
* Python (>= 3.10)
* pip or pipenv/poetry
* (Optional) Docker

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access the app at:
👉 `http://localhost:5173` (Frontend)
👉 `http://localhost:8000` (Backend API)

---

## 🔑 Environment Variables

Create `.env` files in both backend and frontend with the following keys:

### Backend (`backend/.env`)

```
OPENAI_API_KEY=your_api_key_here
ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (`frontend/.env`)

```
VITE_API_BASE=http://localhost:8000
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run test
```

---

## 📦 Deployment

* **Docker**: Use `docker-compose up --build` to run both frontend and backend together.
* **Cloud**: Deploy backend on AWS/GCP/Azure and frontend on Vercel/Netlify.

---

## 📖 Roadmap

* [ ] Improve auto-fix coverage (contrast adjustments, keyboard navigation)
* [ ] Caching for repeated audits of same URL
* [ ] Support for password-protected/session-based sites
* [ ] Enhanced reporting (PDF/CSV export of accessibility audit)
* [ ] Multi-language TTS

---