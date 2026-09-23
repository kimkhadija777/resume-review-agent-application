import os
import streamlit as st
from pypdf import PdfReader
from docx import Document

from crewai import Agent, Task, Crew, Process, LLM


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Resume Review Agent",
    page_icon="📄",
    layout="wide"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📄 Resume Review Agent")
st.write(
    "Upload your resume, enter a job description, "
    "and get an AI-powered review of your skills and gaps."
)


# --------------------------------------------------
# GET GROQ API KEY
# --------------------------------------------------

groq_api_key = st.secrets.get("GROQ_API_KEY")

if not groq_api_key:
    st.error(
        "GROQ_API_KEY is not configured. "
        "Please add it in Streamlit Secrets."
    )
    st.stop()

os.environ["GROQ_API_KEY"] = groq_api_key


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("⚙️ Settings")

model_name = st.sidebar.selectbox(
    "Choose Groq Model",
    [
        "groq/openai/gpt-oss-20b",
        "groq/openai/gpt-oss-120b"
    ]
)

st.sidebar.info(
    "The application uses one CrewAI agent "
    "to parse, compare, and review the resume."
)


# --------------------------------------------------
# RESUME TEXT EXTRACTION
# --------------------------------------------------

def extract_text_from_pdf(uploaded_file):
    """Extract text from a PDF resume."""

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_text_from_docx(uploaded_file):
    """Extract text from a DOCX resume."""

    document = Document(uploaded_file)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_resume_text(uploaded_file):
    """Extract resume text based on file type."""

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)

    elif file_name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)

    else:
        return ""


# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------

st.header("1️⃣ Upload Resume")

uploaded_resume = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)


st.header("2️⃣ Job Description")

job_description = st.text_area(
    "Paste the job description here",
    height=250,
    placeholder="Paste the complete job description here..."
)


# --------------------------------------------------
# REVIEW BUTTON
# --------------------------------------------------

review_button = st.button(
    "🔍 Review Resume",
    type="primary"
)


# --------------------------------------------------
# RUN RESUME REVIEW
# --------------------------------------------------

if review_button:

    if uploaded_resume is None:
        st.warning("Please upload a resume first.")
        st.stop()

    if not job_description.strip():
        st.warning("Please enter a job description.")
        st.stop()


    # ----------------------------------------------
    # EXTRACT RESUME
    # ----------------------------------------------

    with st.spinner("Reading your resume..."):

        resume_text = extract_resume_text(uploaded_resume)


    if not resume_text.strip():

        st.error(
            "I could not extract readable text from the resume. "
            "Please try another PDF or DOCX file."
        )

        st.stop()


    # ----------------------------------------------
    # CREATE CREWAI LLM
    # ----------------------------------------------

    try:

        llm = LLM(
            model=model_name,
            temperature=0.2
        )


        # ------------------------------------------
        # CREATE ONE AGENT
        # ------------------------------------------

        resume_agent = Agent(
            role="Resume Review Specialist",

            goal=(
                "Review a candidate's resume against a job description, "
                "identify job-related skill and experience gaps, "
                "and provide practical resume improvement recommendations."
            ),

            backstory=(
                "You are a careful resume review specialist. "
                "You compare resumes with job descriptions using only "
                "the information provided. You never invent experience "
                "or skills."
            ),

            llm=llm,

            verbose=False
        )


        # ------------------------------------------
        # CREATE ONE TASK
        # ------------------------------------------

        review_task = Task(

            description=f"""
You are reviewing a resume against a job description.

========================
CANDIDATE RESUME
========================

{resume_text}


========================
JOB DESCRIPTION
========================

{job_description}


Complete the review in THREE stages.

========================
STAGE 1 — INPUT PARSING
========================

Extract:

1. Important skills mentioned in the job description.
2. Important technical requirements.
3. Important soft skills.
4. Required or preferred experience.
5. Education or certification requirements.

Also identify the candidate's:

1. Technical skills.
2. Soft skills.
3. Experience.
4. Education.
5. Certifications.
6. Projects.

Only use information that is actually present.

If something is not mentioned, write:

"Not stated"


========================
STAGE 2 — GAP ANALYSIS
========================

Compare the job requirements with the resume.

Identify:

1. Skills clearly present in the resume.
2. Skills required by the job but not clearly shown in the resume.
3. Experience requirements that are not clearly demonstrated.
4. Important job requirements that need stronger evidence.

Do not assume that the candidate has a skill simply because it is related
to another skill.

For example:

If the job requires Python and the resume only says HTML,
do not say that the candidate knows Python.

Use:

"Not evidenced in the resume."


========================
STAGE 3 — RECOMMENDATIONS
========================

Provide practical recommendations.

Include:

1. Skills the candidate should learn or demonstrate.
2. Resume sections that could be improved.
3. Projects that could strengthen the resume.
4. Suggestions for improving bullet points.
5. Keywords from the job description that should be reflected
   when truthful.
6. Ways to better demonstrate existing experience.


========================
FINAL REPORT FORMAT
========================

Use exactly these sections:

# 1. Job Requirements

# 2. Skills Clearly Present

# 3. Skill Gaps

# 4. Experience Gaps

# 5. Strengths to Highlight

# 6. Improvement Recommendations

# 7. Suggested Resume Improvements

# 8. Final Summary


IMPORTANT RULES:

- Do not invent information.
- Do not create fake experience.
- Do not create fake certifications.
- Do not assume missing skills.
- Clearly distinguish "not stated" from "not evidenced".
- Focus only on job-related qualifications.
- Do not make hiring or rejection decisions.
- Do not infer sensitive personal characteristics.
""",

            expected_output=(
                "A structured resume review containing job requirements, "
                "skills present, skill gaps, experience gaps, strengths, "
                "recommendations, resume improvements, and a final summary."
            ),

            agent=resume_agent
        )


        # ------------------------------------------
        # CREATE CREW
        # ------------------------------------------

        crew = Crew(

            agents=[resume_agent],

            tasks=[review_task],

            process=Process.sequential,

            verbose=False
        )


        # ------------------------------------------
        # RUN CREW
        # ------------------------------------------

        with st.spinner(
            "🤖 AI is reviewing your resume..."
        ):

            result = crew.kickoff()


        # ------------------------------------------
        # DISPLAY RESULT
        # ------------------------------------------

        st.success("✅ Resume review completed!")

        st.header("📊 Resume Review Report")

        st.markdown(str(result))


        # ------------------------------------------
        # DOWNLOAD REPORT
        # ------------------------------------------

        st.download_button(
            label="📥 Download Report",
            data=str(result),
            file_name="resume_review_report.md",
            mime="text/markdown"
        )


    except Exception as e:

        st.error(
            "Something went wrong while running the AI agent."
        )

        st.exception(e)
