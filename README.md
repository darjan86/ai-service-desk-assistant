# 🤖 AI-Powered Service Desk Assistant

> **Status: ✅ Complete

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

| Feature | Description | Status |
|---------|-------------|--------|
| 🎫 Ticket Classifier     | Classify ticket type and priority  | ✅ Complete |
| 💬 Response Generator    | SLA-aware professional reply draft | ✅ Complete |
| 📚 KB Recommender        | Match ticket to KB articles        | ✅ Complete |
| 🖥 Web Demo (Streamlit)  | Interactive UI to demo all features | ✅ Complete |
| 📝 Ticket Summarizer | Summarize long threads into 3-line handover notes | ✅ Complete |

---

## 🛠 Tech Stack

- **Python 3.11+**
- **OpenAI API** (GPT-4o) - classification and generation
- **Streamlit** - demo web interface
- **GitHub** - version control and portfolio
- **Sentence Transformers** (all-MiniLM-L6-v2)

---

## 💡 Why I Built This

After 9 years running service desk operations hiring 20+ engineers,
managing 24/7 shifts, designing SLA frameworks - I saw firsthand how much
repetitive cognitive work could be automated without losing the human
judgment that actually matters.

This project is my practical exploration of that intersection:
**service operations expertise + AI tooling**.

## 🚀 Live Demo
[Try the app here]([https://your-app-link.streamlit.app](https://darjan86-ai-service-desk-assistant.streamlit.app/)

## How to Run Locally
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file: `OPENAI_API_KEY=sk-your-key`
4. Run: `python -m streamlit run app.py`

## 📸 Screenshots

### Interface
<img width="1796" height="805" alt="Screenshot 2026-04-21 133244" src="https://github.com/user-attachments/assets/53337c51-5d17-4e04-843a-fbbebdb0e37f" />
<img width="947" height="802" alt="Screenshot 2026-04-21 141132" src="https://github.com/user-attachments/assets/55b00d81-0057-4133-9606-00846cf549ad" />


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
