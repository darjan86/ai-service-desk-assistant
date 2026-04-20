import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# ── PHASE 1 & 2: Classifier ──────────────────────────────────────────────────

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


# ── PHASE 3: Response Generator ──────────────────────────────────────────────

def generate_full_response(ticket_text, category, priority):
    prompt = f"""
You are a senior IT service desk engineer writing a professional response to a support ticket.

Ticket details:
- User's message: \"{ticket_text}\"
- Category: {category}
- Priority: {priority}

Write a complete, professional support response that:
1. Acknowledges the issue with empathy
2. Sets clear expectations (response time based on priority: P1=30min, P2=2hrs, P3=8hrs, P4=next business day)
3. Asks for any missing information needed to resolve it (if applicable)
4. Closes warmly and professionally

Keep it concise (4-6 sentences). Do not use placeholders like [Name] — write it as a real engineer would send it.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional IT service desk engineer. Write clear, empathetic support responses."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content


# ── MAIN: Interactive Loop ────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  AI SERVICE DESK ASSISTANT — by Darjan Stojanovski")
    print("  Phases: Classifier + Response Generator")
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
            print(f"{'─' * 60}")

            # Step 2: Generate full response
            print("\n⏳ Generating response...")
            full_response = generate_full_response(ticket, category, priority)

            print(f"\n  📧 SUGGESTED RESPONSE:")
            print(f"{'─' * 60}")
            print(f"{full_response}")
            print(f"{'─' * 60}")

        except Exception as e:
            print(f"❌ Error: {e}")



if __name__ == "__main__":
    main()