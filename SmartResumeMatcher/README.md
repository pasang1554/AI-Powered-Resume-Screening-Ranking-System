# 🧠 Smart Resume Matcher (SaaS Edition)

**AI-Powered Resume Screening & Ranking System**

## 🚀 Project Overview
A modern, Streamlit-based HR Dashboard that automates the resume screening process using Natural Language Processing (NLP). It compares candidate resumes against a job description (JD) to calculate match scores, identify missing skills, and rank candidates instantly.

## ✨ Key Features
- **📊 Interactive Dashboard**: A professional dark-themed UI with KPI cards and glassmorphism styling.
- **🛠️ Sidebar Controls**: Easy access to file uploads and settings (Threshold Slider).
- **📉 Advanced Analytics**:
    - **Overview Tab**: Key metrics (Total Candidates, Shortlisted, Avg Score).
    - **Rankings Tab**: Sortable data table with progress bars.
    - **Detailed Tab**: Deep-dive analysis with missing skill tags and status badges.
- **Inbox Export Logic**: Download the full ranking report as a CSV file.
- **🧠 NLP Engine**: Uses TF-IDF and Cosine Similarity for accurate text matching.
- **🤖 AI Integration**:
    - **Expert Evaluation**: Provides a qualitative "Ready to Hire" assessment.
    - **ATS Check**: Scores resumes on ATS friendliness.
    - **Deep Insights**: Lists strengths, weaknesses, and missing critical skills using **Llama 3.1**.



## 🛠️ Installation

1. **Clone the repository** (if applicable) or download the files.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python -m streamlit run app.py
   ```

## 💡 How to Use
1. **Upload Resumes**: Drag & drop PDF resumes in the **Sidebar**.
2. **Input JD**: Paste the Job Description in the main text area.
3. **Set Threshold**: Adjust the success threshold slider in the sidebar (default: 60%).
4. **Analyze**: Click the "Analyze Candidates" button.
5. **Explore Results**: Switch between the "Overview", "Ranking Table", and "Detailed Analysis" tabs.

## 📁 Project Structure
- `app.py`: Main application logic (UI, Layout, Visuals).
- `utils.py`: Core NLP functions (Text Extraction, Cleaning, Similarity Calculation).
- `requirements.txt`: List of dependencies.
- `PROJECT_REPORT.md`: Techincal documentation and viva preparation.

---
*Developed for Mini Project | CSE Department*
