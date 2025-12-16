# Accessify – Frontend

Svelte + Tailwind frontend for the Accessify project. Provides the user interface for auditing websites, reviewing fixes, and interacting with the AI-powered chat.

---

## 🚀 Features

* Clean, accessible UI built with **Svelte + Tailwind CSS**.
* Input validation for website URLs (with or without `http/https`).
* Multi-view toggle: **Summary**, **Inline Iframe**, **Open in New Tab**, **Chat**.
* AI-powered chat interface (max 3 questions per session).
* Text-to-Speech support (play, pause, stop).

---

## ⚙️ Setup

### Prerequisites

* Node.js 18+
* npm or pnpm

### Installation

```bash
cd frontend
npm install
```

### Run Dev Server

```bash
npm run dev
```

Frontend runs at 👉 `http://localhost:5173`

---

## 🔑 Environment Variables

Create a `.env` file inside `frontend/`:

```
VITE_API_BASE=http://localhost:8000
```

---

## 📂 Key Files

```
frontend/
│── src/
│   ├── routes/      # Pages & components
│   ├── lib/         # Helpers & stores
│   └── styles/      # Tailwind config
│── package.json     # Dependencies
```
