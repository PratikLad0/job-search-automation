# ⚛️ Job Search Automation - Frontend

React + TypeScript web interface for the Job Search Automation project.
Built with Vite and Tailwind CSS.

## 🛠️ Tech Stack
- React 18
- TypeScript
- Tailwind CSS
- React Query
- Lucide React
- Recharts (for dashboard stats)
- Markdown Preview (for resumes)

## 🚀 Setup

### Prerequisites
- Node.js 18+
- npm or yarn or pnpm

### Installation

1.  **Navigate to directory**:
    ```bash
    cd job-search-automation/frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Run Development Server**:
    ```bash
    npm run dev
    ```

Access the application at `http://localhost:5173`.

### 🌐 Connecting to Backend

The frontend communicates with the backend API running at `http://localhost:8000`.
Ensure the backend server is running concurrently.

## 📦 Features & Usage

### 📊 Dashboard
- Visualize your job search funnel (Applied, Interviewing, Rejected).
- View daily/weekly progress.

### 🔎 Job Board
- Filter jobs by source, location, and match score.
- **Auto Apply**: Click on a job card to generate documents and trigger automation.

### 🏢 Company Search
- Use the "Companies" tab to search specifically for a company's career page.
- Enter "Company Name" and "Location" (e.g., "OpenAI", "San Francisco").
- The AI will find the career page and extract relevant listings.

### 📧 Smart Inbox
- Connect your Gmail to view job-related emails directly in the app.
- **AI Reply**: Select an email and click "Generate Reply" to get a drafted response based on your profile context.

### 💬 AI Assistant
- Use the chat interface to ask career advice.
- Context-aware: The assistant knows about your profile and the jobs you've saved.

### 👤 Profile
- Upload your existing resume (PDF/DOCX) to auto-populate your profile.
- Edit your skills and experience to improve job matching accuracy.

## 📦 Build for Production

```bash
npm run build
```
