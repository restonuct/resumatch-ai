"""
ATS Resume Optimizer — Production Resume Evaluation & Job Alignment Engine
"""

import os
import json
import pandas as pd
import streamlit as st
from pypdf import PdfReader

# Load GEMINI_API_KEY from environment or local .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from google import genai
from google.genai import types


# ---------------- BENCHMARK PROFILES ---------------- #
PRESETS = {
    "AI & Python Developer": {
        "resume": """Alex Morgan
San Francisco, CA | (555) 234-5678 | alex.morgan@email.com | github.com/alexmorgan | linkedin.com/in/alexmorgan

PROFESSIONAL SUMMARY:
Results-driven AI & Python Developer with hands-on experience architecting LLM-powered applications, workflow automation pipelines, and scalable backend services.

TECHNICAL SKILLS:
- Programming Languages: Python, SQL, JavaScript (ES6+), HTML5, CSS3
- AI & LLM Frameworks: Google Gemini API, OpenAI APIs, Prompt Engineering, Vector Search, LangChain
- Web & Backend Frameworks: Streamlit, FastAPI, Flask, REST APIs, JSON Schema
- Libraries & Tools: Pandas, NumPy, pypdf, Requests, Git, GitHub, Docker, Postman, Linux CLI

PROFESSIONAL PROJECTS:
1. Automated Multi-Agent Content Orchestration Engine
   - Architected an end-to-end multi-agent automation pipeline in n8n integrating Google Gemini API for intelligent generation.
   - Connected Stability AI REST API via HTTP Request endpoints with multipart/form-data for automated visual asset generation.
   - Reduced content turnaround time by 80% with automated webhook scheduling and robust error handling.

2. Cloud Parking Rate & Billing Microservice (Python CLI / REST)
   - Built a modular Python utility calculating tiered pricing logic based on vehicle category and duration.
   - Applied object-oriented design patterns, defensive input validation, and unit testing achieving 100% test pass rate.

EDUCATION:
- Bachelor of Science in Computer Science & Artificial Intelligence (Honors)
  Dean's Honor List | 3.85 GPA""",
        "job": """Junior AI & Python Developer
Location: Remote / Hybrid
Role Overview:
We are seeking an ambitious AI & Python Developer to build production prototypes, automate business workflows, and integrate state-of-the-art Generative AI models.

Responsibilities:
- Develop interactive web prototypes and operational dashboards using Streamlit and Python.
- Integrate Generative AI LLM APIs (Google Gemini, Claude, or OpenAI) for text processing, evaluation, and automation.
- Design RESTful API connectors, webhook integrations, and data handling scripts.
- Write modular, well-documented code using Git/GitHub for version control.
- Collaborate with the team on prompt optimization, few-shot prompts, and structured LLM outputs.

Required Qualifications & Skills:
- Strong proficiency in Python (OOP, data structures, scripting, clean code principles).
- Hands-on experience with Streamlit or lightweight web frameworks (FastAPI/Flask).
- Direct experience integrating LLM APIs (Google Gemini API / OpenAI API) and Prompt Engineering.
- Proficient with Git, GitHub version control, and collaborative workflows.
- Familiarity with REST APIs, JSON parsing, and HTTP requests.

Bonus / Preferred Skills:
- Experience with Docker containers, cloud deployment (GCP/AWS), SQL databases, or workflow automation tools."""
    },
    "Data Scientist & ML Engineer": {
        "resume": """Sarah Chen
New York, NY | (555) 345-6789 | sarah.chen@email.com | github.com/sarahchen | linkedin.com/in/sarahchen

PROFESSIONAL SUMMARY:
Data Scientist with proven experience in exploratory data analysis, predictive machine learning pipelines, and statistical modeling using Python and SQL.

TECHNICAL SKILLS:
- Data Science & ML: Python, Pandas, NumPy, Scikit-Learn, Matplotlib, Seaborn, SQL, Jupyter
- Machine Learning: Supervised/Unsupervised Learning, Regression, Random Forests, XGBoost, Clustering
- Workflow & Tools: Git, GitHub, REST APIs, Google Gemini API, Docker, PostgreSQL

KEY PROJECTS:
1. Customer Churn Prediction & Retention Pipeline
   - Cleaned, transformed, and engineered features across 50,000+ customer records using Pandas and SQL.
   - Built and cross-validated Random Forest and Gradient Boosting models, improving predictive recall to 86%.
2. Automated Business Intelligence Extraction System
   - Implemented a Streamlit dashboard powered by Google Gemini API to analyze raw CSV metrics and produce executive summaries.""",
        "job": """Data Scientist & Machine Learning Associate
Role Overview:
Join our analytics organization to develop predictive machine learning models, explore complex enterprise datasets, and build data-driven intelligence solutions.

Requirements:
- Strong mathematical and practical foundations in Python, Pandas, NumPy, and statistical data modeling.
- Hands-on experience training ML algorithms (Regression, Classification, Clustering, Random Forests).
- Data visualization expertise using Matplotlib, Seaborn, or Plotly.
- Relational database querying and data wrangling with SQL.
- Familiarity with LLM prompt engineering, Git version control, and Jupyter Notebook environments."""
    },
    "Full-Stack Software Engineer": {
        "resume": """Marcus Vance
Austin, TX | (555) 456-7890 | marcus.vance@email.com | github.com/marcusvance | linkedin.com/in/marcusvance

PROFESSIONAL SUMMARY:
Full-Stack Software Engineer experienced in creating accessible, responsive web applications and reliable microservices.

TECHNICAL SKILLS:
- Frontend: HTML5, Modern CSS/Tailwind, JavaScript (ES6+), TypeScript, React, Streamlit
- Backend: Python (FastAPI/Flask), Node.js, Express, REST APIs, JSON Schema
- Databases & Cloud: PostgreSQL, SQLite, Docker, Git, GitHub Actions CI/CD

PROJECTS:
1. ResuMatch ATS Evaluation Platform (Streamlit, Gemini API, Python)
   - Built a responsive web application for resume keyword matching and real-time ATS optimization scoring.
2. Developer Portfolio & Interactive Project Showcase
   - Developed a responsive web app with CI/CD deployment on GitHub Pages.""",
        "job": """Full-Stack Software Engineer
Responsibilities:
- Build and maintain modern, accessible web applications using React, TypeScript, and modern CSS.
- Develop backend RESTful APIs, data validation schemas, and microservices with FastAPI or Node.js.
- Work with relational databases like PostgreSQL and containerized deployments using Docker.
- Implement automated testing, code linting, and CI/CD pipelines with GitHub Actions."""
    }
}


# ---------------- INTERNAL BACKEND LOGIC ---------------- #
def get_backend_api_key() -> str:
    """Read API key strictly from server environment / secrets (never exposed to users)."""
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            key = ""
    return key.strip()


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract plain text from uploaded PDF resume."""
    try:
        reader = PdfReader(uploaded_file)
        pages_text = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages_text.append(f"--- Page {idx + 1} ---\n{text.strip()}")
        return "\n\n".join(pages_text)
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""


def build_analysis_prompt(resume_text: str, job_desc: str) -> str:
    """Construct an ATS evaluation prompt requesting structured JSON."""
    return f"""You are a senior ATS (Applicant Tracking System) engineer and expert technical hiring specialist.
Analyze the candidate's RESUME against the target JOB DESCRIPTION thoroughly and objectively.

Return ONLY a valid JSON object with EXACTLY this structure (no markdown fences, no explanatory text outside the JSON):
{{
  "match_score": <integer from 0 to 100>,
  "fit_verdict": "<'Exceptional Match' | 'Strong Match' | 'Moderate Match' | 'Needs Improvement'>",
  "summary": "<2-3 sentence executive assessment of candidate fit, strengths, and primary gaps>",
  "breakdown": {{
    "skills_score": <integer from 0 to 100>,
    "experience_score": <integer from 0 to 100>,
    "keywords_score": <integer from 0 to 100>
  }},
  "matching_skills": [
    "<Skill 1>",
    "<Skill 2>",
    "<Skill 3>"
  ],
  "missing_skills": [
    "<Missing Skill 1>",
    "<Missing Skill 2>",
    "<Missing Skill 3>"
  ],
  "suggestions": [
    "<Actionable, specific tip 1>",
    "<Actionable, specific tip 2>",
    "<Actionable, specific tip 3>",
    "<Actionable, specific tip 4>",
    "<Actionable, specific tip 5>"
  ],
  "bullet_rewrites": [
    {{
      "original": "<A weak or generic phrase/bullet found in the candidate resume>",
      "improved": "<ATS-optimized rewrite incorporating action verb, relevant skill keyword, and quantified impact (STAR method)>",
      "why": "<Brief reason why this improves ATS keyword indexing and recruiter appeal>"
    }},
    {{
      "original": "<Second weak or improvable bullet>",
      "improved": "<Second ATS-optimized rewrite with metrics and tech stack>",
      "why": "<Brief reason>"
    }}
  ]
}}

CANDIDATE RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_desc}
"""


def analyze_resume(resume_text: str, job_desc: str, api_key: str) -> dict:
    """Execute analysis via resilient backend fallback (Gemini models)."""
    client = genai.Client(api_key=api_key)
    prompt = build_analysis_prompt(resume_text, job_desc)
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.2,
    )

    models_to_try = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
    ]

    last_error = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.strip("`")
                if raw.lower().startswith("json"):
                    raw = raw[4:].strip()
            return json.loads(raw)
        except Exception as err:
            last_error = err
            continue

    raise RuntimeError(f"Service temporarily busy. Please retry shortly. ({last_error})")


# ---------------- PAGE CONFIG & CLEAN STYLING ---------------- #
st.set_page_config(
    page_title="ATS Resume Optimizer — Check Match Score & Keyword Gaps",
    page_icon=":material/task_alt:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit Deploy button, header menu, and decoration
st.html("""
<style>
    /* Clean up all Streamlit developer chrome */
    .stDeployButton, [data-testid="stToolbar"], [data-testid="stDecoration"], footer, #MainMenu {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        height: 0px !important;
        background: transparent !important;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }
</style>
""")


# ---------------- CLEAN HERO BANNER ---------------- #
with st.container(border=True):
    st.title(":material/task_alt: ATS Resume Optimizer")
    st.write(
        "Upload or paste your resume alongside any target job description to get an instant ATS compatibility score, "
        "uncover missing keywords, and receive recruiter-approved bullet rewrites."
    )


# ---------------- PRESET SHORTCUTS ---------------- #
st.write("")
col_presets_label, col_presets_pills = st.columns([1, 5], vertical_alignment="center")
with col_presets_label:
    st.markdown("**:material/bolt: Try a Sample Role:**")
with col_presets_pills:
    preset_keys = list(PRESETS.keys())
    chosen_preset = st.pills(
        "Sample Roles:",
        preset_keys,
        default=preset_keys[0],
        selection_mode="single",
        label_visibility="collapsed",
        key="chosen_preset_pills"
    )

if "current_preset_loaded" not in st.session_state:
    st.session_state["current_preset_loaded"] = chosen_preset
    st.session_state["resume_text_val"] = PRESETS[chosen_preset]["resume"]
    st.session_state["job_desc_val"] = PRESETS[chosen_preset]["job"]

if chosen_preset != st.session_state["current_preset_loaded"]:
    st.session_state["current_preset_loaded"] = chosen_preset
    st.session_state["resume_text_val"] = PRESETS[chosen_preset]["resume"]
    st.session_state["job_desc_val"] = PRESETS[chosen_preset]["job"]
    st.rerun()


# ---------------- INPUT WORKSPACE ---------------- #
col_resume, col_job = st.columns(2)

with col_resume:
    with st.container(border=True):
        st.subheader(":material/description: 1. Your Resume")
        resume_tab_pdf, resume_tab_text = st.tabs([
            ":material/upload_file: Upload PDF",
            ":material/edit_note: Edit Text"
        ])
        
        with resume_tab_pdf:
            uploaded_pdf = st.file_uploader(
                "Upload Resume PDF:",
                type=["pdf"],
                help="Automatically extracts text from your PDF.",
                label_visibility="collapsed"
            )
            if uploaded_pdf is not None:
                pdf_text = extract_text_from_pdf(uploaded_pdf)
                if pdf_text:
                    st.session_state["resume_text_val"] = pdf_text
                    st.success(f"Loaded {uploaded_pdf.name} successfully.")
        
        with resume_tab_text:
            edited_text = st.text_area(
                "Resume Plain Text:",
                value=st.session_state["resume_text_val"],
                height=270,
                key="resume_textarea",
                label_visibility="collapsed"
            )
            st.session_state["resume_text_val"] = edited_text

        resume_words = len(st.session_state["resume_text_val"].split())
        st.caption(f":material/format_align_left: {resume_words} words · {len(st.session_state['resume_text_val']):,} characters")

with col_job:
    with st.container(border=True):
        st.subheader(":material/work: 2. Target Job Description")
        job_edited = st.text_area(
            "Target Job Description:",
            value=st.session_state["job_desc_val"],
            height=322,
            key="job_textarea",
            label_visibility="collapsed",
            help="Paste the full job requirements and responsibilities here."
        )
        st.session_state["job_desc_val"] = job_edited
        
        job_words = len(job_edited.split())
        st.caption(f":material/format_align_left: {job_words} words · {len(job_edited):,} characters")


# ---------------- ACTION CONTROLS ---------------- #
st.write("")
btn_col1, btn_col2 = st.columns([3, 1])

with btn_col1:
    analyze_btn = st.button(
        ":material/sparkles: Analyze Resume & Check ATS Score",
        type="primary",
        width="stretch",
    )

with btn_col2:
    if st.button(":material/refresh: Reset Sample", width="stretch"):
        st.session_state["resume_text_val"] = PRESETS["AI & Python Developer"]["resume"]
        st.session_state["job_desc_val"] = PRESETS["AI & Python Developer"]["job"]
        st.session_state["current_preset_loaded"] = "AI & Python Developer"
        if "ats_result" in st.session_state:
            del st.session_state["ats_result"]
        st.rerun()


# ---------------- ANALYSIS EXECUTION ---------------- #
if analyze_btn:
    cur_resume = st.session_state.get("resume_text_val", "").strip()
    cur_job = st.session_state.get("job_desc_val", "").strip()
    backend_key = get_backend_api_key()

    if not cur_resume or not cur_job:
        st.warning("Please provide both a resume and a job description.")
    elif not backend_key:
        st.error("Server API key is not configured. Please ensure GEMINI_API_KEY is defined in your .env file.")
    else:
        with st.spinner("Analyzing resume against job requirements..."):
            try:
                res_data = analyze_resume(cur_resume, cur_job, backend_key)
                st.session_state["ats_result"] = res_data
                st.toast("Analysis complete!", icon="✅")
            except Exception as e:
                st.error(f"Analysis error: {e}")


# ---------------- PRESENT RESULTS ---------------- #
if "ats_result" in st.session_state:
    data = st.session_state["ats_result"]
    score = int(data.get("match_score", 0))
    fit_verdict = data.get("fit_verdict", "Evaluated")
    breakdown = data.get("breakdown", {})
    skills_score = int(breakdown.get("skills_score", score))
    exp_score = int(breakdown.get("experience_score", max(score - 6, 0)))
    kw_score = int(breakdown.get("keywords_score", score))

    st.write("")
    st.divider()

    st.header(":material/analytics: ATS Evaluation Results")

    # 4 Core KPI Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(
            label="Overall ATS Match",
            value=f"{score}%",
            delta=fit_verdict,
            border=True,
            chart_data=[max(score - 30, 10), max(score - 15, 20), max(score - 5, 40), score],
            chart_type="area",
        )
    with kpi2:
        st.metric(
            label="Skills Alignment",
            value=f"{skills_score}%",
            delta="Tech Stack",
            border=True,
            chart_data=[max(skills_score - 25, 10), max(skills_score - 10, 30), skills_score],
            chart_type="line",
        )
    with kpi3:
        st.metric(
            label="Experience Relevance",
            value=f"{exp_score}%",
            delta="Role Fit",
            border=True,
            chart_data=[max(exp_score - 20, 10), max(exp_score - 8, 30), exp_score],
            chart_type="line",
        )
    with kpi4:
        st.metric(
            label="Keyword Density",
            value=f"{kw_score}%",
            delta="Search Index",
            border=True,
            chart_data=[max(kw_score - 35, 10), max(kw_score - 15, 25), kw_score],
            chart_type="area",
        )

    # Executive Recruiter Summary Box
    with st.container(border=True):
        st.subheader(":material/rate_review: Recruiter Assessment Summary")
        st.write(data.get("summary", "No summary provided."))

    # Benchmark Alignment Chart
    with st.container(border=True):
        st.subheader(":material/leaderboard: Alignment Breakdown (Candidate vs 100% Target)")
        df_chart = pd.DataFrame({
            "Category": ["Overall Match", "Skills Alignment", "Experience Fit", "Keyword Indexing"],
            "Candidate Score": [score, skills_score, exp_score, kw_score],
            "Target Benchmark": [100, 100, 100, 100],
        }).set_index("Category")
        st.bar_chart(df_chart, height=210)

    # In-Depth Tabs
    tab_skills, tab_tips, tab_rewrites, tab_export = st.tabs([
        ":material/verified: Skills Breakdown",
        ":material/tips_and_updates: 5 Priority Improvements",
        ":material/auto_fix_high: Bullet Point Rewrites",
        ":material/file_download: Export Report",
    ])

    with tab_skills:
        col_matched, col_missing = st.columns(2)
        with col_matched:
            with st.container(border=True):
                st.markdown("#### :material/check_circle: Matching Skills Found")
                matches = data.get("matching_skills", [])
                if matches:
                    badges_html = " ".join([f":green-badge[✔ {m}]" for m in matches])
                    st.markdown(badges_html)
                else:
                    st.caption("No direct matching skills detected.")

        with col_missing:
            with st.container(border=True):
                st.markdown("#### :material/cancel: Missing Required Skills & Keywords")
                missing = data.get("missing_skills", [])
                if missing:
                    badges_missing = " ".join([f":orange-badge[✖ {m}]" for m in missing])
                    st.markdown(badges_missing)
                else:
                    st.success("All target skills were found in your resume!")

    with tab_tips:
        with st.container(border=True):
            st.markdown("#### :material/checklist: Actionable Steps to Improve ATS Ranking")
            for idx, tip in enumerate(data.get("suggestions", []), start=1):
                st.markdown(f"**{idx}.** {tip}")

    with tab_rewrites:
        st.markdown("#### :material/magic_button: High-Impact Bullet Rewrites (STAR Method)")
        st.caption("Optimize weak resume bullets into high-impact, keyword-rich statements:")
        
        rewrites = data.get("bullet_rewrites", [])
        if rewrites:
            for item in rewrites:
                with st.container(border=True):
                    st.markdown(f":red-badge[Original / Weak:] *\"{item.get('original', '')}\"*")
                    st.markdown(f":green-badge[ATS-Optimized:] **\"{item.get('improved', '')}\"**")
                    if item.get("why"):
                        st.caption(f"**:material/psychology: Why this works:** {item.get('why')}")
        else:
            st.caption("No bullet rewrites generated.")

    with tab_export:
        with st.container(border=True):
            st.markdown("#### :material/download: Export Your Report")
            
            export_text = f"""# ATS Resume Evaluation Report
Overall Match Score: {score}/100 ({fit_verdict})

## Score Breakdown
- Skills Alignment: {skills_score}%
- Experience Fit: {exp_score}%
- Keyword Indexing: {kw_score}%

## Recruiter Assessment
{data.get('summary', '')}

## Matching Skills
{chr(10).join(['- ' + s for s in data.get('matching_skills', [])])}

## Missing Skills & Keywords
{chr(10).join(['- ' + s for s in data.get('missing_skills', [])])}

## Actionable Suggestions
{chr(10).join([f"{i}. {s}" for i, s in enumerate(data.get('suggestions', []), 1)])}
"""
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                st.download_button(
                    label=":material/article: Download Markdown Report (.md)",
                    data=export_text,
                    file_name="ATS_Resume_Evaluation_Report.md",
                    mime="text/markdown",
                    width="stretch",
                )
            with dcol2:
                st.download_button(
                    label=":material/data_object: Download Raw JSON (.json)",
                    data=json.dumps(data, indent=2),
                    file_name="ATS_Resume_Evaluation_Report.json",
                    mime="application/json",
                    width="stretch",
                )
