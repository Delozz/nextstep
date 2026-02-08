# NextStep 🚀

Interactive career planning platform with AI-powered resume analysis and mock interviews.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Or install individually:**
```bash
# Core app
pip install streamlit pandas numpy scikit-learn plotly joblib

# PDF parsing
pip install PyPDF2 pypdf

# AI features
pip install google-genai python-dotenv

# UI enhancements
pip install streamlit-lottie requests

# Interview feature
pip install fastapi uvicorn[standard] websockets
```

### 2. Set Up API Key

Create a `.env` file:
```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Run the App

```bash
streamlit run app.py
```

### 4. (Optional) Run Interview Server

For the mock interview feature:
```bash
uvicorn src.interview.server:app --reload --port 8000
```

---

## Features

| Feature | Description |
|---------|-------------|
| 📊 **City Comparison** | Compare salary, rent, and cost of living across US cities |
| 🗺️ **Map View** | Interactive map with viability scores |
| 💰 **Budget Lab** | Monthly budget breakdown calculator |
| 📄 **Resume Parser** | AI-powered resume analysis using Gemini |
| 🎤 **Mock Interview** | Real-time AI interview practice (~$2/session) |

---

## Project Structure

```
nextstep/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── .env                      # API keys (create this)
├── src/
│   ├── resume_parser.py      # AI resume analysis
│   └── interview/            # Mock interview feature
│       ├── server.py         # FastAPI WebSocket server
│       ├── scoring.py        # 70/30 scoring algorithm
│       └── prompts.py        # Role-specific personas
└── data/
    └── sample_livability_data.csv
```

---

## Requirements

- Python 3.10+
- Gemini API key ([Get one here](https://aistudio.google.com/apikey))
