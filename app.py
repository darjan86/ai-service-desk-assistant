import os
import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import streamlit as st

N8N_WEBHOOK_URL = st.secrets["N8N_WEBHOOK_URL"]

def send_to_n8n(ticket_text, category, severity):
    payload = {
        "ticket_text": ticket_text,
        "category": category,
        "severity": severity
    }
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
import csv
import os
from datetime import datetime

def log_ticket(title, severity, category, kb_match, escalated):
    log_file = "ticket_log.csv"
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "title", "severity", "category", "kb_match", "escalated"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "severity": severity,
            "category": category,
            "kb_match": kb_match,
            "escalated": escalated
        })

# PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Service Desk Assistant",
    page_icon="🎫",
    layout="centered"
)

# KNOWLEDGE BASE ────────────────────────────────────────────────────────────

KNOWLEDGE_BASE = [
    {
        "id": "KB001",
        "title": "VPN Connection Issues",
        "content": """
        Common VPN issues and fixes:
        1. Restart the VPN client application completely
        2. Check internet connection is active before launching VPN
        3. Verify credentials - password may have expired
        4. Try switching VPN server/region if multiple are available
        5. Disable and re-enable network adapter
        6. Reinstall VPN client if above steps fail
        Escalate to Network team if issue persists across multiple users.
        """
    },
    {
        "id": "KB002",
        "title": "Laptop Won't Turn On",
        "content": """
        Steps to troubleshoot a laptop that won't power on:
        1. Check power cable is firmly connected and power outlet works
        2. Hold power button 30 seconds to force discharge
        3. Remove battery (if removable), hold power 15 seconds, reinsert
        4. Try booting without external devices (USB, monitors)
        5. Check for any indicator lights - no lights may mean PSU failure
        6. If recent Windows update, may need recovery mode boot
        Escalate to Hardware team if no response after these steps.
        """
    },
    {
        "id": "KB003",
        "title": "Password Reset Procedure",
        "content": """
        Standard password reset process:
        1. Verify user identity via employee ID or manager confirmation
        2. Use Active Directory to reset: ADUC > right-click user > Reset Password
        3. Set temporary password, force change on next login
        4. Confirm user can log in with new credentials
        5. For MFA-locked accounts, also reset authenticator app enrollment
        6. Log reset action in ticket with timestamp for audit trail
        """
    },
    {
        "id": "KB004",
        "title": "Printer Offline Error",
        "content": """
        Resolving printer showing as offline:
        1. Check printer is powered on and paper/toner are not depleted
        2. Right-click printer in Windows > See what's printing > Printer menu
        3. Uncheck 'Use Printer Offline' if checked
        4. Clear print queue - cancel all pending jobs
        5. Restart Print Spooler service: services.msc > Print Spooler > Restart
        6. Remove and re-add printer if above fails
        7. For network printers: verify IP address hasn't changed via printer settings page
        """
    },
    {
        "id": "KB005",
        "title": "Database Connection Timeout",
        "content": """
        Immediate steps for database connection timeout (P1):
        1. Check database server status - ping server IP
        2. Verify connection string in application config is correct
        3. Check firewall rules - port 1433 (SQL) or 5432 (PostgreSQL) must be open
        4. Review database server logs for error messages
        5. Check active connections - may have hit max connection limit
        6. Restart application service (NOT database) as temporary fix
        7. Escalate to DBA team immediately if affecting production
        Always raise a Major Incident for production DB issues affecting 3+ users.
        """
    },
    {
        "id": "KB006",
        "title": "New Hardware Request Process",
        "content": """
        Process for requesting new hardware (monitors, keyboards, laptops):
        1. User submits request via Service Portal with business justification
        2. Line manager must approve requests over £500
        3. Check asset inventory first - refurbished equipment may be available
        4. Raise purchase order via procurement system if no stock
        5. Standard lead time: 5-7 business days for in-stock items
        6. Configure device and enroll in MDM before delivery to user
        7. Update asset register with new device serial number and assigned user
        """
    },
    {
        "id": "KB007",
        "title": "Microsoft 365 / Outlook Issues",
        "content": """
        Common Microsoft 365 troubleshooting steps:
        1. Sign out and sign back into Microsoft 365 account
        2. Clear Office credentials from Windows Credential Manager
        3. Run Office repair tool: Control Panel > Programs > Office > Change > Repair
        4. For Outlook not syncing: remove and re-add email account
        5. Check Microsoft 365 service health at admin.microsoft.com
        6. Disable add-ins if Outlook crashes on startup
        7. License issues: verify user has active license in M365 Admin Center
        """
    },
    {
        "id": "KB008",
        "title": "Slow Computer Performance",
        "content": """
        Steps to resolve slow computer performance:
        1. Check Task Manager for high CPU/RAM processes - end if unnecessary
        2. Run disk cleanup and clear temp files
        3. Check available disk space - less than 10% free causes slowdowns
        4. Scan for malware using Defender or corporate antivirus
        5. Check for pending Windows updates and install
        6. Disable startup programs: Task Manager > Startup tab
        7. If laptop is overheating, clean vents and ensure airflow
        8. Consider RAM upgrade if consistently above 85% usage
        """
    },
    {
        "id": "KB009",
        "title": "Multi-Factor Authentication (MFA) Issues",
        "content": """
        Resolving MFA and two-factor authentication problems:
        1. Ensure authenticator app time is synced (check app settings > sync)
        2. Try backup codes if available
        3. If phone lost: admin can disable MFA temporarily in Azure AD
        4. Re-enroll authenticator: Azure AD > User > Authentication methods > Reset
        5. For SMS-based MFA: verify phone number is correct in user profile
        6. Never disable MFA permanently without security team approval
        Always verify user identity via video call before resetting MFA.
        """
    },
    {
        "id": "KB010",
        "title": "Software Installation Request",
        "content": """
        Process for requesting software installation:
        1. Check approved software list first - may already be pre-approved
        2. User submits request via Service Portal with business justification
        3. Security team reviews non-standard software requests (2-3 days)
        4. IT deploys approved software via SCCM/Intune remotely
        5. User must not install unapproved software - policy violation
        6. For urgent licensed software: escalate to IT Manager for expedited review
        7. License cost must be approved by department head for paid software
        """
    }
]

# LOAD MODEL ────────────────────────────────────────────────────────────────

@st.cache_resource
def load_model_and_embeddings():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode([article["content"] for article in KNOWLEDGE_BASE])
    return model, embeddings

embedding_model, kb_embeddings = load_model_and_embeddings()

# FUNCTIONS ─────────────────────────────────────────────────────────────────

def classify_ticket(ticket_text):
    prompt = f"""
You are an expert IT service desk classifier with 10 years of experience.

Analyze the following support ticket and return a JSON response with exactly these fields:
- "category": one of [Hardware, Software, Network, Access, Infrastructure, Other]
- "priority": one of [P1 - Critical, P2 - High, P3 - Medium, P4 - Low]
- "priority_reason": one sentence explaining why you chose that priority
- "suggested_response": a short, professional first reply to send to the user (2-3 sentences)

Ticket:
\"{ticket_text}\"

Return only valid JSON. No explanation outside the JSON block.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise IT service desk classifier. Always return valid JSON."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2
    )
    return json.loads(response.choices[0].message.content)


def find_best_kb_article(ticket_text):
    ticket_embedding = embedding_model.encode([ticket_text])
    similarities = cosine_similarity(ticket_embedding, kb_embeddings)[0]
    best_index = np.argmax(similarities)
    best_score = similarities[best_index]
    return KNOWLEDGE_BASE[best_index], round(float(best_score) * 100, 1)


def generate_full_response(ticket_text, category, priority, kb_article):
    prompt = f"""
You are a senior IT service desk engineer writing a professional response to a support ticket.

Ticket details:
- User's message: \"{ticket_text}\"
- Category: {category}
- Priority: {priority}

Relevant knowledge base article:
Title: {kb_article['title']} ({kb_article['id']})
Content: {kb_article['content']}

Write a complete, professional support response that:
1. Acknowledges the issue with empathy
2. Sets clear expectations (P1=30min, P2=2hrs, P3=8hrs, P4=next business day)
3. Provides specific first steps using the KB article
4. Closes warmly and professionally

Keep it concise (4-6 sentences). Do not use placeholders like [Name].
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional IT service desk engineer."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content


def summarize_thread(thread_text):
    # Trim thread if too long (keep first 3000 characters)
    if len(thread_text) > 3000:
        thread_text = thread_text[:3000] + "\n[Thread trimmed for length]"

    prompt = f"""
You are an experienced IT service desk team lead preparing a shift handover note.

Analyze the following support ticket thread and return a JSON response with exactly these fields:
- "issue_summary": a list of exactly 3 strings, each being one bullet point
- "status": one of [Resolved, Unresolved, Escalated, Pending User Response]
- "status_reason": one sentence explaining the current status
- "handover_note": a ready-to-send shift handover note (3-5 sentences)

Ticket thread:
\"{thread_text}\"

Return only valid JSON. No explanation outside the JSON block. Example format:
{{
  "issue_summary": ["Point 1", "Point 2", "Point 3"],
  "status": "Resolved",
  "status_reason": "Issue was resolved after rollback.",
  "handover_note": "The incident has been resolved..."
}}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise IT service desk team lead. Always return valid JSON only, no extra text."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2,
        max_tokens=800
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw)

# PRIORITY COLOURS ──────────────────────────────────────────────────────────

PRIORITY_COLORS = {
    "P1 - Critical": "#FF4B4B",
    "P2 - High":     "#FF8C00",
    "P3 - Medium":   "#1F77B4",
    "P4 - Low":      "#2CA02C",
}

STATUS_COLORS = {
    "Resolved":              "#2CA02C",
    "Unresolved":            "#FF4B4B",
    "Escalated":             "#FF8C00",
    "Pending User Response": "#1F77B4",
}

# UI ────────────────────────────────────────────────────────────────────────

st.title("🎫 AI Service Desk Assistant")
st.markdown("*Powered by GPT-4o-mini + Semantic KB Search*")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Ticket Analyser",
    "📝 Ticket Summarizer",
    "🚨 Triage & Escalation",
    "📋 Ticket History Log"
])

# TAB 1: TICKET ANALYSER ────────────────────────────────────────────────────
# existing Ticket Classifier code
with tab1:
    st.markdown("### 📩 Submit a Ticket")
    ticket_input = st.text_area(
        label="Describe the issue:",
        placeholder="e.g. I can't connect to the VPN from home since this morning...",
        height=120,
        max_chars=2000,
        label_visibility="collapsed",
        key="ticket_input"
    )
    char_count_1 = len(ticket_input)
    st.caption(f"📝 {char_count_1}/2000 characters · Demo app — do not paste sensitive production data.")

    analyse_clicked = st.button(
        "🔍 Analyse Ticket",
        type="primary",
        use_container_width=True,
        key="analyse_btn"
    )

    if analyse_clicked:
        if not ticket_input.strip():
            st.warning("⚠️ Please enter a ticket description first.")
        else:
            with st.spinner("Classifying ticket and searching knowledge base..."):
                try:
                    classification = classify_ticket(ticket_input)
                    kb_article, match_score = find_best_kb_article(ticket_input)
                    full_response = generate_full_response(
                        ticket_input,
                        classification["category"],
                        classification["priority"],
                        kb_article
                    )

                    st.markdown("---")
                    st.markdown("### 📊 Analysis Results")
                    st.success("Analysis completed successfully.", icon="✅")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**📂 Category**")
                        st.info(classification.get("category", "N/A"))
                    with col2:
                        priority = classification.get("priority", "N/A")
                        color = PRIORITY_COLORS.get(priority, "#888888")
                        st.markdown("**🚨 Priority**")
                        st.markdown(
                            f'<div style="background-color:{color}; color:white; '
                            f'padding:8px 16px; border-radius:8px; font-weight:bold; '
                            f'text-align:center;">{priority}</div>',
                            unsafe_allow_html=True
                        )


                    st.markdown("**💡 Priority Reason**")
                    st.markdown(f"> {classification.get('priority_reason', 'N/A')}")

                    st.markdown("---")
                    st.markdown("### 📚 Knowledge Base Match")
                    kb_col1, kb_col2 = st.columns([3, 1])
                    with kb_col1:
                        st.markdown(f"**[{kb_article['id']}] {kb_article['title']}**")
                    with kb_col2:
                        st.metric("Relevance", f"{match_score}%")
                    with st.expander("📖 View KB Article Content"):
                        st.markdown(kb_article["content"])

                    st.markdown("---")
                    st.markdown("### 📧 Suggested Response")
                    st.text_area(
                        label="Copy and send to user:",
                        value=full_response,
                        height=200,
                        label_visibility="visible",
                        key="response_output"
                    )

                except Exception:
                    st.error("❌ Analysis failed. Please check your input and try again. If the issue persists, the input may be too long.", icon="🚨")


# TAB 2: TICKET SUMMARIZER ──────────────────────────────────────────────────
# existing Shift Handover Summarizer code
with tab2:
    st.markdown("### 📋 Paste Ticket Thread")
    st.markdown("Paste the full back-and-forth conversation from any ticket below.")

    thread_input = st.text_area(
        label="Ticket thread:",
        placeholder="""e.g.
User [09:14]: My laptop won't connect to the VPN since this morning.
Agent [09:17]: Can you confirm which VPN client you're using?
User [09:18]: It's Cisco AnyConnect.
Agent [09:21]: Please try restarting the client and reconnecting.
User [09:35]: Still not working, same error message.
Agent [09:38]: I've escalated this to the Network team for investigation.""",
        height=220,
        max_chars=4000,
        label_visibility="collapsed",
        key="thread_input"
    )
    char_count_2 = len(thread_input)
    st.caption(f"📝 {char_count_2}/4000 characters · Demo app — do not paste sensitive production data. Long threads may be trimmed before analysis.")

    summarize_clicked = st.button(
        "📝 Summarise Thread",
        type="primary",
        use_container_width=True,
        key="summarise_btn"
    )

    if summarize_clicked:
        if not thread_input.strip():
            st.warning("⚠️ Please paste a ticket thread first.")
        else:
            with st.spinner("Analysing thread and generating handover note..."):
                try:
                    summary = summarize_thread(thread_input)

                    st.markdown("---")
                    st.markdown("### 📊 Thread Summary")
                    st.success("Thread analysed successfully.", icon="✅")

                    # Status badge
                    status = summary.get("status", "N/A")
                    status_color = STATUS_COLORS.get(status, "#888888")
                    st.markdown("**Current Status**")
                    st.markdown(
                        f'<div style="background-color:{status_color}; color:white; '
                        f'padding:8px 16px; border-radius:8px; font-weight:bold; '
                        f'text-align:center; max-width:250px;">{status}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f"> {summary.get('status_reason', 'N/A')}")

                    # Issue summary bullets
                    st.markdown("---")
                    st.markdown("### 🔍 Issue Summary")
                    bullets = summary.get("issue_summary", [])
                    if isinstance(bullets, list):
                        for bullet in bullets:
                            st.markdown(f"• {bullet}")
                    else:
                        st.markdown(bullets)

                    # Handover note
                    st.markdown("---")
                    st.markdown("### 🤝 Shift Handover Note")
                    st.text_area(
                        label="Ready to paste into your handover:",
                        value=summary.get("handover_note", "N/A"),
                        height=180,
                        label_visibility="visible",
                        key="handover_output"
                    )

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# TAB 3: Ticket Triage & Escalation n8n form ──────────────────────────────────────────────────
with tab3:
    st.markdown("### 🚨 Ticket Triage & Escalation")
    st.markdown("Submit a ticket for automated triage. A KB suggestion is checked first, then the ticket is routed based on severity.")

    with st.form("triage_form"):
        triage_input = st.text_area(
            label="Describe the issue:",
            placeholder="e.g. All users are locked out of the system since 9am...",
            height=120,
            max_chars=2000,
            label_visibility="collapsed",
            key="triage_input"
        )
        char_count_3 = len(triage_input)
        st.caption(f"📝 {char_count_3}/2000 characters · Demo app — do not paste sensitive production data.")

        col_cat, col_sev = st.columns(2)
        with col_cat:
            triage_category = st.selectbox(
                "Category",
                ["Access Issue", "Billing", "Incident", "Request", "Other"],
                key="triage_category"
            )
        with col_sev:
            triage_severity = st.selectbox(
                "Severity",
                ["low", "medium", "high"],
                key="triage_severity"
            )

        submitted = st.form_submit_button(
            "🚀 Submit to Workflow",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not triage_input.strip():
            st.warning("⚠️ Please enter a ticket description first.")
        else:
            st.markdown("---")

            # ── STEP 1: KB Suggestion ────────────────────────────────
            st.markdown("### 📚 Knowledge Base Suggestion")

            with st.spinner("Searching knowledge base..."):
                kb_article, match_score = find_best_kb_article(triage_input)

            if match_score >= 0.45:
                st.success(f"✅ Relevant KB article found — try this before escalating.", icon="💡")
                kb_col1, kb_col2 = st.columns([3, 1])
                with kb_col1:
                    st.markdown(f"**[{kb_article['id']}] {kb_article['title']}**")
                with kb_col2:
                    st.metric("Relevance", f"{match_score}%")
                with st.expander("📖 View KB Article Content"):
                    st.markdown(kb_article["content"])
            else:
                st.info("ℹ️ No strong KB match found for this ticket. Proceeding to workflow routing.", icon="📋")

            st.markdown("---")

            # ── STEP 2: Send to n8n Workflow ─────────────────────────
            st.markdown("### ⚙️ Workflow Routing")

            with st.spinner("Sending to n8n workflow..."):
                success = send_to_n8n(triage_input, triage_category, triage_severity)

            if success:
                if triage_severity == "high":
                    st.error(
                        "🚨 **High severity ticket submitted.** Escalation email alert has been triggered.",
                        icon="🚨"
                    )
                elif triage_severity == "medium":
                    st.warning(
                        "⚠️ **Medium severity ticket submitted.** Routed for priority handling.",
                        icon="⚠️"
                    )
                else:
                    st.success(
                        "✅ **Low severity ticket submitted.** Routed for standard handling.",
                        icon="✅"
                    )
                with sum_col3:
                    st.markdown("**📚 KB Match**")
                    kb_status = f"{match_score}% — {kb_article['title']}" if match_score >= 0.45 else "No strong match"
                # After severity/category/kb_match are determined, call:
                log_ticket(
                    title=triage_input,
                    severity=triage_severity,
                    category=triage_category,
                    kb_match=kb_article['title'] if match_score >= 0.45 else "No match",
                    escalated="Yes" if triage_severity == "high" else "No"
                )   
                # ── Routing Summary ───────────────────────────────────
                st.markdown("---")
                st.markdown("### 📋 Triage Summary")

                sum_col1, sum_col2, sum_col3 = st.columns(3)
                with sum_col1:
                    st.markdown("**📂 Category**")
                    st.info(triage_category)
                with sum_col2:
                    st.markdown("**🔴 Severity**")
                    severity_colors = {
                        "high": "#d9534f",
                        "medium": "#f0ad4e",
                        "low": "#5cb85c"
                    }
                    color = severity_colors.get(triage_severity, "#888888")
                    st.markdown(
                        f'<div style="background-color:{color}; color:white; '
                        f'padding:8px 16px; border-radius:8px; font-weight:bold; '
                        f'text-align:center;">{triage_severity.upper()}</div>',
                        unsafe_allow_html=True
                    )            
            else:
                st.error("❌ Could not reach the workflow. Check your webhook URL or n8n status.", icon="🚨")
# TAB 4: TICKET HISTORY LOG ──────────────────────────────────────────────────
with tab4:
    st.header("📋 Ticket History Log")

    log_file = "ticket_log.csv"

    if os.path.isfile(log_file):
        import pandas as pd
        df = pd.read_csv(log_file)
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🗑️ Clear Log"):
                os.remove(log_file)
                st.success("Log cleared.")
                st.rerun()
    else:
        st.info("No tickets logged yet. Submit a ticket in the Triage & Escalation tab to start.")

# FOOTER ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:12px;'>"
    "AI Service Desk Assistant · Built by Darjan Stojanovski · "
    "Powered by OpenAI GPT-4o-mini + Sentence Transformers"
    "</div>",
    unsafe_allow_html=True
)
