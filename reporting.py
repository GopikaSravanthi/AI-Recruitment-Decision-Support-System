from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import pandas as pd
import zipfile


# ---------------------------------------------------
# Candidate PDF Report
# ---------------------------------------------------

def generate_candidate_pdf(row):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(8.5 * inch, 11 * inch),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    elements = []

    # ---------------- Styles ----------------

    title = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        alignment=1,
        fontSize=20,
        textColor=colors.HexColor("#1F4E79")
    )

    subtitle = ParagraphStyle(
        "subtitle",
        parent=styles["Heading2"],
        alignment=1,
        fontSize=13,
        textColor=colors.HexColor("#3A5F8A")
    )

    section = ParagraphStyle(
        "section",
        parent=styles["Normal"],
        textColor=colors.white,
        backColor=colors.HexColor("#4F81BD"),
        fontSize=11,
        leftIndent=6,
        spaceBefore=8,
        spaceAfter=6
    )

    normal = ParagraphStyle(
        "normal",
        parent=styles["Normal"],
        fontSize=9
    )

    # ---------------- Header ----------------

    elements.append(Paragraph("ENTERPRISE AI RECRUITMENT DECISION SYSTEM", subtitle))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("Candidate Evaluation Report", title))
    elements.append(Spacer(1, 10))

    # ---------------- Candidate Details ----------------

    elements.append(Paragraph("Candidate Details", section))

    details = [
        ["Name", row.get("Candidate_Name", "N/A")],
        ["Email", row.get("Email", "N/A")],
        ["Phone", row.get("Phone", "N/A")]
    ]

    details_table = Table(details, colWidths=[120, 360])
    details_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF3F8")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9)
    ]))

    elements.append(details_table)
    elements.append(Spacer(1, 8))

    # ---------------- Academic + Summary ----------------

    cgpa = row.get("CGPA", "N/A")
    score = float(row.get("Final_Score (%)", 0))
    eligibility = row.get("Eligibility", "Not Eligible")

    color = colors.green if eligibility == "Eligible" else colors.red

    academic = [
        ["CGPA", str(cgpa)],
        ["Score", f"{score}%"],
        ["Status", eligibility]
    ]

    academic_table = Table(academic, colWidths=[120, 120])
    academic_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF3F8")),
        ("TEXTCOLOR", (1, 2), (1, 2), color),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey)
    ]))

    summary = [
        ["Recruitment Summary"],
        [f"Score : {score}%"],
        ["CGPA : Qualified"],
        [f"Status : {eligibility}"]
    ]

    summary_table = Table(summary, colWidths=[240])
    summary_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
        ("FONTSIZE", (0, 0), (-1, -1), 9)
    ]))

    two_column = Table([[academic_table, summary_table]], colWidths=[250, 250])
    two_column.setStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ])

    elements.append(two_column)
    elements.append(Spacer(1, 8))

    # ---------------- Progress Bar ----------------

    elements.append(Paragraph("Skill Match Percentage", section))
    elements.append(Paragraph(f"<b>{round(score)}%</b>", normal))

    bar_width = 350
    filled = (score / 100) * bar_width

    progress = Table(
        [["", ""]],
        colWidths=[filled, bar_width - filled],
        rowHeights=8
    )

    progress.setStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#2ecc71")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#D3D3D3"))
    ])

    elements.append(progress)
    elements.append(Spacer(1, 8))

    # ---------------- Skill Analysis ----------------

    elements.append(Paragraph("Skill Analysis", section))

    matched = row.get("Matched_Skills", "")
    missing = row.get("Missing_Skills", "")

    elements.append(Paragraph(f"<b>Matched:</b> {matched}", normal))
    elements.append(Paragraph(f"<b>Missing:</b> {missing}", normal))
    elements.append(Spacer(1, 6))

    # ---------------- Skill Table ----------------

    matched_list = matched.split(", ") if matched else []
    missing_list = missing.split(", ") if missing else []

    skills = matched_list + missing_list

    if skills:

        weight = round(100 / len(skills), 2)

        data = [["Skill", "Score", "Status"]]

        for skill in skills:
            if skill in matched_list:
                data.append([skill, f"{weight}%", "✔"])
            else:
                data.append([skill, "0%", "✖"])

        skill_table = Table(data, colWidths=[220, 100, 80])

        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ])

        # striped rows
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F9FB"))

        skill_table.setStyle(style)

        elements.append(skill_table)

    doc.build(elements)
    return buffer.getvalue()


# ---------------------------------------------------
# Summary PDF
# ---------------------------------------------------

def generate_summary_pdf(df):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Recruitment Summary Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Total: {len(df)}", styles["Normal"]))
    elements.append(Paragraph(f"Eligible: {len(df[df['Eligibility']=='Eligible'])}", styles["Normal"]))
    elements.append(Paragraph(f"Not Eligible: {len(df[df['Eligibility']=='Not Eligible'])}", styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()


# ---------------------------------------------------
# Excel Export
# ---------------------------------------------------

def generate_excel(df):

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df[df["Eligibility"]=="Eligible"].to_excel(writer, sheet_name="Eligible", index=False)
        df[df["Eligibility"]=="Not Eligible"].to_excel(writer, sheet_name="Not_Eligible", index=False)

    return buffer.getvalue()


# ---------------------------------------------------
# ZIP Export
# ---------------------------------------------------

def generate_all_reports_zip(df):

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer,"w") as zf:
        for _, row in df.iterrows():
            pdf_bytes = generate_candidate_pdf(row)
            filename = f"{row['Candidate_Name'].replace(' ','_')}_Report.pdf"
            zf.writestr(filename, pdf_bytes)

    return zip_buffer.getvalue()
