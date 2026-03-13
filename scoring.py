import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------
# Load Transformer Model (Singleton)
# --------------------------------

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


# --------------------------------
# Technical Skill Dictionary
# --------------------------------

IMPORTANT_KEYWORDS = [
    "python","java","c++","sql","mysql","postgresql",
    "aws","azure","gcp",
    "rest","api","apis",
    "git","docker","kubernetes",
    "pandas","numpy","machine learning","ml",
    "data structures","algorithms",
    "react","node","flask","django",
    "tensorflow","pytorch","scikit",
    "power bi","tableau"
]


# --------------------------------
# Skill Extraction
# --------------------------------

def extract_clean_skills(text):
    text = text.lower()
    found = []

    for skill in IMPORTANT_KEYWORDS:
        if skill in text:
            found.append(skill)

    return list(set(found))


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
# Skill Matching Score (NO HARD FAIL)
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

        # Skill Score %
        if len(jd_skills) == 0:
            score = 0
        else:
            score = (len(matched) / len(jd_skills)) * 100

        skill_scores.append(round(score, 2))
        matched_list.append(", ".join(sorted(matched)))
        missing_list.append(", ".join(sorted(missing)))

    df["Skill_Score (%)"] = skill_scores
    df["Matched_Skills"] = matched_list
    df["Missing_Skills"] = missing_list

    return df


# --------------------------------
# Final Hybrid Score (Always Shows Real %)
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