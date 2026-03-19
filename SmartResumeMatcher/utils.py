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

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

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
    # Additional extraction using NLP
    tokens = word_tokenize(clean_text(text))

    try:
        stop_words = set(stopwords.words("english"))
    except AttributeError:
        # Fallback for NLTK LazyCorpusLoader error
        stop_words = {
            "i",
            "me",
            "my",
            "myself",
            "we",
            "our",
            "ours",
            "ourselves",
            "you",
            "you're",
            "you've",
            "you'll",
            "you'd",
            "your",
            "yours",
            "yourself",
            "yourselves",
            "he",
            "him",
            "his",
            "himself",
            "she",
            "she's",
            "her",
            "hers",
            "herself",
            "it",
            "it's",
            "its",
            "itself",
            "they",
            "them",
            "their",
            "theirs",
            "themselves",
            "what",
            "which",
            "who",
            "whom",
            "this",
            "that",
            "that'll",
            "these",
            "those",
            "am",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "having",
            "do",
            "does",
            "did",
            "doing",
            "a",
            "an",
            "the",
            "and",
            "but",
            "if",
            "or",
            "because",
            "as",
            "until",
            "while",
            "of",
            "at",
            "by",
            "for",
            "with",
            "about",
            "against",
            "between",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "to",
            "from",
            "up",
            "down",
            "in",
            "out",
            "on",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "any",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "s",
            "t",
            "can",
            "will",
            "just",
            "don",
            "don't",
            "should",
            "should've",
            "now",
            "d",
            "ll",
            "m",
            "o",
            "re",
            "ve",
            "y",
            "ain",
            "aren",
            "aren't",
            "couldn",
            "couldn't",
            "didn",
            "didn't",
            "doesn",
            "doesn't",
            "hadn",
            "hadn't",
            "hasn",
            "hasn't",
            "haven",
            "haven't",
            "isn",
            "isn't",
            "ma",
            "mightn",
            "mightn't",
            "mustn",
            "mustn't",
            "needn",
            "needn't",
            "shan",
            "shan't",
            "shouldn",
            "shouldn't",
            "wasn",
            "wasn't",
            "weren",
            "weren't",
            "won",
            "won't",
            "wouldn",
            "wouldn't",
        }
    except Exception:
        stop_words = set()

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


def evaluate_resume_with_groq(client, job_description, resume_text):
    """
    Evaluates a resume against a job description using the GROQ API.

    Args:
        client (Groq): Initialized Groq client
        job_description (str): Job Description text
        resume_text (str): Resume text

    Returns:
        dict: Parsed JSON response from the LLM
    """
    system_prompt = """You are an expert AI HR recruiter with 15+ years of experience in technical hiring.
Your job is to evaluate candidate resumes against a given Job Description (JD).
Be analytical, fair, and structured in your evaluation.
Return output strictly in JSON format with the following structure:
{
    "match_score": <number 0-100>,
    "hiring_status": "<'Ready to Hire' | 'Not Ready'>",
    "ats_friendly_score": <number 0-100>,
    "is_ats_friendly": <boolean>,
    "summary": "<brief executive summary>",
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "weaknesses": ["<weakness 1>", "<weakness 2>", ...],
    "missing_critical_skills": ["<skill 1>", "<skill 2>", ...],
    "recommendation": "<'Strongly Hire' | 'Hire' | 'Weak Hire' | 'Reject'>"
}
"""

    user_prompt = f"""
    Job Description:
    {job_description}
    
    Candidate Resume:
    {resume_text}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1000,
            top_p=1,
            stream=False,
            stop=None,
        )

        response_content = completion.choices[0].message.content
        # Try to parse JSON strictly
        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            # If standard parsing fails, try to find JSON block
            import re

            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return {
                    "error": "Failed to parse JSON response",
                    "raw_content": response_content,
                }

    except Exception as e:
        return {"error": str(e)}


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


def calculate_detailed_match(job_description, resume_text):
    """Calculates detailed breakdown of match score."""
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
        skill_score = (len(matched) / len(jd_skills)) * 50
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
    }
