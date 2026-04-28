# 🤖 AI-Powered Service Desk Assistant

> **Status: 🚧 Active Development — Phase 7 Complete**

An AI-powered service desk tool built by a 9-year service operations veteran
to solve real problems I experienced firsthand managing 24/7 support teams.

---

## 🎯 The Problem This Solves

In high-volume service desk environments, engineers waste significant time on:
- Manually classifying and routing incoming tickets
- Writing repetitive first-response messages
- Searching through knowledge base articles during triage
- Summarizing long ticket threads during shift handovers

This tool automates those tasks using AI - freeing engineers to focus
on actual problem-solving.

---

## ✨ Planned Features

| Phase | Feature | Description | Status |
|-------|---------|-------------|--------|
| 1 |🎫Ticket Classifier | Classify ticket type and priority | ✅ Complete |
| 2 |💬Response Generator | SLA-aware professional reply draft | ✅ Complete |
| 3 |📚KB Recommender | Match ticket to KB articles | ✅ Complete |
| 4 |🖥 Web Demo (Streamlit) | Interactive UI to demo all features | ✅ Complete |
| 5 |📝Ticket Summarizer | Summarize long threads into 3-line handover notes | ✅ Complete |
| 6 |🚨Ticket Triage & Escalation | n8n webhook routing + Gmail alert for high severity | ✅ Complete |
| 7 |🔍KB Suggestion Before Escalation | Suggest KB resolution before escalating | ✅ Complete |
| 8 |📊Ticket History Log | Log and display all submitted tickets | 🔄 In Progress |
| 9 |📈Ops Dashboard | Visual metrics — severity counts, categories | ⏳ Planned |

---

## 🏗 Architecture

![Architecture Diagram](./assets/architecture.png)

**Tab 1 — Ticket Analyser**
- User submits a ticket via Streamlit UI
- OpenAI GPT-4o-mini classifies category, priority, and generates a response
- Sentence Transformers match the ticket to the most relevant KB article via cosine similarity

**Tab 2 — Ticket Summariser**
- User pastes a full ticket thread
- OpenAI GPT-4o-mini generates a 3-bullet summary, status, and handover note

**Tab 3 — Ticket Triage & Escalation**
- User submits a ticket with category and severity via Streamlit UI
- Ticket is sent via POST request to an n8n Cloud webhook
- n8n IF node checks severity — routes HIGH to Gmail escalation alert
- Low/normal severity tickets receive a standard confirmation response
- Gmail node sends an instant email alert for high priority incidents

---

## ⚠️ Limitations / Future Improvements

- Demo version uses manual text input only
- No authentication or role-based access yet
- Results depend on prompt quality and LLM output consistency
- Live demo uses API-backed requests, so token usage should be controlled
- n8n workflow requires production URL activation for persistent demo

---

## ⚡Future Automation

- Ticket history log with persistent storage
- Ops dashboard with visual severity and category metrics
- Slack notification channel alongside Gmail
- Confidence scoring and evaluation logging

---

## 🛠 Tech Stack

- **Python 3.11+**
- **OpenAI API** (GPT-4o) - classification and generation
- **Streamlit** - demo web interface
- **GitHub** - version control and portfolio
- **Sentence Transformers** (all-MiniLM-L6-v2)
- **n8n Cloud** - workflow automation, severity routing and escalation

---

## 💡 Why I Built This

After 9 years running service desk operations hiring 20+ engineers,
managing 24/7 shifts, designing SLA frameworks - I saw firsthand how much
repetitive cognitive work could be automated without losing the human
judgment that actually matters.

This project is my practical exploration of that intersection:
**service operations expertise + AI tooling**.

## 🚀 Live Demo
[Try the app here](https://darjan86-ai-service-desk-assistant.streamlit.app/)

## How to Run Locally
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file: `OPENAI_API_KEY=sk-your-key`
4. Run: `python -m streamlit run app.py`

## 📸 Screenshots

### Interface
<img width="787" height="1526" alt="image" src="https://github.com/user-attachments/assets/dff4741c-9d0b-4f46-99aa-2bc4b941b43e" />


### Analysis Results
<img width="1052" height="810" alt="Screenshot 2026-04-21 133749" src="https://github.com/user-attachments/assets/255ac464-6db1-4fe0-a61b-9b191c2eed45" />
<img width="1063" height="635" alt="Suggested response" src="https://github.com/user-attachments/assets/27fcee22-2fbc-4c5e-8f00-b3595929774a" />
<img width="1027" height="710" alt="Screenshot 2026-04-21 133930" src="https://github.com/user-attachments/assets/0ffe21de-7509-4cc1-896b-7cd716d40b81" />

### Ticket Summarizer Results
<img width="1021" height="1026" alt="Screenshot 2026-04-21 143126" src="https://github.com/user-attachments/assets/2707faf3-557f-49db-b764-b336b2b3c0cb" />
<img width="983" height="908" alt="Screenshot 2026-04-21 143035" src="https://github.com/user-attachments/assets/73eedcd2-3ce0-4261-b344-61a8941b9c1e" />

---

## 👤 About the Author

**Darjan Stojanovski** - Service Operations Manager with 9+ years in SaaS support operations.
ITIL4 Foundation | AWS Cloud Practitioner | Open to remote roles.

🔗 [LinkedIn](linkedin.com/in/darjan-stojanovski-ab527812a)
