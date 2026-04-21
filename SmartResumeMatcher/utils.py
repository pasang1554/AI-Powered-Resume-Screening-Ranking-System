import PyPDF2
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import json
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

# Download necessary NLTK data
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")
try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")

# Initialize lemmatizer and stop words
lemmatizer = WordNetLemmatizer()

try:
    GLOBAL_STOP_WORDS = set(stopwords.words("english"))
except Exception:
    GLOBAL_STOP_WORDS = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
        "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", 
        "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", 
        "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", 
        "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
        "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", 
        "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", 
        "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", 
        "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", 
        "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", 
        "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
    }

# Comprehensive tech skills taxonomy for semantic extraction
TECH_SKILLS_TAXONOMY = {
    "programming": [
        "python",
        "java",
        "javascript",
        "js",
        "typescript",
        "ts",
        "c++",
        "c#",
        "c",
        "go",
        "golang",
        "rust",
        "swift",
        "kotlin",
        "scala",
        "ruby",
        "php",
        "perl",
        "r",
        "matlab",
        "vba",
        "dart",
        "julia",
        "lua",
        "haskell",
        "clojure",
        "erlang",
        "elixir",
        "f#",
    ],
    "web_frontend": [
        "react",
        "angular",
        "vue",
        "svelte",
        "html",
        "css",
        "sass",
        "less",
        "bootstrap",
        "tailwind",
        "jquery",
        "redux",
        "webpack",
        "babel",
        "next.js",
        "nuxt.js",
        "gatsby",
        "material-ui",
        "antd",
        "styled-components",
    ],
    "web_backend": [
        "node.js",
        "nodejs",
        "express",
        "django",
        "flask",
        "fastapi",
        "spring",
        "spring boot",
        "rails",
        "laravel",
        "asp.net",
        "graphql",
        "rest api",
        "microservices",
        "serverless",
        "aws lambda",
        "docker",
        "kubernetes",
        "nginx",
        "apache",
    ],
    "data_science": [
        "machine learning",
        "ml",
        "deep learning",
        "dl",
        "tensorflow",
        "pytorch",
        "keras",
        "scikit-learn",
        "sklearn",
        "pandas",
        "numpy",
        "scipy",
        "matplotlib",
        "seaborn",
        "plotly",
        "jupyter",
        "rstudio",
        "statistics",
        "hypothesis testing",
        "a/b testing",
        "regression",
        "classification",
        "clustering",
        "neural networks",
        "nlp",
        "computer vision",
    ],
    "databases": [
        "sql",
        "mysql",
        "postgresql",
        "postgres",
        "mongodb",
        "nosql",
        "redis",
        "elasticsearch",
        "cassandra",
        "dynamodb",
        "sqlite",
        "oracle",
        "mssql",
        "firebase",
        "supabase",
        "prisma",
        "sequelize",
        "hibernate",
    ],
    "devops_cloud": [
        "aws",
        "azure",
        "gcp",
        "google cloud",
        "docker",
        "kubernetes",
        "k8s",
        "jenkins",
        "gitlab ci",
        "github actions",
        "terraform",
        "ansible",
        "puppet",
        "chef",
        "prometheus",
        "grafana",
        "elk stack",
        "ci/cd",
        "devops",
        "sre",
    ],
    "mobile": [
        "ios",
        "android",
        "react native",
        "flutter",
        "xamarin",
        "cordova",
        "ionic",
        "swift",
        "objective-c",
        "java android",
        "kotlin android",
    ],
    "soft_skills": [
        "leadership",
        "communication",
        "teamwork",
        "problem solving",
        "critical thinking",
        "project management",
        "agile",
        "scrum",
        "kanban",
        "jira",
        "confluence",
        "stakeholder management",
        "mentoring",
        "collaboration",
    ],
}

# Flatten taxonomy for easy lookup
ALL_SKILLS = []
for category in TECH_SKILLS_TAXONOMY.values():
    ALL_SKILLS.extend(category)

# Bias indicators to check
BIAS_INDICATORS = {
    "gendered_language": [
        "rockstar",
        "ninja",
        "guru",
        "wizard",
        "hero",
        "dominant",
        "aggressive",
        "competitive",
        "ambitious",
        "confident",
        "independent",
        "superior",
    ],
    "age_bias": [
        "young",
        "energetic",
        "fresh",
        "recent graduate",
        "digital native",
        "millennial",
        "gen z",
        "junior",
        "senior",  # context-dependent
    ],
    "cultural_bias": ["native english", "western", "local", "cultural fit"],
}


def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from a PDF file with enhanced error handling.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        str: Extracted text or None if extraction fails
    """
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return None


def extract_email(text):
    """
    Extracts the first email address found in the text using a standard regex.

    Args:
        text (str): Input text

    Returns:
        str: Extracted email address or None if not found
    """
    if not text:
        return None
    
    # Standard email regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    if match:
        return match.group(0)
    return None


def clean_text(text):
    """
    Advanced text cleaning with lemmatization.

    Args:
        text (str): Raw input text

    Returns:
        str: Cleaned text
    """
    # Convert to lowercase
    text = text.lower()

    # Remove special characters but preserve spaces
    text = re.sub(r"[^a-zA-Z0-9+.#\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def calculate_similarity(job_description, resume_text):
    """
    Calculates match score using skill-based matching + text similarity.

    Args:
        job_description (str): Job description text
        resume_text (str): Resume text

    Returns:
        float: Match score (0-100)
    """
    try:
        # Clean texts
        jd_clean = clean_text(job_description)
        resume_clean = clean_text(resume_text)

        # Extract skills from both
        jd_skills = extract_semantic_skills(job_description)
        resume_skills = extract_semantic_skills(resume_text)

        # Calculate skill match percentage
        if jd_skills:
            matched_skills = [s for s in jd_skills if s.lower() in resume_clean.lower()]
            skill_match_score = (
                len(matched_skills) / len(jd_skills)
            ) * 60  # 60% weight
        else:
            skill_match_score = 0

        # TF-IDF text similarity (40% weight)
        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000,
                min_df=1,
                max_df=1.0,
            )
            content = [jd_clean, resume_clean]
            tfidf_matrix = vectorizer.fit_transform(content)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            text_similarity = float(similarity) * 40  # 40% weight
        except:
            text_similarity = 0

        # Keyword matching bonus (bonus points for important keywords)
        important_keywords = [
            "python",
            "java",
            "javascript",
            "react",
            "aws",
            "docker",
            "kubernetes",
            "sql",
            "postgresql",
            "mongodb",
            "git",
            "agile",
        ]
        jd_lower = job_description.lower()
        resume_lower = resume_text.lower()

        keyword_bonus = 0
        for keyword in important_keywords:
            if keyword in jd_lower and keyword in resume_lower:
                keyword_bonus += 2

        final_score = min(100, skill_match_score + text_similarity + keyword_bonus)

        return round(final_score, 1)

    except Exception as e:
        print(f"Error in calculate_similarity: {e}")
        return 0.0


def extract_semantic_skills(text):
    """
    Extracts skills from text using the comprehensive taxonomy.
    Uses regex word boundaries for precise matching and n-gram analysis
    for compound skills (e.g., "machine learning").

    Complexity: O(n×m) where n=text length, m=skill count

    Args:
        text (str): Input text

    Returns:
        list: Sorted list of matched skills
    """
    text_lower = text.lower()
    found_skills = set()

    # Direct matching from taxonomy
    for skill in ALL_SKILLS:
        # Use word boundaries for better matching
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    # Additional extraction using NLP
    tokens = word_tokenize(clean_text(text))

    stop_words = GLOBAL_STOP_WORDS

    # Look for compound skills (e.g., "machine learning")
    bigrams = [f"{tokens[i]} {tokens[i + 1]}" for i in range(len(tokens) - 1)]
    trigrams = [
        f"{tokens[i]} {tokens[i + 1]} {tokens[i + 2]}" for i in range(len(tokens) - 2)
    ]

    for ngram in bigrams + trigrams:
        if ngram in ALL_SKILLS:
            found_skills.add(ngram)

    return sorted(list(found_skills))


def calculate_skill_depth(resume_text, skills_list):
    """
    Calculates a skill depth score based on:
    - Frequency of skill mentions (diminishing returns)
    - Context around mentions (years, projects)
    - Experience indicators ("expert", "advanced", "5 years")

    Returns score 0-10

    Args:
        resume_text (str): Full resume text
        skills_list (list): List of skills to evaluate

    Returns:
        float: Depth score (0-10)
    """
    if not skills_list:
        return 0.0

    text_lower = resume_text.lower()
    depth_score = 0

    for skill in skills_list:
        # Count occurrences
        count = len(re.findall(r"\b" + re.escape(skill.lower()) + r"\b", text_lower))

        # Look for experience indicators
        experience_patterns = [
            r"(\d+)\+?\s*years?\s*(?:of)?\s*experience.*?\b" + re.escape(skill.lower()),
            r"\b" + re.escape(skill.lower()) + r".*?\d\+?\s*years?",
            r"expert\s*(?:in)?\s*\b" + re.escape(skill.lower()),
            r"advanced\s*(?:in)?\s*\b" + re.escape(skill.lower()),
            r"proficient\s*(?:in)?\s*\b" + re.escape(skill.lower()),
        ]

        for pattern in experience_patterns:
            if re.search(pattern, text_lower):
                depth_score += 2  # Bonus for experience indicators
                break

        # Add frequency-based score (diminishing returns)
        depth_score += min(count * 0.5, 2)

    # Normalize to 0-10 scale
    normalized_score = min(10, depth_score / max(len(skills_list), 1) * 2)
    return round(normalized_score, 1)


def find_missing_skills(job_description, resume_text):
    """
    Identifies required skills from JD that are missing in resume.

    Args:
        job_description (str): Job description text
        resume_text (str): Resume text

    Returns:
        list: Missing skills
    """
    required_skills = extract_semantic_skills(job_description)
    candidate_skills = extract_semantic_skills(resume_text)

    # Find missing skills
    missing = []
    for skill in required_skills:
        if skill not in candidate_skills:
            # Check for partial matches (e.g., "react" vs "react.js")
            partial_match = False
            for cs in candidate_skills:
                if skill in cs or cs in skill:
                    partial_match = True
                    break
            if not partial_match:
                missing.append(skill)

    return missing


def detect_bias_indicators(text):
    """
    Detects potential bias indicators in resume text.
    Categories: gendered_language, age_bias, cultural_bias

    Args:
        text (str): Input text

    Returns:
        list: Flagged terms with categories
    """
    text_lower = text.lower()
    flags = []

    for category, terms in BIAS_INDICATORS.items():
        for term in terms:
            if term in text_lower:
                flags.append(f"{category}:{term}")

    return flags


def generate_skill_radar_data(job_description, resume_text):
    """
    Generates data for skill radar chart comparing JD requirements vs candidate skills.

    Args:
        job_description (str): Job description
        resume_text (str): Resume text

    Returns:
        dict: Radar chart data with categories and scores
    """
    categories = list(TECH_SKILLS_TAXONOMY.keys())

    jd_skills = extract_semantic_skills(job_description)
    resume_skills = extract_semantic_skills(resume_text)

    jd_scores = []
    resume_scores = []

    for category in categories:
        category_skills = TECH_SKILLS_TAXONOMY[category]

        jd_count = len([s for s in jd_skills if s in category_skills])
        resume_count = len([s for s in resume_skills if s in category_skills])

        # Normalize scores (0-100)
        jd_scores.append(min(jd_count * 20, 100))
        resume_scores.append(min(resume_count * 20, 100))

    return {
        "categories": categories,
        "job_description": jd_scores,
        "candidate": resume_scores,
    }


def safe_json_loads(text):
    """
    Attempts to clean and parse JSON from LLM responses more robustly.
    """
    if not text:
        return {"error": "Empty response"}
    
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # Attempt to find JSON block with regex
    json_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if json_match:
        try:
            # Clean up common LLM artifacts like trailing commas or non-standard escapes
            clean_json = json_match.group(1).replace(",\n}", "\n}").replace(",}", "}")
            return json.loads(clean_json)
        except:
            pass

    # Final attempt: manual cleanup of newlines inside strings or common mistakes
    try:
        # This is a risky broad cleanup but helps in some cases
        fixed_text = text.strip()
        if not fixed_text.startswith("{") and "{" in fixed_text:
            fixed_text = fixed_text[fixed_text.find("{"):]
        if not fixed_text.endswith("}") and "}" in fixed_text:
            fixed_text = fixed_text[:fixed_text.rfind("}")+1]
        return json.loads(fixed_text)
    except:
        return {"error": "Failed to parse JSON core", "raw": text[:200]}

def evaluate_resume_with_groq(client, job_description, resume_text):
    """
    Evaluates a resume against a job description using the GROQ API.
    Includes retry logic with exponential backoff for handling rate limits (429).

    Args:
        client (Groq): Initialized Groq client
        job_description (str): Job Description text
        resume_text (str): Resume text

    Returns:
        dict: Parsed JSON response from the LLM
    """
    import time
    import random

    system_prompt = """You are an Advanced Multilingual ATS (Applicant Tracking System).
Your task is to analyze the relationship between a Job Description (JD) and a Resume content.

GLOBAL INTELLIGENCE RULES:
1. MULTILINGUAL SUPPORT: The Resume may be in any language (Spanish, French, German, Hindi, etc.). You must accurately translate and understand the candidate's experience in the context of the English Job Description.
2. SEMANTIC CORRELATION: Focus on underlying skills and impact even if terminologies differ across languages.
3. BLIND HIRING: If PII is redacted, strictly ignore demographics and focus only on competence.

Return output strictly in JSON format:
{
    "match_score": <number 0-100>,
    "hiring_status": "<'Ready to Hire' | 'Not Ready'>",
    "ats_friendly_score": <number 0-100>,
    "summary": "<2-sentence executive summary in English>",
    "strengths": ["<top strength 1>", ...],
    "weaknesses": ["<top weakness 1>", ...],
    "recommendation": "<verdict>",
    "custom_interview_questions": ["<top q1>", ...],
    "red_flags": ["<hr red flag or 'None'>"],
    "market_value": "<salary range>",
    "resume_language": "<detected language>"
}
"""

    user_prompt = f"""
    Job Description:
    {job_description}
    
    Candidate Resume (Truncated for API Context):
    {resume_text[:10000]}
    """

    max_retries = 3
    base_delay = 2  # seconds

    for attempt in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=600,
                top_p=1,
                stream=False,
                stop=None,
            )

            response_content = completion.choices[0].message.content
            return safe_json_loads(response_content)

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg and attempt < max_retries:
                # Exponential backoff with jitter
                delay = (base_delay * (2 ** attempt)) + (random.random() * 1.5)
                print(f"Rate limit hit. Retrying in {delay:.2f} seconds (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(delay)
                continue
            
            return {"error": error_msg}


def generate_ats_coaching(client, job_description, resume_text):
    """
    Generates personalized ATS coaching and improvement tips for a candidate.
    
    Args:
        client (Groq): Initialized Groq client
        job_description (str): Job Description text
        resume_text (str): Resume text

    Returns:
        dict: Coaching tips and improvement plan
    """
    import time
    import random

    system_prompt = """You are a professional Career Coach and Resume Expert.
Your goal is to provide highly specific, actionable advice to help a candidate improve their resume for a specific Job Description.
Be encouraging but critical. Focus on:
1. Missing technical skills that are in the JD.
2. Formatting and ATS readability.
3. Quantifying achievements (using metrics/percentages).
4. Keywords that should be emphasized.

Return output strictly in JSON format with:
{
    "overall_feedback": "<brief motivational summary>",
    "critical_fixes": ["<fix 1>", ...],
    "suggested_additions": ["<skill or project to add>", ...],
    "formatting_tips": ["<tip 1>", ...],
    "impact_statements": ["<example of how to rewrite a bullet point to show impact>", ...]
}
"""

    user_prompt = f"""
    Job Description:
    {job_description}
    
    Candidate Resume:
    {resume_text}
    """

    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
                max_tokens=800,
            )

            response_content = completion.choices[0].message.content
            return safe_json_loads(response_content)

        except Exception as e:
            if "429" in str(e) and attempt < max_retries:
                time.sleep(base_delay * (2 ** attempt) + random.random())
                continue
            return {"error": str(e)}


def generate_interview_scorecard(client, job_description):
    """
    Generates a structured interview scorecard with specific evaluation criteria
    and scoring rubrics based on the Job Description.
    """
    system_prompt = """You are an Expert Technical Interviewer. 
Create a detailed, structured interview scorecard for the provided Job Description.
Return output strictly in JSON format:
{
    "evaluation_criteria": [
        {
            "category": "<e.g., Python Architecture>",
            "weight": <0.0-1.0>,
            "key_questions": ["<q1>", "<q2>"],
            "look_for": ["<indicator 1>", "<indicator 2>"]
        },
        ...
    ],
    "behavioral_questions": ["<q1>", "<q2>"],
    "overall_scorecard_notes": "<advice for the interviewer>"
}
"""
    user_prompt = f"Job Description:\n{job_description}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        response_content = completion.choices[0].message.content
        return safe_json_loads(response_content)
    except Exception as e:
        return {"error": str(e)}


def optimize_jd(client, raw_content):
    """
    Optimizes a raw JD for clarity, professionalism, and bias elimination.
    """
    system_prompt = """You are an Expert Recruitment Consultant. 
Enhance the provided raw job description content.
- Fix grammar and formatting.
- Ensure the tone is professional but welcoming.
- Remove any biased language.
- Structure logically: Summary, Responsibilities, Requirements.
Return ONLY the optimized text.
"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Raw Content:\n{raw_content}"},
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


def generate_jd(client, role_title, key_points):
    """
    Generates a full JD from a role title and brief key points.
    """
    system_prompt = """You are an Expert HR Professional.
Generate a comprehensive, high-quality Job Description based on the Title and Key Points provided.
Structure:
1. Role Summary
2. Core Responsibilities
3. Required Technical Skills
4. Soft Skills & Qualifications
5. Nice to Have
"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Title: {role_title}\nKey Points: {key_points}"},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


def simulate_candidate_response(client, resume_text, job_description, question):
    """
    Simulates a candidate's response to an interview question using their resume context.
    """
    system_prompt = f"""You are the candidate described in the provided Resume.
Your goal is to answer an interview question based on your experience and the Job Description.
Stay in character. Be professional, highlight your relevant skills, and be honest about your experience.
If the question is about a skill you don't have (based on the resume), acknowledge it but mention 
your willingness to learn or related skills.

MATCHING CONTEXT:
Job Description: {job_description}
"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Resume:\n{resume_text}\n\nInterviewer Question: {question}"},
            ],
            temperature=0.6,
            max_tokens=800,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error simulating response: {e}"


def generate_enterprise_brief(analyses_data, project_title, jd_content):
    """
    Generates a professional project-wide Recruitment Brief PDF.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"Recruitment Intelligence Brief: {project_title}", styles['Title']))
    story.append(Spacer(1, 12))

    # JD Summary
    story.append(Paragraph("Project Job Description", styles['Heading2']))
    jd_snippet = jd_content[:500] + "..." if jd_content else "No JD content provided."
    story.append(Paragraph(jd_snippet, styles['BodyText']))
    story.append(Spacer(1, 12))

    # Analytics Summary
    story.append(Paragraph("Pipeline Strategic Overview", styles['Heading2']))
    total = len(analyses_data)
    if total > 0:
        avg_score = sum(a.get('match_score', 0) for a in analyses_data) / total
        story.append(Paragraph(f"Total Candidates Analyzed: {total}", styles['BodyText']))
        story.append(Paragraph(f"Average Match Score: {avg_score:.1f}%", styles['BodyText']))
    else:
        story.append(Paragraph("No candidate data available for this project yet.", styles['BodyText']))
    story.append(Spacer(1, 12))

    # Candidates Table
    story.append(Paragraph("Candidate Rankings & Top Picks", styles['Heading2']))
    data = [["Candidate", "Score", "Skills", "Status"]]
    
    sorted_analyses = sorted(analyses_data, key=lambda x: x.get('match_score', 0), reverse=True)[:10]
    
    if sorted_analyses:
        for a in sorted_analyses:
            data.append([
                a.get('candidate_name', 'Unknown'), 
                f"{a.get('match_score', 0)}%", 
                ", ".join(a.get('matched_skills', [])[:3]) if a.get('matched_skills') else "N/A",
                a.get('status', 'New')
            ])
    else:
        data.append(["N/A", "N/A", "N/A", "N/A"])
    
    t = Table(data, colWidths=[150, 50, 200, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.cadetblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def detect_experience_years(text):
    """Detects years of experience from resume text."""
    text_lower = text.lower()

    patterns = [
        r"(\d+)\+?\s*years?\s*(?:of)?\s*experience",
        r"experience\s*:?\s*(\d+)\+?\s*years?",
        r"(\d+)\+?\s*years?\s*(?:in|of)\s*(?:software|development|programming)",
    ]

    years_found = []
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        years_found.extend([int(m) for m in matches])

    if years_found:
        return max(years_found)
    return 0


def calculate_ats_score(text):
    """Calculates ATS (Applicant Tracking System) friendliness score."""
    score = 50  # Base score

    text_lower = text.lower()

    # Positive factors
    positive_factors = [
        ("email" in text_lower and "@" in text),  # Has email
        bool(re.search(r"\d{10}", text)),  # Phone number
        bool(
            re.search(r"education|degree|b\.?tech|m\.?tech|be|me", text_lower)
        ),  # Education section
        bool(
            re.search(r"experience|work|employment", text_lower)
        ),  # Experience section
        bool(
            re.search(r"skills|technologies|competencies", text_lower)
        ),  # Skills section
        bool(re.search(r"\d+\.\d+/10|\d+%|\bgpa\b", text_lower)),  # Has numbers/grades
        len(re.findall(r"•|\*|-", text)) > 3,  # Has bullet points
        bool(re.search(r"github|linkedin|portfolio", text_lower)),  # Has links
    ]

    score += sum(positive_factors) * 5

    # Negative factors
    negative_factors = [
        len(text) < 200,  # Too short
        len(text) > 15000,  # Too long
        bool(re.search(r"photo|image|picture", text_lower)),  # Contains images
        text.count("\n\n\n") > 2,  # Too many blank lines
    ]

    score -= sum(negative_factors) * 5

    return max(0, min(100, score))


def redact_pii(text):
    """
    Redacts Personal Identifiable Information (PII) from text.
    Masks emails, phone numbers, and common social media/professional links.
    """
    if not text:
        return text
    
    # 1. Redact Emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text = re.sub(email_pattern, "[EMAIL_REDACTED]", text)
    
    # 2. Redact Phone Numbers (Common formats)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    text = re.sub(phone_pattern, "[PHONE_REDACTED]", text)
    
    # 3. Redact Web Links (LinkedIn, Portfolios, etc.)
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    # Special care for common professional links
    text = re.sub(url_pattern, "[LINK_REDACTED]", text)
    
    # 4. Redact potential name patterns (Address/Location placeholders often follow names)
    # This is a bit risky but we can mask common "Location: ..." blocks
    location_pattern = r'(?i)location\s*:\s*.*'
    text = re.sub(location_pattern, "Location: [REDACTED]", text)
    
    return text


def calculate_detailed_match(job_description, resume_text, weighted_skills=None):
    """Calculates detailed breakdown of match score with optional skill weighting."""
    jd_clean = clean_text(job_description)
    resume_clean = clean_text(resume_text)
    jd_lower = job_description.lower()
    resume_lower = resume_text.lower()

    # Extract skills
    jd_skills = extract_semantic_skills(job_description)
    resume_skills = extract_semantic_skills(resume_text)

    # 1. Skill Match (50% of total)
    if jd_skills:
        matched = [s for s in jd_skills if s.lower() in resume_lower]
        
        score_weight = len(matched)
        total_weight = len(jd_skills)

        # Apply 5x weight to priority skills
        if weighted_skills:
            for s in jd_skills:
                # Check if this JD skill is one of the priority ones
                if any(w.lower() in s.lower() for w in weighted_skills):
                    total_weight += 4 # 1 (original) + 4 = 5x
                    if s.lower() in resume_lower:
                        score_weight += 4
        
        skill_score = (score_weight / total_weight) * 50
    else:
        skill_score = 25

    # 2. Experience Match (20% of total)
    jd_exp = detect_experience_years(job_description)
    resume_exp = detect_experience_years(resume_text)

    if jd_exp > 0 and resume_exp > 0:
        if resume_exp >= jd_exp:
            exp_score = 20
        else:
            exp_score = (resume_exp / jd_exp) * 20
    else:
        exp_score = 10

    # 3. Keywords Match (20% of total)
    important_keywords = [
        "python",
        "java",
        "javascript",
        "react",
        "angular",
        "node",
        "sql",
        "postgresql",
        "mongodb",
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "git",
        "agile",
        "scrum",
        "api",
        "rest",
        "microservices",
        "cloud",
    ]

    jd_keywords = sum(1 for kw in important_keywords if kw in jd_lower)
    matched_keywords = sum(
        1 for kw in important_keywords if kw in jd_lower and kw in resume_lower
    )

    if jd_keywords > 0:
        keyword_score = (matched_keywords / jd_keywords) * 20
    else:
        keyword_score = 10

    # 4. ATS Score (10% of total)
    ats_score = calculate_ats_score(resume_text)
    ats_component = (ats_score / 100) * 10

    total = skill_score + exp_score + keyword_score + ats_component

    return {
        "total": round(total, 1),
        "skill_score": round(skill_score, 1),
        "experience_score": round(exp_score, 1),
        "keyword_score": round(keyword_score, 1),
        "ats_score": round(ats_component, 1),
        "matched_skills": matched if jd_skills else [],
        "all_resume_skills": resume_skills,
        "years_experience": resume_exp,
        "email": extract_email(resume_text)
    }

def xml_escape(text):
    """Escapes special characters for ReportLab Paragraphs."""
    if not text: return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def generate_ics_content(candidate_name, role_title, interview_date, medium, interviewer_email):
    """
    Generates iCalendar (.ics) content for an interview.
    """
    from datetime import timedelta
    import uuid
    
    dt_start = interview_date.strftime("%Y%m%dT%H%M%SZ")
    dt_end = (interview_date + timedelta(hours=1)).strftime("%Y%m%dT%H%M%SZ")
    dt_now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = str(uuid.uuid4())

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Smart Resume Matcher//EN",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dt_now}",
        f"DTSTART:{dt_start}",
        f"DTEND:{dt_end}",
        f"SUMMARY:Interview: {candidate_name} for {role_title}",
        f"DESCRIPTION:Interview scheduled via Smart Resume Matcher.\\nMedium: {medium}",
        f"LOCATION:{medium}",
        f"ORGANIZER;CN=Recruitment Team:MAILTO:{interviewer_email}",
        "END:VEVENT",
        "END:VCALENDAR"
    ]
def generate_intelligence_report_pdf(candidate_name, jd_title, match_score, ai_eval):
    """
    Generates a professional PDF report for a candidate's AI evaluation.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#4F46E5"),
        spaceAfter=20,
        alignment=1 # Center
    )
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=15,
        spaceAfter=10
    )
    body_style = styles['BodyText']
    
    elements = []
    
    # 1. Header
    elements.append(Paragraph("Institutional Talent Intelligence Report", header_style))
    elements.append(Spacer(1, 10))
    
    # 2. Metadata Table
    meta_data = [
        ["Candidate:", candidate_name],
        ["Applied Role:", jd_title],
        ["Generated At:", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
        ["System Verdict:", ai_eval.get("recommendation", "N/A")],
        ["Match Score:", f"{match_score}%"]
    ]
    meta_table = Table(meta_data, colWidths=[1.5*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#475569")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))
    
    # 3. Executive Summary
    elements.append(Paragraph("Executive Summary", section_style))
    summary_text = xml_escape(ai_eval.get("summary", "No summary available."))
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 15))
    
    # 4. Strengths and Weaknesses
    col_data = [
        [Paragraph("<b>💎 Key Strengths</b>", body_style), Paragraph("<b>⚠️ Potential Gaps</b>", body_style)]
    ]
    
    strengths = ai_eval.get("strengths", [])
    weaknesses = ai_eval.get("weaknesses", [])
    
    max_rows = max(len(strengths), len(weaknesses))
    for i in range(max_rows):
        s = strengths[i] if i < len(strengths) else ""
        w = weaknesses[i] if i < len(weaknesses) else ""
        col_data.append([Paragraph(f"• {s}", body_style) if s else "", Paragraph(f"• {w}", body_style) if w else ""])
        
    sw_table = Table(col_data, colWidths=[2.75*inch, 2.75*inch])
    sw_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(sw_table)
    elements.append(Spacer(1, 20))
    
    # 5. Footer / Disclaimer
    elements.append(Spacer(1, 30))
    disclaimer = Paragraph(
        "<font color='grey' size='8'>This report is generated by Smart Resume Matcher AI. "
        "Intended for professional institutional use only.</font>",
        styles['Italic']
    )
    elements.append(disclaimer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
