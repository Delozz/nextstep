# NextStep - Setup Guide for Interview Feature

This guide will help you get the full NextStep app running with the AI-powered mock interview feature.

## Prerequisites

- Python 3.9 or higher
- Git
- A Google Gemini API key

## Step-by-Step Setup

### 1. Clone and Navigate to Project

```bash
git clone https://github.com/yourusername/nextstep.git
cd nextstep
```

### 2. Install All Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

**Important packages that MUST be installed:**
- `streamlit` - Main web framework
- `google-genai` - Gemini AI SDK (required for interviews & resume analysis)
- `fastapi` - Interview server backend
- `uvicorn[standard]` - ASGI server for FastAPI
- `websockets` - Real-time communication
- `streamlit-lottie` - Animations
- `plotly` - Data visualizations
- All others in `requirements.txt`

### 3. Configure API Key

Create a `.env` file in the root directory:

```bash
# .env
GEMINI_API_KEY=your_actual_api_key_here
```

**Get your Gemini API key:**
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API key"
3. Copy the key and paste it in `.env`

### 4. Start BOTH Servers (Required for Interview Feature)

You need **TWO** servers running simultaneously in **separate terminals**:

#### Terminal 1: Interview Backend Server

```bash
uvicorn src.interview.server:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process using WatchFiles
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
[Interview] Server starting...
```

#### Terminal 2: Streamlit App

```bash
streamlit run app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### 5. Access the App

Open your browser to the URL shown by Streamlit (usually `http://localhost:8501` or `http://localhost:8506`).

## Troubleshooting

### "Failed to connect to server. Is it running on port 8000?"

**Cause:** Interview backend server is not running.

**Fix:**
1. Open a separate terminal
2. Navigate to the project root
3. Run: `uvicorn src.interview.server:app --reload --port 8000`
4. Make sure you see "Application startup complete"
5. Refresh the Streamlit app

### "ModuleNotFoundError: No module named 'google.genai'"

**Cause:** The `google-genai` package is not installed.

**Fix:**
```bash
pip install google-genai
```

### "ImportError: cannot import name 'genai' from 'google'"

**Cause:** You might have an old conflicting `google` package.

**Fix:**
```bash
pip uninstall google
pip install google-genai
```

### "GEMINI_API_KEY not configured"

**Cause:** The `.env` file is missing or the API key is not set.

**Fix:**
1. Create a `.env` file in the project root
2. Add: `GEMINI_API_KEY=your_key_here`
3. Restart BOTH servers (they load `.env` at startup)

### Interview Report Not Showing

**Cause:** The interview completed but the report display has a bug.

**Fix:**
1. After interview ends, wait 5-10 seconds for report generation
2. The report should appear inline in the interview window
3. If not, try clicking "End Interview" manually

### Port Already in Use

**Cause:** Port 8000 or 8501 is already occupied.

**Fix:**

For interview server:
```bash
uvicorn src.interview.server:app --reload --port 8001
```
(Then update the WebSocket URL in the app)

For Streamlit:
```bash
streamlit run app.py --server.port 8502
```

## Quick Start Commands (Copy-Paste)

**For first-time setup:**
```bash
pip install -r requirements.txt
# Then edit .env and add your GEMINI_API_KEY
```

**To run the app every time:**

**Terminal 1:**
```bash
uvicorn src.interview.server:app --reload --port 8000
```

**Terminal 2:**
```bash
streamlit run app.py
```

## Features Checklist

Once both servers are running, you should be able to:

- ✅ Complete onboarding (name, career, debt, lifestyle, resume)
- ✅ Explore salary/city maps
- ✅ View budget breakdowns for different cities
- ✅ Upload resume for AI keyword analysis
- ✅ **Start mock interview** (requires both servers)
- ✅ Get real-time AI questions during interview
- ✅ Receive 70/30 scored report with feedback

## Architecture Overview

```
NextStep Application
├── Streamlit App (Frontend) ─────────────┐
│   - Main UI                              │
│   - Onboarding                           │
│   - Map/Budget tabs                      │
│   - Interview tab (embedded iframe) ────┼──> WebSocket
│                                          │
├── FastAPI Server (Backend) ─────────────┘
    - Port 8000
    - WebSocket endpoints
    - Gemini AI integration
    - Interview scoring
```

The interview feature requires **both** servers because:
1. Streamlit renders the UI and form
2. FastAPI handles real-time WebSocket communication with the AI
3. They communicate via `ws://localhost:8000`

## Common Mistakes

❌ **Starting only Streamlit** - Interview won't work, connection fails
✅ **Start both servers in separate terminals**

❌ **Placeholder API key in .env** - Server returns 500 errors
✅ **Use your real Gemini API key**

❌ **Starting server without restarting after .env change** - Old process has no key
✅ **Restart both servers after changing .env**

## Support

If you're still having issues:
1. Check that both servers are running (see their terminal output)
2. Verify `.env` has a real API key
3. Make sure all dependencies from `requirements.txt` are installed
4. Try clearing browser cache and reloading

---

**Happy interviewing!** 🎤✨
