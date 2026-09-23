# resume-review-agent-application
📄 Resume Review Agent

An AI-powered Resume Review Agent that compares a resume with a job description and provides skill gaps, experience gaps, strengths, and improvement recommendations.

🚀 Features

- Upload a resume in PDF or DOCX format
- Extract resume text automatically
- Enter a job description
- Compare resume skills with job requirements
- Identify skill gaps
- Identify experience gaps
- Highlight strengths
- Generate resume improvement recommendations
- Download the review report
- Uses CrewAI with a single AI agent
- Uses Groq for LLM inference
- Streamlit interface

🧠 Project Workflow

Resume
   +
Job Description
       ↓
Input Parsing
       ↓
Gap Analysis
       ↓
Recommendations
       ↓
Final Resume Review Report

🛠️ Technologies

- Python
- Streamlit
- CrewAI
- Groq
- PyPDF
- python-docx

🤖 Agent Architecture

This project intentionally uses one CrewAI agent.

             Resume
                │
                ↓
        ┌─────────────────┐
        │ Resume Review    │
        │ Specialist Agent │
        └─────────────────┘
                ↑
                │
        Job Description
                │
                ↓
        Input Parsing
                ↓
          Gap Analysis
                ↓
        Recommendations
                ↓
          Final Report

🔑 API Key Setup

The application requires a Groq API key.

For Streamlit deployment, add the following to Streamlit Secrets:

GROQ_API_KEY = "your_groq_api_key_here"

Never upload your real API key to GitHub.

💻 Run Locally

Install the requirements:

pip install -r requirements.txt

Create:

.streamlit/secrets.toml

Add:

GROQ_API_KEY = "your_groq_api_key_here"

Run the application:

streamlit run app.py

📄 Supported Resume Formats

Currently supported:

- PDF
- DOCX

📊 Review Sections

The generated report contains:

1. Job Requirements
2. Skills Clearly Present
3. Skill Gaps
4. Experience Gaps
5. Strengths to Highlight
6. Improvement Recommendations
7. Suggested Resume Improvements
8. Final Summary

⚠️ Important

The application reviews the information provided in the resume and job description. It does not invent skills, experience, certifications, or qualifications.

The application is designed to provide job-related resume feedback and does not make hiring or rejection decisions.

☁️ Streamlit Deployment

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Connect your GitHub repository.
4. Select "app.py".
5. Select Python 3.11 if available in the deployment settings.
6. Add your "GROQ_API_KEY" in Streamlit Secrets.
7. Deploy the application.

📁 Project Structure

resume-review-agent/
│
├── app.py
├── requirements.txt
├── runtime.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml.example

🎯 Learning Goals

This project demonstrates:

- AI agents
- CrewAI
- LLM integration
- Prompt engineering
- Resume parsing
- Job requirement extraction
- Skill gap analysis
- Streamlit application development
- API key management
- GitHub project management
- AI application deployment
