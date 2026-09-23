import os

# --------------------------------------------------
# CREWAI / GROQ CACHE FIX
# --------------------------------------------------

try:
    import crewai.llms.cache as crewai_cache
    crewai_cache.mark_cache_breakpoint = lambda message: message
except Exception:
    pass


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
# GROQ API KEY
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
    "This application uses one CrewAI agent "
    "for the complete resume review process."
)


# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# --------------------------------------------------
# DOCX TEXT EXTRACTION
# --------------------------------------------------

def extract_text_from_docx(uploaded_file):
    document = Document(uploaded_file)

    text = ""

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"

    return text


# --------------------------------------------------
# RESUME TEXT EXTRACTION
# --------------------------------------------------

def extract_resume_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)

    elif file_name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)

    return ""


# --------------------------------------------------
# UPLOAD RESUME
# --------------------------------------------------

st.header("1️⃣ Upload Resume")

uploaded_resume = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)


# --------------------------------------------------
# JOB DESCRIPTION
# --------------------------------------------------

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
# MAIN APPLICATION
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

    with st.spinner("📖 Reading your resume..."):

        resume_text = extract_resume_text(
            uploaded_resume
        )


    if not resume_text.strip():

        st.error(
            "I could not extract readable text from "
            "your resume. Please try another PDF or DOCX file."
        )

        st.stop()


    # ----------------------------------------------
    # CREATE LLM
    # ----------------------------------------------

    try:

        llm = LLM(
            model=model_name,
            api_key=groq_api_key,
            temperature=0.2
        )


        # ------------------------------------------
        # ONE CREWAI AGENT
        # ------------------------------------------

        resume_agent = Agent(

            role="Resume Review Specialist",

            goal=(
                "Review a candidate's resume against a "
                "job description, identify job-related "
                "skill and experience gaps, and provide "
                "practical resume improvement recommendations."
            ),

            backstory=(
                "You are a careful professional resume "
                "review specialist. You compare resumes "
                "with job descriptions using only the "
                "information provided. You never invent "
                "experience, skills, certifications, or "
                "qualifications."
            ),

            llm=llm,

            verbose=False,

            allow_delegation=False
        )


        # ------------------------------------------
        # ONE TASK
        # ------------------------------------------

        review_task = Task(

            description=f"""

You are reviewing a candidate resume against a job description.

==================================================
CANDIDATE RESUME
==================================================

{resume_text}


==================================================
JOB DESCRIPTION
==================================================

{job_description}


==================================================
STAGE 1 — INPUT PARSING
==================================================

Extract the important information from both inputs.

From the JOB DESCRIPTION identify:

1. Job title
2. Technical skills
3. Programming languages
4. Libraries and frameworks
5. AI and machine learning requirements
6. Databases or vector stores
7. Cloud requirements
8. DevOps requirements
9. Soft skills
10. Education requirements
11. Experience requirements
12. Certifications


From the RESUME identify:

1. Technical skills
2. Programming languages
3. Frameworks
4. AI and machine learning skills
5. Projects
6. Work experience
7. Education
8. Certifications
9. Soft skills
10. Other relevant qualifications


==================================================
STAGE 2 — GAP ANALYSIS
==================================================

Compare the job requirements with the resume.

Identify:

1. Skills clearly present in the resume.
2. Skills required by the job but not clearly evidenced.
3. Experience requirements that are not clearly demonstrated.
4. Requirements that partially match.
5. Requirements that need stronger evidence.


IMPORTANT:

Do NOT assume a skill.

For example, if the job requires Python but
Python is not mentioned in the resume, write:

"Python — Not evidenced in the resume."

Do not assume the candidate knows Python.


==================================================
STAGE 3 — RECOMMENDATIONS
==================================================

Provide practical recommendations.

Include:

1. Skills to learn or strengthen.
2. Existing skills that should be highlighted.
3. Projects that could strengthen the resume.
4. Suggestions for improving resume bullet points.
5. Relevant job-description keywords that could be
   reflected when truthful.
6. Suggestions for demonstrating existing experience.
7. Suggestions for improving project descriptions.


==================================================
FINAL REPORT
==================================================

Return the result using these sections:

# 1. Job Requirements

# 2. Skills Clearly Present

# 3. Skill Gaps

# 4. Experience Gaps

# 5. Strengths to Highlight

# 6. Improvement Recommendations

# 7. Suggested Resume Improvements

# 8. Final Summary


==================================================
IMPORTANT RULES
==================================================

- Never invent information.
- Never create fake experience.
- Never create fake skills.
- Never create fake certifications.
- Never assume missing information.
- Use "Not stated" when information is absent.
- Use "Not evidenced in the resume" when a requirement
  is not demonstrated.
- Focus only on job-related qualifications.
- Do not make hiring or rejection decisions.
- Do not infer sensitive personal characteristics.
- Give practical and realistic recommendations.
- Keep the report clear and useful.
""",

            expected_output=(
                "A structured resume review containing "
                "job requirements, skills clearly present, "
                "skill gaps, experience gaps, strengths, "
                "improvement recommendations, suggested "
                "resume improvements, and a final summary."
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

        st.success(
            "✅ Resume review completed successfully!"
        )

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
            "Something went wrong while running "
            "the AI agent."
        )

        st.exception(e)
