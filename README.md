# User Interaction Predictor (UIP)

User Interaction Predictor is a system for simulating user behavior in "For You" recommendation feeds across social media platforms such as TikTok, Instagram, and YouTube.

It is designed as a core component for **algorithmic auditing**, enabling structured, reproducible experiments on how AI-driven recommendation systems respond to different user profiles.

This system runs **locally** and is intended to be integrated into a broader audit pipeline.

---

## 🎯 Purpose

The main goal of UIP is to:

- Simulate realistic user interactions (likes, skips, watch time, etc.)
- Enable **sockpuppeting-based audits**
- Support reproducible research of recommendation algorithms
- Provide a foundation for AI auditing methodologies

The project is part of the research initiative:

👉 **https://kinit.sk/project/ai-auditology-social-media-ai-algorithms-auditing/**

---

## ⚙️ Key Features

- Simulation of user behavior in "For You" feeds
- Two prediction modes:
  - **V1 (fast, heuristic-based)**
  - **V2 (LLM-driven, content-aware)**
- Video content analysis (visual + music)
- Decision engine for interaction prediction
- Local-first architecture
- Agent-based audit execution

---

## 🧩 System Overview

UIP is not a standalone solution. It is designed to work with:

- **Mobile/Frontend Agent** → executes predicted actions
- **Visualization Tool** → interprets collected audit data

---

## 🚀 Quick Start

### Requirements

*This system was developed and tested using specific versions of the technologies listed below. While these represent the verified environment, other versions may also be compatible*

- Python >= 3.12.5
- Node.js >= 22.8.0 (for frontend)
- Docker
- Git
- Azure OpenAI deployment
- Stable internet connection

---

### Installation & Execution

```bash
# Clone repository
git clone https://github.com/erikmacak/user-interaction-predictor.git

# Backend setup
cd src/backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]

# Infrastructure
cd ..
docker compose up -d

# Environment variables
cp .env.example .env
# → fill in values

# Database
cd backend
alembic upgrade head

# Create admin
python scripts/create_admin.py

# Run tests
pytest tests/ -v

# Run backend
fastapi dev main.py

# Frontend
cd src/frontend
npm install
npm run dev
```

**Note on Test Results:** Some integration tests (~30) may return a 'FAILED' status with a 429 error. This is expected behavior caused by the active Rate Limiter during rapid test execution. All components were verified in a controlled development environment. As long as the remaining tests pass, the system is correctly configured.

### Access
 + Frontend: **http://localhost:3000**
 + Backend: **http://localhost:8000**

---

## 🧪 Basic Usage Flow
 1. Create an agent
 2. Define audit scenario (user profile)
 3. Start an audit session
 4. Call API endpoint `POST /predict_actions`
 5. Execute returned actions via agents

---

## 👤 User Modeling

Accurate simulation depends heavily on user profile definition. 

---

## ⚠️ Limitations
 + Single-agent limitation (LLM constraint)
   + Same API key
 + Platform instability
   + Frequently change UI
   + Break automation flows
 + Not a final production-ready solution
   + Never going to be

---

## 📊 Performance

**Performance depends on:**
 + Internet connection
 + LLM latency
 + Video length
 + Number of analyzed segments

**Optimized for:**
 + 15–180 second videos
   + *less than 15 seconds*: May not respond before video ends
   + *more than 180 seconds*: Not analyzed
 + Tested primarily on Instagram Reels

---

## 🧱 Tech Stack

**Backend** (along with its specific libraries):
 + Python (FastAPI)
 + Pydantic
 + OpenCV
 + yt-dlp
 + ShazamAPI
 + *and much more*

**Frontend**:
 + Next.js (React-based)

---

## 📌 Disclaimer

**This project represents an experimental foundation for AI auditing methodologies.**

It is:
 + Not a finished product
 + Subject to breaking changes
 + Intended for research and extension

---

## 🧑‍💻 Contributing

**Feel free to fork, modify, and extend the system!**