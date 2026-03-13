import streamlit as st
from reporting import (
    generate_candidate_pdf,
    generate_summary_pdf,
    generate_excel,
    generate_all_reports_zip
)

# --------------------------------
# Dashboard Display Function
# --------------------------------
def render_dashboard(df, top_n):

    st.subheader("🔍 Filters")

    search = st.text_input("Search Candidate")

    if search:
        df = df[df["Candidate_Name"].str.contains(search, case=False)]

    min_score = st.slider("Minimum Score Filter", 0, 100, 0)
    df = df[df["Final_Score (%)"] >= min_score]

    # --------------------------------
    # Tabs
    # --------------------------------
    tab1, tab2, tab3 = st.tabs(
        ["📊 Overview", "📋 Rankings", "📄 Reports"]
    )

    # --------------------------------
    # TAB 1 — Overview
    # --------------------------------
    with tab1:

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Candidates", len(df))
        col2.metric(
            "Eligible",
            len(df[df["Eligibility"] == "Eligible"])
        )
        col3.metric(
            "Not Eligible",
            len(df[df["Eligibility"] == "Not Eligible"])
        )

        st.markdown("### 📊 Score Distribution")

        if len(df) > 0:
            st.bar_chart(
                df.set_index("Candidate_Name")["Final_Score (%)"]
            )

        st.markdown("### 📈 Eligibility Distribution")

        if len(df) > 0:
            st.bar_chart(
                df["Eligibility"].value_counts()
            )

    # --------------------------------
    # TAB 2 — Rankings
    # --------------------------------
    with tab2:

        st.markdown(f"### 🏆 Top {top_n} Candidates")

        st.dataframe(
            df.head(top_n),
            use_container_width=True
        )

    # --------------------------------
    # TAB 3 — Reports
    # --------------------------------
    with tab3:

        st.markdown("### 📥 Download Lists")

        eligible = df[df["Eligibility"] == "Eligible"]
        not_eligible = df[df["Eligibility"] == "Not Eligible"]

        st.download_button(
            "Download Eligible List (CSV)",
            eligible.to_csv(index=False),
            file_name="Eligible_Candidates.csv",
            key="eligible_csv"
        )

        st.download_button(
            "Download Not Eligible List (CSV)",
            not_eligible.to_csv(index=False),
            file_name="Not_Eligible_Candidates.csv",
            key="not_eligible_csv"
        )

        st.download_button(
            "Download Excel Report",
            generate_excel(df),
            file_name="Recruitment_Report.xlsx",
            key="excel_report"
        )

        st.download_button(
            "Download All Candidate Reports (ZIP)",
            generate_all_reports_zip(df),
            file_name="All_Candidate_Reports.zip",
            key="zip_reports"
        )

        st.download_button(
            "Download Recruiter Summary PDF",
            generate_summary_pdf(df),
            file_name="Recruitment_Summary.pdf",
            mime="application/pdf",
            key="summary_pdf"
        )

        st.markdown("### 📄 Individual Candidate Reports")

        for idx, row in df.iterrows():

            pdf_bytes = generate_candidate_pdf(row)

            st.download_button(
                label=f"Download Report - {row['Candidate_Name']}",
                data=pdf_bytes,
                file_name=f"{row['Candidate_Name'].replace(' ','_')}_Report.pdf",
                mime="application/pdf",
                key=f"download_{idx}"
            )