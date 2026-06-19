import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------
# Load Transformer Model
# --------------------------------

_model = None

def get_model():

    global _model

    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')

    return _model


# --------------------------------
# Canonical Skill Dictionary
# --------------------------------

CANONICAL_SKILLS = [

# Programming
"python","java","c","c++","c#","javascript","typescript","go","rust","scala","r",

# Web
"html","css","bootstrap","react","angular","vue","nextjs",

# Backend
"flask","django","fastapi","node","express","spring boot",

# APIs
"api","graphql","microservices",

# Databases
"sql","mysql","postgresql","mongodb","redis","sqlite",

# Data Science
"pandas","numpy","scipy","matplotlib","seaborn",

# Machine Learning
"machine learning","deep learning","reinforcement learning",

# NLP
"natural language processing","spacy","nltk","gensim",

# Computer Vision
"computer vision","opencv","object detection","image segmentation",

# ML Frameworks
"tensorflow","pytorch","keras","scikit","xgboost","lightgbm",

# Big Data
"spark","pyspark","hadoop","kafka",

# Visualization
"power bi","tableau","excel",

# DevOps
"git","docker","kubernetes","jenkins","terraform",

# Cloud
"aws","azure","gcp",

# Generative AI
"generative ai","large language models",

# LLM Frameworks
"langchain","llamaindex","crewai","autogen","langgraph",

# Agentic AI
"ai agents","agentic ai","multi-agent systems",

# Vector Databases
"vector database","faiss","pinecone","weaviate","chroma",

# RAG
"rag","retrieval augmented generation",

# Prompt Engineering
"prompt engineering",

# AI Platforms
"openai","huggingface","vertex ai"

]


# --------------------------------
# Skill Normalization
# --------------------------------

SKILL_VARIATIONS = {

"api": ["api","apis","rest api","restful api"],

"machine learning": ["machine learning","ml","machine-learning"],

"deep learning": ["deep learning","dl"],

"natural language processing": [
    "nlp",
    "natural language processing"
],

"data structure": [
    "data structure",
    "data structures"
],

"algorithm": [
    "algorithm",
    "algorithms"
],

"scikit": [
    "scikit",
    "sklearn",
    "scikit-learn"
],

"javascript": ["javascript","js"],

"node": ["node","nodejs","node.js"],

"tensorflow": ["tensorflow","tf"],

"pytorch": ["pytorch","torch"],

"power bi": ["powerbi","power bi"],

"spark": ["spark","apache spark"],

"generative ai": ["generative ai","gen ai"],

"large language models": ["llm","large language models"],

"vector database": ["vector db","vector database"],

"rag": ["rag","retrieval augmented generation"]

}


# --------------------------------
# Normalize Skill
# --------------------------------

def normalize_skill(skill):

    skill = skill.lower().strip()

    for canonical, variants in SKILL_VARIATIONS.items():

        if skill in variants:
            return canonical

    return skill


# --------------------------------
# Remove duplicates
# --------------------------------

def unique_list(seq):

    seen = set()
    result = []

    for item in seq:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


# --------------------------------
# Skill Extraction
# --------------------------------

def extract_clean_skills(text):

    text = text.lower()

    found = []

    # Canonical skills
    for skill in CANONICAL_SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            found.append(normalize_skill(skill))

    # Skill variations
    for canonical, variants in SKILL_VARIATIONS.items():

        for variant in variants:

            pattern = r"\b" + re.escape(variant) + r"\b"

            if re.search(pattern, text):
                found.append(normalize_skill(canonical))
                break

    return unique_list(found)


# --------------------------------
# Semantic Similarity Score
# --------------------------------

def compute_semantic_scores(df, job_description):

    model = get_model()

    resume_embeddings = model.encode(df["Structured_Text"].tolist())
    jd_embedding = model.encode([job_description])

    similarity = cosine_similarity(resume_embeddings, jd_embedding)

    df["Semantic_Score (%)"] = (similarity.flatten() * 100).round(2)

    return df


# --------------------------------
# Skill Matching Score
# --------------------------------

def compute_skill_scores(df, job_description):

    jd_text = job_description.lower()

    jd_skills = extract_clean_skills(jd_text)

    skill_scores = []
    matched_list = []
    missing_list = []

    for resume in df["Structured_Text"]:

        resume_text = resume.lower()

        resume_skills = extract_clean_skills(resume_text)

        matched = list(set(jd_skills) & set(resume_skills))
        missing = list(set(jd_skills) - set(resume_skills))

        matched = unique_list(sorted(matched))
        missing = unique_list(sorted(missing))

        if len(jd_skills) == 0:
            score = 0
        else:
            score = (len(matched) / len(jd_skills)) * 100

        skill_scores.append(round(score, 2))
        matched_list.append(", ".join(matched))
        missing_list.append(", ".join(missing))

    df["Skill_Score (%)"] = skill_scores
    df["Matched_Skills"] = matched_list
    df["Missing_Skills"] = missing_list

    return df


# --------------------------------
# Final Hybrid Score
# --------------------------------

def compute_final_scores(df):

    final_scores = []

    for _, row in df.iterrows():

        score = (
            row["Semantic_Score (%)"] * 0.60 +
            row["Skill_Score (%)"] * 0.40
        )

        final_scores.append(round(score, 2))

    df["Final_Score (%)"] = final_scores

    return df


# --------------------------------
# Eligibility Classification
# --------------------------------

def classify_eligibility(df, threshold):

    df["Eligibility"] = df["Final_Score (%)"].apply(
        lambda x: "Eligible" if x >= threshold else "Not Eligible"
    )

    return df


# --------------------------------
# Ranking
# --------------------------------

def rank_candidates(df):

    df = df.sort_values(by="Final_Score (%)", ascending=False).reset_index(drop=True)

    df["Rank"] = df.index + 1

    return df