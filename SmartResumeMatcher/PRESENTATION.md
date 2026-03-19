# Mini Project Presentation

---

## SLIDE 1: Title

# SMART RESUME MATCHER
### AI-Powered Resume Screening & Ranking System

**Mini Project | Computer Science Department**

*Your Name | USN | Date*

---

## SLIDE 2: Problem Statement

### Why This Project?

- **Problem**: HR teams spend 23 hours/week screening resumes
- **Challenge**: Manual screening is time-consuming and prone to bias
- **Solution**: Automate initial screening using AI/NLP

> "60% of recruiters say screening candidates is their biggest challenge"

---

## SLIDE 3: Project Overview

### What is Smart Resume Matcher?

- Web-based application built with **Python + Streamlit**
- Uses **Natural Language Processing (NLP)** for analysis
- Compares resumes against job descriptions
- Ranks candidates by match percentage
- Identifies missing skills and biases

---

## SLIDE 4: Architecture

### System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │ ──► │  Streamlit  │ ──► │  NLP Engine │
│   (Upload)  │     │   Frontend  │     │  (scikit)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Analytics  │
                    │  Dashboard  │
                    └─────────────┘
```

---

## SLIDE 5: Features

### Key Features

| Feature | Description |
|---------|-------------|
| PDF Resume Upload | Support for multiple PDF files |
| Job Description Input | Text area with skill detection |
| Match Scoring | TF-IDF + Cosine Similarity algorithm |
| Skill Analysis | Extracts matched & missing skills |
| Bias Detection | Identifies biased language |
| Visual Dashboard | Charts, tables, and metrics |
| Export Reports | Download CSV/JSON reports |

---

## SLIDE 6: Technology Stack

### Technologies Used

**Frontend**
- Streamlit - Web UI framework
- Plotly - Interactive charts

**Backend**
- Python - Core programming
- scikit-learn - NLP/Machine Learning
- NLTK - Text processing
- PyPDF2 - PDF text extraction

**Libraries**
- NumPy, Pandas - Data handling
- Groq SDK - AI Integration (optional)

---

## SLIDE 7: Algorithm

### How It Works

1. **Text Extraction**: Extract text from PDF resumes
2. **Preprocessing**: Clean and normalize text
3. **TF-IDF Vectorization**: Convert text to numerical vectors
4. **Cosine Similarity**: Calculate match percentage
5. **Skill Analysis**: Match required vs provided skills
6. **Composite Scoring**: Final ranking with bonuses/penalties

---

## SLIDE 8: Demo

### Live Demo

**Steps:**
1. Upload sample resumes
2. Paste job description
3. Click "Analyze"
4. View results

**Expected Output:**
- John Smith: ~80% (Best match)
- Sara Johnson: ~65% (Good match)
- Mike Chen: ~35% (Low match)

---

## SLIDE 9: Results

### Dashboard Overview

- **Total Candidates Analyzed**
- **Shortlisted Count** (above threshold)
- **Average Match Score**
- **Top Performer Score**

**Additional Views:**
- Candidate Rankings Table
- Skill Match Analysis
- Missing Skills Detection
- Bias Indicator Report

---

## SLIDE 10: Future Scope

### Enhancements

- [ ] Deploy to cloud (AWS/Streamlit Cloud)
- [ ] Add user authentication
- [ ] Integrate LinkedIn/GitHub APIs
- [ ] Use Transformer models (BERT, GPT)
- [ ] Multi-language support
- [ ] ATS compatibility scoring

---

## SLIDE 11: Conclusion

### Summary

- ✅ Automated resume screening
- ✅ AI-powered matching
- ✅ Fair & unbiased analysis
- ✅ Time-saving for HR teams
- ✅ Interactive visualization

**Thank You!**

Questions?

---

## SLIDE 12: References

### References

- scikit-learn.org - Machine Learning in Python
- nltk.org - Natural Language Toolkit
- streamlit.io - Data app framework
- Plotly.com - Interactive visualizations
- "Introduction to Information Retrieval" - Manning et al.

