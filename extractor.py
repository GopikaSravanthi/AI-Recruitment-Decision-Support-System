import re
import os
import zipfile
from PyPDF2 import PdfReader


# --------------------------------
# Name Extraction Logic
# --------------------------------

BAD_WORDS = [
    "objective","summary","resume","profile","github","linkedin",
    "email","gmail","mobile","contact","india","software",
    "developer","engineer","phone","computer","science"
]


def clean_name(line):
    line = re.sub(r'\S+@\S+', '', line)
    line = re.sub(r'\+?\d[\d\s\-]{8,}', '', line)
    line = re.sub(r'[^A-Za-z\s]', '', line)

    for word in BAD_WORDS:
        line = re.sub(r'\b'+word+r'\b', '', line, flags=re.IGNORECASE)

    return re.sub(r'\s+', ' ', line).strip()


def extract_candidate_name(text):

    lines = text.split("\n")[:10]

    for line in lines:

        cleaned = clean_name(line.strip())
        words = cleaned.split()

        if 2 <= len(words) <= 5:
            return " ".join(words).title()

    return "Name Not Found"


# --------------------------------
# CGPA Extraction (NEW FEATURE)
# --------------------------------

def extract_cgpa(text):

    text = text.lower()

    patterns = [
        r'cgpa\s*[:\-]?\s*(\d\.\d)',
        r'gpa\s*[:\-]?\s*(\d\.\d)',
        r'(\d\.\d)\s*/\s*10'
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            try:
                return float(match.group(1))
            except:
                continue

    return 0


# --------------------------------
# Structured Resume Extraction
# --------------------------------

def extract_structured_content(text):

    text = text.lower()
    lines = text.split("\n")

    structured_text = ""
    capture = False

    keywords = [
        "skill", "technical skill",
        "project", "experience",
        "internship", "certification",
        "achievement", "award"
    ]

    for line in lines:

        if any(keyword in line for keyword in keywords):
            capture = True
            continue

        if capture and line.strip() == "":
            capture = False

        if capture:
            structured_text += " " + line

    return structured_text.strip()


# --------------------------------
# ZIP Resume Reader
# --------------------------------

def read_resumes_from_zip(zip_path, extract_path="temp"):

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    data = []

    for root, dirs, files in os.walk(extract_path):

        for file in files:

            if file.lower().endswith(".pdf"):

                file_path = os.path.join(root, file)

                try:
                    reader = PdfReader(file_path)

                    text = ""

                    for page in reader.pages:

                        page_text = page.extract_text()

                        if page_text:
                            text += page_text

                    if text.strip():

                        name = extract_candidate_name(text)

                        structured = extract_structured_content(text)

                        cgpa = extract_cgpa(text)

                        data.append((name, structured, cgpa))

                except:
                    continue

    return data