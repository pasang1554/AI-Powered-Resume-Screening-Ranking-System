import numpy as np
import re
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from collections import Counter

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

SKILL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "ruby",
    "go",
    "rust",
    "react",
    "angular",
    "vue",
    "node.js",
    "nodejs",
    "django",
    "flask",
    "fastapi",
    "spring",
    "express",
    "next.js",
    "nextjs",
    "html",
    "css",
    "sass",
    "tailwind",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "elasticsearch",
    "cassandra",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "jenkins",
    "ci/cd",
    "terraform",
    "git",
    "github",
    "gitlab",
    "jira",
    "agile",
    "scrum",
    "kanban",
    "machine learning",
    "ml",
    "deep learning",
    "tensorflow",
    "pytorch",
    "keras",
    "data science",
    "pandas",
    "numpy",
    "scikit-learn",
    "nlp",
    "computer vision",
    "rest api",
    "graphql",
    "microservices",
    "api",
    "backend",
    "frontend",
    "fullstack",
    "linux",
    "unix",
    "bash",
    "shell scripting",
    "networking",
    "security",
    "tableau",
    "power bi",
    "excel",
    "data analysis",
    "statistics",
    "flutter",
    "react native",
    "ios",
    "android",
    "mobile development",
    "tensorflow",
    "spark",
    "hadoop",
    "kafka",
    "data engineering",
    "communication",
    "leadership",
    "problem solving",
    "teamwork",
    "project management",
}


def clean_text(text: str) -> str:
    text = re.sub(r"[^a-zA-Z\s]", " ", text.lower())
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found_skills = []

    for skill in SKILL_KEYWORDS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            s_low = skill.lower()
            if s_low in ["fastapi", "nodejs", "nextjs"]:
                res = s_low.replace("api", "API").replace("js", "JS")
                res = res[0].upper() + res[1:]
                found_skills.append(res)
            elif len(s_low) <= 3 or s_low in ["html", "css", "sql", "aws", "gcp", "ci/cd"]:
                found_skills.append(s_low.upper())
            else:
                found_skills.append(s_low.title())

    return list(set(found_skills))





def calculate_tfidf_similarity(text1: str, text2: str) -> float:
    clean1 = clean_text(text1)
    clean2 = clean_text(text2)

    if not clean1 or not clean2:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([clean1, clean2])

        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity * 100), 2)
    except Exception:
        return 0.0


def calculate_skill_depth(text: str, skills: List[str]) -> float:
    if not skills:
        return 0.0

    text_lower = text.lower()
    depth_indicators = [
        "senior",
        "lead",
        "expert",
        "advanced",
        "proficient",
        "intermediate",
        "years",
        "yr",
        "experience",
        "developed",
        "implemented",
        "designed",
        "architected",
        "managed",
        "created",
        "built",
        "led",
        "mentored",
    ]

    indicator_count = sum(1 for ind in depth_indicators if ind in text_lower)
    base_depth = min(len(skills) * 1.5, 10)
    depth_score = base_depth + (indicator_count * 0.3)

    return round(min(depth_score, 10.0), 1)


def find_missing_skills(
    required_skills: List[str], candidate_skills: List[str]
) -> List[str]:
    required_set = {s.lower() for s in required_skills}
    candidate_set = {s.lower() for s in candidate_skills}
    return list(required_set - candidate_set)


def detect_bias(text: str) -> List[str]:
    bias_indicators = []

    gendered_terms = {
        "he": "Gendered pronoun usage",
        "she": "Gendered pronoun usage",
        "him": "Gendered pronoun usage",
        "her": "Gendered pronoun usage",
        "his": "Gendered pronoun usage",
        "guys": "Gendered term",
        "boys": "Gendered term",
        "girls": "Gendered term",
        "chairman": "Gendered title",
        "salesman": "Gendered title",
        "stewardess": "Gendered title",
        "young": "Age-related term",
        "energetic": "Age-related term",
        "recent graduate": "Age-related term",
    }

    text_lower = text.lower()
    for term, category in gendered_terms.items():
        if f" {term} " in f" {text_lower} " or f" {term}." in text_lower:
            if category not in bias_indicators:
                bias_indicators.append(category)

    return bias_indicators


def analyze_resume(job_description: str, resume_text: str) -> Dict[str, Any]:
    required_skills = extract_skills(job_description)
    candidate_skills = extract_skills(resume_text)

    similarity_score = calculate_tfidf_similarity(job_description, resume_text)
    skill_depth = calculate_skill_depth(resume_text, candidate_skills)
    missing_skills = find_missing_skills(required_skills, candidate_skills)
    bias_flags = detect_bias(resume_text)

    depth_bonus = min(skill_depth * 2, 10)
    bias_penalty = len(bias_flags) * 5
    final_score = max(0, min(100, similarity_score + depth_bonus - bias_penalty))

    return {
        "match_score": round(final_score, 2),
        "semantic_similarity": similarity_score,
        "skill_depth": skill_depth,
        "required_skills": required_skills,
        "matched_skills": candidate_skills,
        "missing_skills": missing_skills,
        "bias_indicators": bias_flags,
        "status": "shortlisted" if final_score >= 65 else "not_selected",
    }


def generate_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not results:
        return {}

    scores = [r["match_score"] for r in results]

    return {
        "total_candidates": len(results),
        "shortlisted": sum(1 for r in results if r["status"] == "shortlisted"),
        "average_score": round(np.mean(scores), 2),
        "max_score": round(max(scores), 2),
        "min_score": round(min(scores), 2),
        "top_skills": list(
            set(skill for r in results for skill in r.get("matched_skills", []))
        )[:10],
    }
