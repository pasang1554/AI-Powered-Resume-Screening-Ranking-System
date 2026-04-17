# 🌌 Smart Resume Matcher (Universal Singularity Edition v8.1)

**AI-Powered Strategic Recruitment & Global Talent Singularity**

## 🚀 Project Overview
A world-class, institutional-grade recruitment intelligence platform. Evolving from a simple matcher into a unified **Talent Singularity**, the system manages the entire organizational life-cycle—from autonomous screening to global succession foresight.

## ✨ Key Features (v8.1 Singularity Suite)
- **🎭 Role-Adaptive UI**: Persona-based interface (Operator, Architect, Strategist) that dynamically reconfigures tools based on user context.
- **🧠 Intelligence Deep-Dive**: Groq-powered qualitative analysis including ATS Coaching, Interview Scorecards, and Candidate Roleplay Simulations.
- **🌍 Public Career Portal**: An unauthenticated application gateway for external talent with autonomous AI ingestion.
- **🤝 Strategic Interview Orchestration**: Integrated session management with .ics calendar export and institutional feedback loops.
- **📊 Institutional Insights Dashboard**: High-fidelity analytics covering Skill Scarcity, Recruitment ROI, and Quantum Workforce Roadmaps.
- **📥 Intelligence PDF Export**: Branded report generation for candidate profiles and AI verdicts.
- **🛡️ Neural Safeguards**: Blind hiring mode to redact PII and ensure ethical talent discovery.

## 🛠️ Installation & Boot-Sequence

### Option A: Local Development (Manual)
1. **System Preparation**:
   ```bash
   pip install -r requirements-api.txt
   pip install -r requirements-frontend.txt
   ```
2. **Launch Services**:
   - Backend: `uvicorn backend.main:app --reload`
   - Frontend: `streamlit run app.py`

### Option B: Production Deployment (Docker)
1. **Orchestrate via Compose**:
   ```bash
   docker-compose up --build
   ```
   *This launches the Backend (Port 8000) and Frontend (Port 8501) as isolated services.*

### Option C: Institutional Quality Assurance (Tests)
1. **Run Full Suite**:
   ```bash
   ./scripts/test_runner.sh
   ```
   *Verifies core intelligence logic and API stability with coverage reporting.*



## 📁 Project Architecture
- `app.py`: The Recruitment nervous system (UI, Navigation, Logic).
- `utils.py`: Semantic intelligence and signal extraction layer.
- `backend/`: High-performance FastAPI orchestration and DB persistence.
- `PROJECT_REPORT.md`: Comprehensive technical thesis for academic submission.

---
*Developed for Mini Project | CSE Department | Universal Singularity Phase*
