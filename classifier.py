import os
import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ── KNOWLEDGE BASE ────────────────────────────────────────────────────────────
# Mock KB articles — replace with real ones later

KNOWLEDGE_BASE = [
    {
        "id": "KB001",
        "title": "VPN Connection Issues",
        "content": """
        Common VPN issues and fixes:
        1. Restart the VPN client application completely
        2. Check internet connection is active before launching VPN
        3. Verify credentials — password may have expired
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
        5. Check for any indicator lights — no lights may mean PSU failure
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
        4. Clear print queue — cancel all pending jobs
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
        1. Check database server status — ping server IP
        2. Verify connection string in application config is correct
        3. Check firewall rules — port 1433 (SQL) or 5432 (PostgreSQL) must be open
        4. Review database server logs for error messages
        5. Check active connections — may have hit max connection limit
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
        3. Check asset inventory first — refurbished equipment may be available
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
        1. Check Task Manager for high CPU/RAM processes — end if unnecessary
        2. Run disk cleanup and clear temp files
        3. Check available disk space — less than 10% free causes slowdowns
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
        1. Check approved software list first — may already be pre-approved
        2. User submits request via Service Portal with business justification
        3. Security team reviews non-standard software requests (2-3 days)
        4. IT deploys approved software via SCCM/Intune remotely
        5. User must not install unapproved software — policy violation
        6. For urgent licensed software: escalate to IT Manager for expedited review
        7. License cost must be approved by department head for paid software
        """
    }
]


# ── LOAD EMBEDDING MODEL ──────────────────────────────────────────────────────

print("⏳ Loading AI model (first run may take 1-2 minutes to download)...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Model loaded.\n")

# Pre-compute embeddings for all KB articles (done once at startup)
kb_embeddings = embedding_model.encode(
    [article["content"] for article in KNOWLEDGE_BASE]
)


# ── PHASE 4: KB RECOMMENDER ───────────────────────────────────────────────────

def find_best_kb_article(ticket_text, top_n=1):
    """Find the most relevant KB article for a given ticket."""
    ticket_embedding = embedding_model.encode([ticket_text])
    similarities = cosine_similarity(ticket_embedding, kb_embeddings)[0]
    best_index = np.argmax(similarities)
    best_score = similarities[best_index]
    best_article = KNOWLEDGE_BASE[best_index]
    return best_article, round(float(best_score), 3)


# ── PHASE 1 & 2: Classifier ───────────────────────────────────────────────────

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
    return response.choices[0].message.content


# ── PHASE 3: Response Generator ───────────────────────────────────────────────

def generate_full_response(ticket_text, category, priority, kb_article=None):
    kb_context = ""
    if kb_article:
        kb_context = f"""
Relevant knowledge base article to inform your response:
Title: {kb_article['title']} ({kb_article['id']})
Content: {kb_article['content']}

Use this KB article to make your response more specific and actionable.
"""

    prompt = f"""
You are a senior IT service desk engineer writing a professional response to a support ticket.

Ticket details:
- User's message: \"{ticket_text}\"
- Category: {category}
- Priority: {priority}
{kb_context}

Write a complete, professional support response that:
1. Acknowledges the issue with empathy
2. Sets clear expectations (response time based on priority: P1=30min, P2=2hrs, P3=8hrs, P4=next business day)
3. Provides specific first steps the user can try immediately (use the KB article if provided)
4. Closes warmly and professionally

Keep it concise (4-6 sentences). Do not use placeholders like [Name].
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional IT service desk engineer. Write clear, empathetic, actionable support responses."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content


# ── MAIN: Interactive Loop ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  AI SERVICE DESK ASSISTANT — by Darjan Stojanovski")
    print("  Phases: Classifier + Response Generator + KB Recommender")
    print("  Type a ticket. Type 'quit' to exit.")
    print("=" * 60)

    while True:
        print()
        ticket = input("📩 Enter ticket: ").strip()

        if not ticket:
            print("⚠️  Please enter a ticket description.")
            continue

        if ticket.lower() in ("quit", "exit"):
            print("\n👋 Goodbye!")
            break

        print("\n⏳ Classifying ticket...")

        try:
            # Step 1: Classify
            raw_result = classify_ticket(ticket)
            parsed = json.loads(raw_result)

            category = parsed.get("category", "N/A")
            priority = parsed.get("priority", "N/A")
            reason   = parsed.get("priority_reason", "N/A")

            print(f"\n{'─' * 60}")
            print(f"  📂 Category:  {category}")
            print(f"  🚨 Priority:  {priority}")
            print(f"  💡 Reason:    {reason}")

            # Step 2: Find best KB article
            kb_article, similarity_score = find_best_kb_article(ticket)
            print(f"\n  📚 KB Article: [{kb_article['id']}] {kb_article['title']}")
            print(f"  🎯 Relevance:  {similarity_score * 100:.0f}% match")
            print(f"{'─' * 60}")

            # Step 3: Generate response informed by KB
            print("\n⏳ Generating KB-informed response...")
            full_response = generate_full_response(
                ticket, category, priority, kb_article
            )

            print(f"\n  📧 SUGGESTED RESPONSE:")
            print(f"{'─' * 60}")
            print(f"{full_response}")
            print(f"{'─' * 60}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()