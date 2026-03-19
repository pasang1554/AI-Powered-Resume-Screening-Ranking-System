# SMART RESUME MATCHER - DEMO SCRIPT (Updated v4.0)

## How to Run (5 Seconds)
1. Double-click `START_DEMO.bat`
2. Browser opens automatically
3. Done!

---

## NEW FEATURES (v4.0)

### 1. One-Click Demo Button
- **Look for**: "🚀 Load Sample Data" button in sidebar
- **What it does**: Automatically loads 3 sample resumes + job description
- **No manual upload needed!**

### 2. Score Breakdown Chart
- Shows how the final score is calculated:
  - **Skills Match** (50% weight)
  - **Experience** (20% weight)
  - **Keywords** (20% weight)
  - **ATS Format** (10% weight)

### 3. ATS Score Display
- Shows how resume-friendly the format is (0-100%)
- Checks for: email, phone, education, experience sections, bullet points

### 4. Experience Years Detector
- Automatically extracts years of experience from resumes
- Compares against job requirements

### 5. PDF Report Download
- Professional PDF report with all results
- Download from Rankings tab

---

## Demo Steps for Viva

### Step 1: Start App (30 sec)
"Just double-click START_DEMO.bat and the app opens in browser"

### Step 2: Load Sample Data (30 sec)
1. **Look in LEFT sidebar** for "🚀 Load Sample Data" button
2. **Click it** - all 3 sample resumes load automatically
3. Job description is also loaded

### Step 3: Analyze (1 min)
1. Threshold is already set to 50%
2. Click "🚀 Initiate Neural Analysis"
3. Watch the analysis progress

### Step 4: Show Results (3 min)

#### Tab 1: Executive Overview
- 5 KPI Cards: Total, Shortlisted, Avg Match, ATS Score, Experience
- Distribution chart
- Selection funnel

#### Tab 2: Rankings
- Top 3 podium display
- Sortable data table
- **Download PDF Report** button

#### Tab 3: Deep Analysis
- **Score Breakdown Chart** (NEW!)
- ATS Score
- Experience Years
- Matched vs Missing Skills

#### Tab 4: Comparative Analytics
- Radar chart for skills
- Skill landscape chart
- Scatter plot analysis

---

## Expected Results

| Candidate | Match Score | Experience | ATS Score | Status |
|-----------|-------------|------------|-----------|--------|
| John Smith | ~80% | 6 years | ~80% | ✅ Shortlisted |
| Sara Johnson | ~65% | 4 years | ~70% | ✅ Shortlisted |
| Mike Chen | ~30% | 0 years | ~60% | ❌ Not Selected |

---

## What to Say During Demo

**Q: What new features did you add?**
"A: We added one-click demo loading, score breakdown visualization showing how scores are calculated (skills, experience, keywords, ATS), experience years detection, and PDF report generation."

**Q: How is the score calculated?**
"A: The score has 4 components: Skills Match (50%), Experience (20%), Keywords (20%), and ATS Format (10%). This gives a comprehensive evaluation of each candidate."

**Q: What is ATS Score?**
"A: ATS (Applicant Tracking System) score measures how resume-friendly the format is. It checks for proper sections like email, phone, education, experience, and proper formatting."

**Q: What is the algorithm used?**
"A: We use TF-IDF vectorization combined with skill matching. First, we extract skills from both job description and resume using a comprehensive skill taxonomy. Then we calculate similarity based on matched skills, keywords, and experience."

---

## Algorithms Explained

### 1. Skill Extraction
```
- Maintain a comprehensive IT skills database
- Use regex pattern matching to find skills
- Handle compound skills (e.g., "machine learning")
```

### 2. Score Calculation
```
Total Score = Skill_Match(50%) + Experience(20%) + Keywords(20%) + ATS(10%)
```

### 3. Experience Detection
```
- Use regex to find patterns like "6 years experience"
- Extract maximum years mentioned
```

### 4. ATS Score
```
- Check for: email, phone, education, experience sections
- Positive: Has bullet points, links, grades
- Negative: Too short/long, contains images
```

---

## Troubleshooting

**Q: Demo button not working?**
A: Make sure you're using the updated app.py. Close and restart.

**Q: Scores are low?**
A: The algorithm is working correctly. Mike Chen has no formal experience, hence lower score.

**Q: PDF not downloading?**
A: Make sure reportlab is installed. Run: `pip install reportlab`

---

## Quick Test (Before Presentation)

1. Double-click START_DEMO.bat
2. Click "🚀 Load Sample Data"
3. Click "🚀 Initiate Neural Analysis"
4. Verify:
   - John Smith shows ~80% with 6 years experience
   - Sara Johnson shows ~65% with 4 years experience
   - Mike Chen shows ~30% with 0 years experience
   - ATS scores around 60-80%
   - Score breakdown chart visible in Deep Analysis tab
