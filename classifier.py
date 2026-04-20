import json
from openai import OpenAI

# --- CONFIGURATION ---
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file automatically
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- TICKET DATA ---
sample_tickets = [
    "My laptop won't turn on after the Windows update last night.",
    "I can't access the company VPN from home since this morning.",
    "The printer on floor 3 is showing an offline error for the whole team.",
    "I need a new monitor for my desk, the current one has dead pixels.",
    "Production database is throwing connection timeout errors — 5 users affected.",
]

# --- CLASSIFIER FUNCTION ---
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


# --- MAIN RUNNER ---
def main():
    print("=" * 60)
    print("  AI SERVICE DESK CLASSIFIER — by Darjan Stojanovski")
    print("  Type a ticket description and press Enter.")
    print("  Type 'quit' or 'exit' to stop.")
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

        print("\n⏳ Analysing...")

        try:
            raw_result = classify_ticket(ticket)
            parsed = json.loads(raw_result)

            print(f"\n{'=' * 60}")
            print(f"  Category:        {parsed.get('category', 'N/A')}")
            print(f"  Priority:        {parsed.get('priority', 'N/A')}")
            print(f"  Reason:          {parsed.get('priority_reason', 'N/A')}")
            print(f"  Suggested Reply: {parsed.get('suggested_response', 'N/A')}")
            print(f"{'=' * 60}")

        except Exception as e:
            print(f"❌ Error: {e}")
            
if __name__ == "__main__":
    main()
