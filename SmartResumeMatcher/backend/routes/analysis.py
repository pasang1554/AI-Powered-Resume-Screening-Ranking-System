from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
import io
import re

from backend.database import get_db
from backend.models import User, JobDescription, Candidate, Analysis
from backend.schemas import AnalysisRequest, AnalysisResult
from backend.routes.dependencies import get_current_user, log_action

router = APIRouter(prefix="/analyze", tags=["Resume Analysis"])

@router.post("/pdf")
async def analyze_pdf_resumes(
    job_description: str = Form(...),
    threshold: float = Form(65.0),
    groq_api_key: Optional[str] = Form(None),
    weighted_skills: Optional[List[str]] = Form(None),
    blind_hiring: bool = Form(False),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from utils import (
        extract_text_from_pdf,
        calculate_detailed_match,
        calculate_ats_score,
        detect_experience_years,
        extract_semantic_skills,
        evaluate_resume_with_groq,
        generate_skill_radar_data,
        redact_pii
    )
    
    results = []
    # Extract a professional title from the JD content (first non-empty line, stripping symbols)
    desc_lines = [l.strip() for l in job_description.split('\n') if l.strip()]
    raw_title = desc_lines[0] if desc_lines else f"Analysis {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    jd_title = re.sub(r"[#*_\[\]]", "", raw_title)[:60].strip()

    jd = JobDescription(
        user_id=current_user.id,
        title=jd_title,
        content=job_description,
        threshold=threshold,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)

    # Initialize Groq client once
    client = None
    if groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
        except Exception:
            pass

    groq_semaphore = asyncio.Semaphore(3)

    async def process_file(f):
        file_bytes = await f.read()
        
        def cpu_bound_analysis():
            file_obj = io.BytesIO(file_bytes)
            filename_lower = f.filename.lower()
            if filename_lower.endswith(".pdf"):
                text = extract_text_from_pdf(file_obj)
            else:
                try: text = file_bytes.decode("utf-8", errors="ignore")
                except: text = None
            
            if not text or len(text) <= 50: return None
                
            detailed = calculate_detailed_match(job_description, text, weighted_skills=weighted_skills)
            ats = calculate_ats_score(text)
            exp = detect_experience_years(text)
            req_skills = extract_semantic_skills(job_description)
            cand_skills = detailed.get("all_resume_skills", [])
            missing = list(set(req_skills) - set([s.lower() for s in cand_skills]))
            status = "Shortlisted" if detailed["total"] >= threshold else "Not Selected"
            radar_data = generate_skill_radar_data(job_description, text)
            
            return text, detailed, ats, exp, cand_skills, missing, status, radar_data

        analysis_data = await asyncio.to_thread(cpu_bound_analysis)
        if not analysis_data: return None
        text, detailed, ats, exp, cand_skills, missing, status, radar_data = analysis_data

        ai_eval = None
        if client:
            try:
                async with groq_semaphore:
                    processed_text = redact_pii(text) if blind_hiring else text
                    final_text = processed_text[:8000] if processed_text else ""
                    ai_eval = await asyncio.to_thread(evaluate_resume_with_groq, client, job_description, final_text)
            except Exception as e:
                # Log the specific AI failure but allow basic analysis to proceed
                print(f"Neural evaluation failed for {f.filename}: {e}")
                ai_eval = {"error": "AI evaluation core encountered an anomaly. Proceeding with base metrics."}
                    
        return {
            "filename": f.filename,
            "text": text,
            "detailed": detailed,
            "ats": ats,
            "exp": exp,
            "cand_skills": cand_skills,
            "missing": missing,
            "status": status,
            "ai_eval": ai_eval,
            "file_bytes": file_bytes,
            "radar_data": radar_data
        }

    tasks_results = await asyncio.gather(*(process_file(f) for f in files))

    for res in tasks_results:
        if not res: continue
            
        existing_cand = None
        cand_email = res["detailed"].get("email")
        if cand_email:
            existing_cand = db.query(Candidate).filter(Candidate.email == cand_email).first()
        
        if existing_cand:
            cand = existing_cand
            log_action(db, current_user.id, f"Cross-referenced Duplicate: {cand.name}", "DeDuplication", {"email": cand_email})
        else:
            cand = Candidate(
                job_description_id=jd.id,
                name=res["filename"].replace(".pdf", "").replace(".txt", ""),
                email=cand_email,
                resume_text=res["text"],
                resume_filename=res["filename"],
                resume_data=res["file_bytes"],
                skills=res["cand_skills"]
            )
            db.add(cand)
            db.commit()
            db.refresh(cand)
        
        analysis = Analysis(
            user_id=current_user.id,
            job_description_id=jd.id,
            candidate_id=cand.id,
            match_score=res["detailed"]["total"],
            semantic_similarity=res["detailed"].get("keyword_score", 0.0),
            skill_depth=res["detailed"].get("skill_score", 0.0),
            missing_skills=res["missing"][:5],
            matched_skills=res["cand_skills"][:6],
            status=res["status"],
            ai_evaluation=res["ai_eval"]
        )
        db.add(analysis)
        db.commit()

        log_action(db, current_user.id, f"Analyzed Resume: {cand.name}", "Analysis", {"match_score": res["detailed"]["total"]})

        results.append({
            "id": analysis.id,
            "candidate_id": cand.id,
            "Rank": 0,
            "Candidate": cand.name,
            "filename": cand.resume_filename,
            "Score": round(res["detailed"]["total"], 1),
            "Skill_Score": res["detailed"].get("skill_score", 0),
            "Exp_Score": res["detailed"].get("experience_score", 0),
            "KW_Score": res["detailed"].get("keyword_score", 0),
            "ATS": res["ats"],
            "Experience": res["exp"],
            "Skills_Count": len(res["cand_skills"]),
            "Missing": res["missing"][:5],
            "Missing_Count": len(res["missing"]),
            "Status": res["status"],
            "Top_Skills": res["cand_skills"][:6],
            "AI_Evaluation": res["ai_eval"],
            "resume_text": res["text"],
            "Email": res["detailed"].get("email"),
            "Real_Name": cand.name,
            "Radar_Data": res["radar_data"]
        })

    results = sorted(results, key=lambda x: x["Score"], reverse=True)
    for i, r in enumerate(results): r["Rank"] = i + 1

    return {
        "job_description_id": jd.id,
        "candidates": results,
        "summary": {"total_candidates": len(results)}
    }

@router.post("/coach")
async def get_ats_coaching(
    job_description: str = Form(...),
    resume_text: str = Form(...),
    groq_api_key: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    from utils import generate_ats_coaching
    from groq import Groq
    try:
        client = Groq(api_key=groq_api_key)
        coaching = await asyncio.to_thread(generate_ats_coaching, client, job_description, resume_text)
        return coaching
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/scorecard")
async def get_interview_scorecard(
    job_description: str = Form(...),
    groq_api_key: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    from utils import generate_interview_scorecard
    from groq import Groq
    try:
        client = Groq(api_key=groq_api_key)
        scorecard = await asyncio.to_thread(generate_interview_scorecard, client, job_description)
        return scorecard
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate")
async def api_simulate_candidate(
    candidate_id: int = Form(...),
    groq_api_key: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Phase 8: Autonomous Roleplay Simulator.
    Generates a simulated interview conversation based on candidate profile.
    """
    from groq import Groq
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand: raise HTTPException(status_code=404, detail="Candidate not found")
        
    jd_content = cand.job_description.content
    resume_text = cand.resume_text
    
    prompt = f"Roleplay as {cand.name}. JD: {jd_content}. Resume: {resume_text}. Predict 3 challenging interview questions you would struggle with and 3 you would excel at."
    
    try:
        client = Groq(api_key=groq_api_key)
        response = await asyncio.to_thread(client.chat.completions.create,
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return {"simulation": response.choices[0].message.content}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{analysis_id}")
async def export_candidate_intelligence(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Exports a high-fidelity PDF report for a specific candidate analysis.
    """
    from utils import generate_intelligence_report_pdf
    
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found")
        
    if not analysis.ai_evaluation:
        raise HTTPException(status_code=400, detail="Deep AI Evaluation not found for this candidate. Run analysis with Groq key first.")
        
    candidate_name = analysis.candidate.name
    jd_title = analysis.job_description.title
    score = analysis.match_score
    ai_eval = analysis.ai_evaluation
    
    pdf_content = generate_intelligence_report_pdf(candidate_name, jd_title, score, ai_eval)
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=intelligence_report_{candidate_name.replace(' ', '_')}.pdf"}
    )
