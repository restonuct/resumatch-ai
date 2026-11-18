# 🎯 ResuMatch AI — Intelligent Resume Analyzer & ATS Optimization Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/AI_Engine-Google_Gemini_3.x-8E75C2.svg)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Production-Ready-brightgreen.svg)](#)

> **ResuMatch AI** is a production-grade talent acquisition and candidate optimization platform. It bridges the gap between candidate resumes and Applicant Tracking Systems (ATS) by providing automated skill gap analysis, keyword density scoring, and actionable recruiter-grade resume enhancements powered by **Google Gemini AI**.

---

## 🌟 Key Capabilities

* **📊 4-Tier ATS Evaluation:**
  * **Overall ATS Alignment %** with automatic fit classification (*Exceptional*, *Strong*, *Moderate*, *Low*).
  * **Technical Skills Alignment %** comparing core stack competencies.
  * **Experience & Impact Match %** evaluating role-specific seniority and responsibility depth.
  * **Keyword Indexing %** verifying ATS scanner discoverability.
* **🧩 Deep Skills Matrix:**
  * Categorized display of confirmed matching competencies.
  * High-visibility missing keyword badges identifying critical filter criteria.
* **✍️ STAR-Method Resume Bullet Rewrites:**
  * AI-generated before-and-after bullet point transformations using action verbs, metrics, and targeted tech stack keywords.
* **⚡ One-Click Benchmark Profiles:**
  * Preloaded profiles for *AI & Python Developers*, *Data Scientists & ML Engineers*, and *Full-Stack Engineers*.
* **📄 Multi-Format Ingestion:**
  * In-memory PDF parsing via `pypdf` with instant plain-text extraction and word statistics.
* **🛡️ Resilient Model Orchestration:**
  * Automatic failover across Google Gemini models (`gemini-3.1-flash-lite` → `gemini-3.5-flash-lite` → `gemini-3.8-flash`) with schema-guaranteed JSON output.
* **📥 1-Click Export:**
  * Download comprehensive evaluation reports in Markdown (`.md`) or raw JSON (`.json`).

---

## 🏗️ Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────┐
│                   User Interface                       │
│     Streamlit (app.py)   /   Zero-Install (index.html) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               Document Ingestion Layer                 │
│         pypdf (Python)   /   PDF.js (Client-Side)      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│            Resilience & Orchestration Engine           │
│     gemini-3.1-flash-lite ──► gemini-3.5 ──► gemini-3.8 │
│              Native JSON Schema Enforcement            │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                   Output Analytics                     │
│  Match %  │  Skill Gap  │  STAR Rewrites  │  MD/JSON   │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart Guide

### Prerequisites
* Python 3.10+
* A free [Google Gemini API Key](https://aistudio.google.com/)

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/your-org/resumatch-ai.git
cd resumatch-ai

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Secrets
Copy `.env.example` to `.env` and insert your Gemini API key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY="your_gemini_api_key_here"
```

### 3. Launch the Application Locally
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Deployment Guide

### Option 1: Streamlit Community Cloud (Recommended & Free)
Streamlit Community Cloud provides 1-click native hosting with full WebSocket support:
1. Navigate to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
2. Click **New app** and select:
   * **Repository:** `restonuct/resumatch-ai`
   * **Branch:** `main`
   * **Main file path:** `app.py`
3. Under **Advanced settings**, add your secret:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
4. Click **Deploy!**

### Option 2: Vercel (Edge Web Deployment)
The repository includes automated `vercel.json` routing:
1. Import `restonuct/resumatch-ai` into [Vercel](https://vercel.com/).
2. Vercel automatically deploys the responsive web interface to its global edge network.

### Option 3: Render / Railway / Hugging Face Spaces
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`


---

## 🌐 Standalone Zero-Install Browser Interface
For offline demonstrations, rapid client previews, or environments without Python:
```bash
# macOS
open index.html

# Linux
xdg-open index.html

# Windows
start index.html
```

---

## 🔒 Security & Privacy Notice
* All resume data and job descriptions are processed **ephemerally in-memory**.
* No documents or candidate personally identifiable information (PII) are stored on disk or persistent third-party databases.
* API keys are loaded strictly through local environment variables or Streamlit secrets and excluded via `.gitignore`.

---

## 📄 License
Distributed under the Apache 2.0 License.
