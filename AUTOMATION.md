# Automated Job Application Documentation

This document explains how the Job Search Automation tool handles browser-based job applications and how you can use it to automate single-job applications.

## How it Works

The tool uses **Playwright**, a browser automation library, to interact with job portals.

### Key Features
1.  **Persistent Browser Context**: It uses your actual browser session (e.g., Chrome or Edge) so that you remain logged into Indeed, LinkedIn, etc.
2.  **Document Integration**: It automatically identifies the generated Resume and Cover Letter for a specific job and uploads them.
3.  **Form Automation**: It scans for "Apply" buttons and fills in required fields like Name, Email, and Phone based on your profile.

---

## Setup Requirements

### 1. Google Authentication (Gmail API)
To enable Email features (Inbox, Smart Reply), you need to set up Google OAuth:

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project.
3.  Enable the **Gmail API**.
4.  Configure the **OAuth Consent Screen** (User Type: External, Add Test Users).
5.  Create **OAuth Client ID** credentials (Application Type: Desktop App).
6.  Download the JSON file, rename it to `credentials.json`, and place it in the `backend/` directory.

### 2. Browser Login
Before starting the automation, ensure you are logged into your target job portal (e.g., [Indeed](https://www.indeed.com)) in your default browser. The automation will "piggyback" on this session.

### 3. Playwright Installation
The backend requires Playwright browsers to be installed. Run the following command in your terminal:
```powershell
playwright install chromium
```

> **IMPORTANT FOR WINDOWS USERS**:
> Always start the backend using `python backend/run.py` instead of uvicorn directly. This script enforces the `ProactorEventLoopPolicy` required for Playwright to function correctly on Windows.

---

## How to Automate an Application

Once you have a job in your dashboard and have generated a resume/cover letter:

1.  **Generate Documents**: Ensure you have generated a resume for the job.
2.  **Trigger Automation**: Click the **"Auto Apply"** button on the job card in the Job Board.
    *   *Note: This button only appears if you have already generated a resume for that job.*

### Automation Flow
1.  **URL Navigation**: Playwright opens the job URL.
2.  **Button Detection**: It looks for "Apply Now", "Easily Apply", or "Apply on Company Site".
3.  **Resume Upload**: It waits for the file input and uploads your generated PDF resume.
4.  **Cover Letter**: If the portal allows, it pastes the generated cover letter or uploads the PDF.
5.  **Submission**: It clicks the final "Submit" or "Apply" button.

---

## Configuration

You can configure the browser profile path in your `.env` file to ensure the automation uses the correct session:

```env
# Path to your Chrome User Data (example)
BROWSER_PROFILE_PATH="C:\Users\YourUser\AppData\Local\Google\Chrome\User Data"
```

### Troubleshooting: "Profile in Use"
If you get an error saying your browser profile is in use:
1.  **Close Chrome**: Close all open Chrome windows and try again.
2.  **Separate Profile**: Create a dedicated Chrome profile for automation and use its path in your `.env` file instead.

> [!WARNING]
> While automation is running, do not close the browser window that Playwright opens (if running in non-headless mode). Let it finish the steps and close automatically.
