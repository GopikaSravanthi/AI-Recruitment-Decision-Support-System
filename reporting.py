import os
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
import zipfile


# --------------------------------
# Individual Candidate PDF
# --------------------------------

def generate_candidate_pdf(row):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    elements = []

    styles = getSampleStyleSheet()

    elements.append(
        Paragraph(
            "<b>Candidate Evaluation Report</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 0.3 * inch))

    elements.append(
        Paragraph(
            f"<b>Name:</b> {row['Candidate_Name']}",
            styles["Normal"]
        )
    )

    if "CGPA" in row:
        elements.append(
            Paragraph(
                f"<b>CGPA:</b> {row['CGPA']}",
                styles["Normal"]
            )
        )

    elements.append(
        Paragraph(
            f"<b>Final Score:</b> {row['Final_Score (%)']}%",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Eligibility:</b> {row['Eligibility']}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 0.3 * inch))

    elements.append(
        Paragraph(
            f"<b>Matched Skills:</b> {row['Matched_Skills']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Missing Skills:</b> {row['Missing_Skills']}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 0.4 * inch))

    # --------------------------------
    # Skill Weightage Table (NEW)
    # --------------------------------

    matched = row["Matched_Skills"].split(", ") if row["Matched_Skills"] else []
    missing = row["Missing_Skills"].split(", ") if row["Missing_Skills"] else []

    all_skills = matched + missing

    if len(all_skills) > 0:

        weight = round(100 / len(all_skills), 2)

        table_data = [["Skill", "Weightage", "Candidate Score"]]

        for skill in all_skills:

            score = weight if skill in matched else 0

            table_data.append([
                skill,
                f"{weight}%",
                f"{score}%"
            ])

        table = Table(table_data)

        table.setStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.grey),
            ('GRID',(0,0),(-1,-1),0.5,colors.black)
        ])

        elements.append(
            Paragraph(
                "<b>Skill Weightage Report</b>",
                styles["Heading3"]
            )
        )

        elements.append(Spacer(1,0.2*inch))

        elements.append(table)

    doc.build(elements)

    return buffer.getvalue()


# --------------------------------
# Recruiter Summary PDF
# --------------------------------

def generate_summary_pdf(df):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    elements = []

    styles = getSampleStyleSheet()

    elements.append(
        Paragraph(
            "<b>Recruitment Summary Report</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1,0.3*inch))

    elements.append(
        Paragraph(
            f"Total Candidates: {len(df)}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Eligible: {len(df[df['Eligibility']=='Eligible'])}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Not Eligible: {len(df[df['Eligibility']=='Not Eligible'])}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1,0.3*inch))

    table_data = [["Rank","Name","Final Score","Eligibility"]]

    for _, row in df.iterrows():

        table_data.append([
            row["Rank"],
            row["Candidate_Name"],
            f"{row['Final_Score (%)']}%",
            row["Eligibility"]
        ])

    table = Table(table_data)

    table.setStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('GRID',(0,0),(-1,-1),0.5,colors.black)
    ])

    elements.append(table)

    doc.build(elements)

    return buffer.getvalue()


# --------------------------------
# Excel Report
# --------------------------------

def generate_excel(df):

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

        df[df["Eligibility"]=="Eligible"].to_excel(
            writer,
            sheet_name="Eligible",
            index=False
        )

        df[df["Eligibility"]=="Not Eligible"].to_excel(
            writer,
            sheet_name="Not_Eligible",
            index=False
        )

    return buffer.getvalue()


# --------------------------------
# Zip All Individual PDFs
# --------------------------------

def generate_all_reports_zip(df):

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:

        for _, row in df.iterrows():

            pdf_bytes = generate_candidate_pdf(row)

            filename = f"{row['Candidate_Name'].replace(' ','_')}_Report.pdf"

            zf.writestr(filename, pdf_bytes)

    return zip_buffer.getvalue()