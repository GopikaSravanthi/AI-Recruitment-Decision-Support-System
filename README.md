# An Intelligent AI-Based Recruitment Decision Support System Using NLP and Machine Learning

🔗 **Live Demo:** [https://ai-recruitment-decision-support-system-4dj8wopffz9vzzylzarykn.streamlit.app/]

An end-to-end recruitment automation platform that screens, scores, and ranks candidates against a job description using NLP-based semantic matching and skill extraction — turning a manual, time-consuming shortlisting process into an automated, data-driven decision system.

## Overview

Recruiters often face hundreds of resumes per role and limited time to manually screen each one for relevance. This system automates that process: recruiters upload a ZIP of candidate resumes and a job description, and the system extracts candidate details, computes a hybrid relevance score, classifies eligibility, and generates professional, ready-to-share reports — all through an interactive dashboard.

## Key Features

- 📂 **Bulk resume processing** — upload a ZIP of PDF resumes for batch analysis
- 🧠 **Semantic matching** — uses Sentence-BERT (`all-MiniLM-L6-v2`) embeddings and cosine similarity to measure how well a resume's content aligns with the job description's meaning, not just keyword overlap
- 🎯 **Skill extraction & matching** — parses resumes against a 60+ term canonical skill taxonomy (programming languages, ML/AI, cloud, DevOps, databases, and more), with normalization for variants (e.g. "ML" → "machine learning", "JS" → "javascript")
- ⚖️ **Hybrid scoring model** — combines semantic similarity (60%) and skill match (40%) into a single Final Score
- 🎓 **CGPA-based eligibility filtering** alongside score-based eligibility
- 📊 **Interactive dashboard** — filterable, searchable candidate rankings with score and eligibility visualizations (built with Streamlit)
- 📄 **Automated report generation** — individual candidate PDF reports (with skill match tables and score breakdowns), summary PDFs, Excel exports, and bulk ZIP downloads — all generated with ReportLab

## How It Works

1. **Resume Upload** — Recruiter uploads a ZIP of candidate resumes (PDF) and enters a job description
2. **Data Extraction** — Each resume is parsed to extract candidate name, email, phone number, CGPA, and structured content (skills, projects, experience sections)
3. **Semantic Scoring** — Resume content and the job description are embedded using Sentence-BERT, and cosine similarity produces a Semantic Score
4. **Skill Scoring** — Skills are extracted from both the resume and job description against a canonical taxonomy, and matched/missing skills are identified
5. **Hybrid Final Score** — Semantic Score (60%) + Skill Score (40%) combine into a Final Score
6. **Eligibility Classification** — Candidates are filtered by both a configurable score threshold and minimum CGPA requirement
7. **Ranking & Dashboard** — Candidates are ranked and displayed in an interactive dashboard with filtering, search, and visualizations
8. **Report Generation** — Recruiters can download individual candidate PDF reports, a recruiter summary PDF, Excel breakdowns, or a ZIP of all reports

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Web Framework | Streamlit |
| NLP / Embeddings | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| Similarity Scoring | Scikit-learn (cosine similarity) |
| Resume Parsing | PyPDF2, Regex |
| Data Handling | Pandas, NumPy |
| Report Generation | ReportLab (PDF), OpenPyXL (Excel) |
| Deployment | Streamlit Community Cloud |

## Configurable Recruitment Settings

- Eligibility score threshold (adjustable 0-100%)
- Minimum CGPA requirement (adjustable 0-10)
- Top N shortlist size
- Live candidate search and score filtering

## Setup (Local)

```bash
git clone https://github.com/GopikaSravanthi/AI-Recruitment-Decision-Support-System.git
cd AI-Recruitment-Decision-Support-System
pip install -r requirements.txt
streamlit run app.py
```

## Status

Deployed and functional. Open to feedback and improvements.
