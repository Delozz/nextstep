# ⚡ QUICK START GUIDE

## Get Running in 3 Steps

### Step 1: Install Dependencies (2 minutes)
```bash
pip install streamlit pandas numpy scikit-learn plotly joblib PyPDF2 pypdf google-generativeai python-dotenv
```

### Step 2: Run the App (instant)
```bash
streamlit run app.py
```

### Step 3: Open Browser
- Browser should auto-open to `http://localhost:8501`
- If not, manually navigate to that URL

**That's it! You're running! 🎉**

---

## Using the App (No Setup Needed)

The app works perfectly **without any configuration**. Just:

1. Select a career path from the sidebar
2. Enter your student loan debt
3. Choose your lifestyle preference
4. Click "Calculate Future"
5. Explore the 3 tabs:
   - **Map View**: See best cities on a map
   - **Budget Lab**: Analyze detailed finances
   - **Resume Pivot**: Check skill keywords

---

## Optional: Enable AI Features

### Why Enable AI?
Without it: Basic keyword matching ✅
With it: Deep resume analysis, skill extraction, career recommendations 🚀

### How to Enable (2 minutes):

1. **Get a Free API Key**
   - Go to https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

2. **Create .env File**
   ```bash
   # Create file named .env in project root
   # Add this line:
   GEMINI_API_KEY=paste_your_key_here
   ```

3. **Restart the App**
   - Stop the app (Ctrl+C)
   - Run `streamlit run app.py` again
   - Upload a PDF resume to test AI features

---

## Troubleshooting

### "No module named 'streamlit'"
**Fix:** Run the install command from Step 1

### "Address already in use"
**Fix:** Different port:
```bash
streamlit run app.py --server.port 8502
```

### "Import error from src"
**Fix:** Run from project root:
```bash
cd /path/to/nextstep
streamlit run app.py
```

### Can't upload PDF
**Fix:** Install pypdf:
```bash
pip install pypdf
```

---

## What's Included

### 9 Career Paths Analyzed:
- Software Engineer
- Data Scientist  
- Cybersecurity Analyst
- UX Designer
- Product Manager
- Machine Learning Engineer
- Cloud Architect
- Data Engineer
- DevOps Engineer

### 16 Cities Compared:
**Tier 1 (High Cost):** SF, NYC, Seattle, Boston
**Tier 2 (Growing):** Austin, Denver, Chicago, Atlanta, Portland
**Tier 3 (Affordable):** Raleigh, Huntsville, Columbus, Salt Lake City
**Tier 4 (College Towns):** College Station, Ann Arbor, Madison

### Financial Analysis:
- Monthly net pay (after taxes)
- Rent costs
- Student loan payments
- Lifestyle expenses
- Projected savings
- 5-year wealth projection

### Resume Analysis:
- ATS keyword matching
- Skills gap identification  
- Career fit scoring
- Improvement suggestions
- (With AI) Deep skill extraction & recommendations

---

## Testing the Backend

Want to verify everything works?

```bash
python test_backend.py
```

Should output:
```
✅ Loaded 144 rows of data.
Sample Cities: ['San Francisco' 'New York' 'Seattle' ...]
--- TEST CASE: San Francisco ---
Role: Software Engineer
Salary: $155,250
Net Monthly: $8,122.50
Thriving Score: 75/100
```

---

## File Structure

```
nextstep/
├── app.py              ← Main app (run this)
├── requirements.txt    ← Dependencies
├── test_backend.py     ← Test file
├── README.md          ← Full documentation
├── QUICK_START.md     ← This file
├── BUG_FIXES.md       ← What was fixed
├── .env.example       ← API key template
└── src/               ← Backend modules
    ├── loader.py      (Data loading)
    ├── logic.py       (Calculations)
    ├── resume_parser.py (AI analysis)
    └── ... (other modules)
```

---

## Next Steps

After running the app:

1. **Try Different Careers**: See how salaries vary
2. **Compare Cities**: Use Budget Lab to deep-dive
3. **Upload Resume**: Get instant feedback
4. **Adjust Lifestyle**: See impact on savings
5. **Enable AI** (optional): Get personalized recommendations

---

## Support

- 📖 Full docs: `README.md`
- 🐛 Bug fixes: `BUG_FIXES.md`  
- 🧪 Test backend: `python test_backend.py`
- ❓ Issues: Check Troubleshooting section above

---

**You're all set! Happy career planning! 🎓🚀**

Last updated: February 2026
