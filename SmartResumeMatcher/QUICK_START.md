# SMART RESUME MATCHER

## Mini Project Demo

### Quick Start

**DOUBLE CLICK:** `START_DEMO.bat`

That's it! The app will open in your browser automatically.

---

## What This Project Does

An **AI-powered resume screening system** that:
- Uploads resumes (PDF or text)
- Compares against job description
- Ranks candidates by match score
- Shows missing skills
- Detects bias in resumes
- Displays beautiful analytics dashboard

---

## Files Included

| File | Purpose |
|------|---------|
| `START_DEMO.bat` | **One-click launcher** |
| `app.py` | Main application |
| `utils.py` | NLP analysis engine |
| `requirements.txt` | Dependencies |
| `DEMO_SCRIPT.md` | **Viva questions & answers** |
| `PRESENTATION.md` | **Slides for PPT** |
| `demo_files/` | Sample resumes & JD |

---

## Demo Files

```
demo_files/
├── sample_resume_1.txt      # Senior developer (high match)
├── sample_resume_2.txt      # Mid-level developer (medium match)
├── sample_resume_3.txt      # Fresh graduate (low match)
└── sample_job_description.txt
```

---

## How to Demo (5 Minutes)

1. **Start App**: Double-click `START_DEMO.bat`

2. **Upload Resumes**: 
   - Use the sample files from `demo_files/` folder
   - Drag & drop into the sidebar

3. **Paste Job Description**:
   - Copy from `demo_files/sample_job_description.txt`
   - Paste in the text area

4. **Analyze**: Click "Initiate Neural Analysis"

5. **Show Results**:
   - Overview tab → KPI cards
   - Rankings tab → Top candidates
   - Deep Analysis → Skill breakdown

---

## Expected Results

With sample files:
- **John Smith** → ~80% (Best match)
- **Sara Johnson** → ~65% (Good match)
- **Mike Chen** → ~35% (Low match)

---

## For PowerPoint Presentation

Copy content from `PRESENTATION.md` into your slides.

## For Viva Preparation

Read `DEMO_SCRIPT.md` for expected questions and answers.

---

## Technologies Used

- **Python** - Core language
- **Streamlit** - Web interface
- **scikit-learn** - NLP/TF-IDF
- **Plotly** - Charts
- **NLTK** - Text processing
- **PyPDF2** - PDF reading

---

## System Requirements

- Python 3.8+
- Windows/Mac/Linux
- Internet (for first-time setup)

---

## Troubleshooting

**Q: App doesn't start?**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Q: Import errors?**
```bash
python setup_nltk.py
```

**Q: PDF not reading?**
- Use text files (.txt) instead for demo
- Or create PDF from text

---

## Credits

Mini Project | Computer Science Department
