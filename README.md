# 🚀 Job Search Automation System

A powerful, self-hosted web application to automate your job search. Scrape job postings from multiple sources, get AI-powered scoring, generate tailored resumes, and track your applications—all from a comprehensive dashboard.

![Dashboard Preview](https://placehold.co/800x400?text=Dashboard+Preview)

## 📂 Project Structure

This project is divided into two main components:

- **[Backend](backend/README.md)**: Python-based API, scrapers, AI engine, and background workers.
- **[Frontend](frontend/README.md)**: React + TypeScript web interface.

## ✨ Key Features

- **🔎 Automated Scraping**: Support for LinkedIn, Indeed, RemoteOK, Naukri, Glassdoor, and more.
- **🎯 AI Company Search**: Targeted scraping of specific company career pages using AI.
- **🤖 AI-Powered Matching**: Scores jobs against your CV using local LLMs (Ollama) or cloud APIs (Gemini/OpenAI).
- **📝 Document Generation**: Auto-generates tailored Resumes (PDF) and Cover Letters.
- **📧 Smart Inbox**: Manage job-related emails, track applications, and generate AI replies.
- **💬 AI Career Assistant**: Real-time chat assistant for interview prep and career advice.
- **🔐 Google Integration**: Seamless Gmail and Google Auth integration.
- **📊 Advanced Dashboard**: Visualize progress, filter jobs, and manage applications.
- **🔔 Notifications**: Real-time alerts via Telegram.

## 🚀 Quick Start

### 1. Backend Setup
Navigate to the `backend` directory and follow the instructions in [backend/README.md](backend/README.md).

```bash
cd backend
# Install dependencies... (see backend/README.md)
python run.py
```
> **Note for Windows Users**: Always use `python run.py` to start the backend. This ensures the correct asyncio event loop is used for Playwright.

### 2. Frontend Setup
Navigate to the `frontend` directory and follow the instructions in [frontend/README.md](frontend/README.md).

```bash
cd frontend
npm install
npm run dev
```

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

MIT License
