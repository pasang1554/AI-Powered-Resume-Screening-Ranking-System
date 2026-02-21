# Weekly Progress Logs - Smart Resume Matcher

This document tracks the weekly progress and milestones achieved during the development of the Smart Resume Matcher project.

---

### **Week 1: Project Identification & Concept Definition**
**Status**: Completed  
**Work carried out**:  
Conducted an initial brain-storming session to identify challenges in the modern recruitment process, focusing on the high volume of resumes received by HR. Defined the core objective of building an AI-powered screening tool that automates resume shortlisting. Researched the fundamentals of Applicant Tracking Systems (ATS) and how they process candidate data. Finalized the project scope to include both quantitative match scores and qualitative AI-based insights.

### **Week 2: Literature Survey & Feasibility Study**
**Status**: Completed  
**Work carried out**:  
Performed a literature survey on various Natural Language Processing (NLP) techniques like keyword matching and semantic analysis. Evaluated existing tools and research papers related to resume parsing and ranking algorithms. Studied the effectiveness of Cosine Similarity versus Euclidean distance for text comparison tasks. Documented the feasibility of using Python-based libraries for text extraction and machine learning.

### **Week 3: Tech Stack Selection & Environment Setup**
**Status**: Completed  
**Work carried out**:  
Finalized the technology stack, selecting Python as the primary language and Streamlit for a fast, interactive web interface. Configured the local development environment and initialized a Git repository for version control. Identified essential libraries such as `scikit-learn` for TF-IDF, `nltk` for preprocessing, and `PyPDF2` for PDF handling. Created the `requirements.txt` file and installed all necessary dependencies.

### **Week 4: Logical Architecture & Data Flow Design**
**Status**: Completed  
**Work carried out**:  
Designed the high-level architecture of the application, mapping out the flow from file upload to final ranking. Created a logical flowchart for text preprocessing steps including tokenization, normalization, and stopword removal. Planned the UI layout with a focus on user experience, deciding on a sidebar for controls and tabs for results. Drafted the data structure for storing temporary resume data and job description parameters.

### **Week 5: PDF Parsing & Text Extraction Logic**
**Status**: Completed  
**Work carried out**:  
Implemented the core text extraction module using the `PyPDF2` library to handle different PDF formats. Developed robust error-handling mechanisms to manage corrupted files or non-selectable text layouts. Integrated the `nltk` library to clean the extracted text by removing noise, special characters, and common English stopwords. Verified the extraction accuracy across multiple sample resumes with varying structures.

### **Week 6: Development of Similarity Engine (NLP)**
**Status**: Completed  
**Work carried out**:  
Developed the quantitative matching engine using **TF-IDF Vectorization** to convert text into numerical vectors. Implemented the **Cosine Similarity** algorithm to calculate the mathematical overlap between resumes and job descriptions. Fine-tuned the vectorization parameters to prioritize rare technical skills over common corporate terminology. Tested the engine against controlled datasets to ensure the ranking logic was fair and accurate.

### **Week 7: UI Construction & Dashboard Development**
**Status**: Completed  
**Work carried out**:  
Built the interactive web dashboard using Streamlit, incorporating a professional dark theme. Developed custom CSS modules for glassmorphism-styled KPI cards to display metrics like average scores and shortlist counts. Created the "Rankings Table" with dynamic progress bars and sorting capabilities for better data visualization. Implemented a success threshold slider in the sidebar to allow recruiters to filter candidates in real-time.

### **Week 8: Groq AI & Llama 3.1 Integration**
**Status**: Completed  
**Work carried out**:  
Integrated the **Groq API** to leverage the **Llama 3.1** Large Language Model for qualitative resume evaluation. Developed custom AI prompts that act as an "Expert Recruiter" to analyze candidate strengths, weaknesses, and seniority. Implemented an "ATS Friendliness Check" module that provides specific feedback on resume optimization. Fixed latency issues by optimizing the API calling frequency and implementing effective session state management in Streamlit.

### **Week 9: Feature Refinement & Deep Analysis Tabs**
**Status**: Completed  
**Work carried out**:  
Enhanced the "Detailed Analysis" tab by adding missing skill tags and status badges (e.g., "Ready to Hire"). Optimized the missing skills identification logic to cross-reference job requirements more accurately. Implemented the "Inbox Export" logic, allowing users to download the full ranking report as a CSV file. Conducted a UI polish to ensure consistent spacing, typography, and responsive design across different screen resolutions.

### **Week 10: Final Testing, Documentation & Viva Prep**
**Status**: Completed  
**Work carried out**:  
Conducted end-to-end system testing with a diverse batch of 20+ resumes to ensure stability and accuracy. Finalized the `PROJECT_REPORT.md` including technical explanations and architectural diagrams. Prepared a comprehensive `VIVA_SCRIPT.md` with probable questions and presentation tips. Completed the project documentation and packaged the final source code for submission.
