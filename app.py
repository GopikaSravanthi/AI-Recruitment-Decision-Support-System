import streamlit as st
import os
import pandas as pd

from extractor import read_resumes_from_zip
from scoring import (
    compute_semantic_scores,
    compute_skill_scores,
    compute_final_scores,
    classify_eligibility,
    rank_candidates
)

from ui_dashboard import render_dashboard


# --------------------------------
# Session State Initialization
# --------------------------------
if "df" not in st.session_state:
    st.session_state.df = None


# --------------------------------
# Page Config
# --------------------------------
st.set_page_config(
    page_title="Enterprise AI Recruitment System",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
.big-title {font-size:34px; font-weight:700; color:#1F4E79;}
.sub-text {color:gray; font-size:15px;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="big-title">🧠 Enterprise AI Recruitment Decision System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-text">Automated Resume Screening | AI Matching | Smart Ranking</div>',
    unsafe_allow_html=True
)

st.divider()


# --------------------------------
# Sidebar Controls
# --------------------------------
with st.sidebar:

    st.header("⚙️ Recruitment Settings")

    uploaded_zip = st.file_uploader(
        "Upload Resume ZIP",
        type=["zip"]
    )

    job_description = st.text_area(
        "Enter Job Description"
    )

    threshold = st.slider(
        "Eligibility Threshold (%)",
        0, 100, 40
    )

    # ⭐ NEW FEATURE — CGPA Requirement
    min_cgpa = st.slider(
        "Minimum CGPA Requirement",
        0.0, 10.0, 6.5
    )

    top_n = st.number_input(
        "Top N Shortlist",
        min_value=1,
        max_value=100,
        value=5
    )

    analyze = st.button("🚀 Run AI Analysis")


# --------------------------------
# Run Analysis
# --------------------------------
if analyze:

    if uploaded_zip is None or job_description.strip() == "":
        st.warning("Please upload resumes and enter job description.")
        st.stop()

    # Create temp folder
    if not os.path.exists("temp"):
        os.makedirs("temp")

    zip_path = os.path.join("temp", uploaded_zip.name)

    # Save uploaded ZIP
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.read())

    # --------------------------------
    # Extract Resume Data
    # --------------------------------
    data = read_resumes_from_zip(zip_path)

    if len(data) == 0:
        st.error("No valid resumes found inside ZIP.")
        st.stop()

    # ⭐ Now includes CGPA
    df = pd.DataFrame(
        data,
        columns=["Candidate_Name", "Structured_Text", "CGPA"]
    )

    # --------------------------------
    # CGPA Eligibility
    # --------------------------------
    df["CGPA_Eligibility"] = df["CGPA"].apply(
        lambda x: "Eligible" if x >= min_cgpa else "Not Eligible"
    )

    # --------------------------------
    # Scoring Pipeline
    # --------------------------------
    df = compute_semantic_scores(df, job_description)

    df = compute_skill_scores(df, job_description)

    df = compute_final_scores(df)

    df = classify_eligibility(df, threshold)

    # --------------------------------
    # Combine CGPA + Score Eligibility
    # --------------------------------
    df["Eligibility"] = df.apply(
        lambda row:
        "Eligible"
        if row["CGPA_Eligibility"] == "Eligible"
        and row["Eligibility"] == "Eligible"
        else "Not Eligible",
        axis=1
    )

    df = rank_candidates(df)

    # Store results
    st.session_state.df = df


# --------------------------------
# Always Render Dashboard If Data Exists
# --------------------------------
if st.session_state.df is not None:

    render_dashboard(
        st.session_state.df,
        top_n
    )