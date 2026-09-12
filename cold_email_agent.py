import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
PIPELINE_FILE = BASE_DIR / "email_pipeline.json"

# IST Timezone (UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Verticals & Templates
TEMPLATES = {
    "hotel": {
        "subject": "AI receptionist for {name}",
        "body": (
            "{name} is clearly one of {city}'s top-rated destinations, with over {reviews} online reviews "
            "and a {rating} rating showing the strong trust guests place in your hospitality.\n\n"
            "Your hotel is active 24/7, which means every unanswered WhatsApp inquiry during late or busy "
            "hours is a direct loss of a customer to your competitor.\n\n"
            "I have a solution for this: I can build a personal AI receptionist for your hotel that works 24/7 "
            "to handle most routine booking and banquet inquiries on WhatsApp.\n\n"
            "If you are interested, can I send you a brief demo video showing how this AI receptionist handles "
            "booking inquiries instantly?\n\n"
            "— Aman Raj\nAI Developer"
        )
    },
    "clinic": {
        "subject": "AI receptionist for {name}",
        "body": (
            "{name} is clearly one of {city}'s leading health clinics, with over {reviews} patient reviews "
            "and a {rating} rating showing the trust patients place in your care.\n\n"
            "Your clinic receives inquiries constantly, which means missed calls or delayed WhatsApp responses "
            "during busy consultation hours lead patients to book elsewhere.\n\n"
            "I have a solution for this: I can build a personal AI receptionist for your clinic that works 24/7 "
            "to handle appointment bookings, clinic hours, and fee inquiries on WhatsApp.\n\n"
            "If you are interested, can I send you a brief demo video showing how this AI receptionist handles "
            "patient inquiries instantly?\n\n"
            "— Aman Raj\nAI Developer"
        )
    },
    "restaurant": {
        "subject": "AI receptionist for {name}",
        "body": (
            "{name} is clearly one of {city}'s premier dining spots, with over {reviews} online reviews "
            "and a {rating} rating showing how much diners love your experience.\n\n"
            "During peak lunch and dinner hours, staff are too busy to answer calls, leading to lost table "
            "reservations and party bookings.\n\n"
            "I have a solution for this: I can build a personal AI receptionist for your restaurant that works 24/7 "
            "to take table reservations, share menus, and handle party inquiries on WhatsApp.\n\n"
            "If you are interested, can I send you a brief demo video showing how this AI receptionist handles "
            "reservation inquiries instantly?\n\n"
            "— Aman Raj\nAI Developer"
        )
    },
    "follow_up": {
        "subject": "Re: AI receptionist for {name}",
        "body": (
            "I wanted to follow up on my previous email regarding the AI receptionist for {name}, as I'm not "
            "sure if it reached you—would you like me to send over the brief demo video?\n\n"
            "— Aman Raj\nAI Developer"
        )
    }
}

def is_within_send_window() -> bool:
    """Rule 79: Only allow sends between 10:00 AM and 5:00 PM IST."""
    now_ist = datetime.now(IST)
    hour = now_ist.hour
    return 10 <= hour < 17

def load_pipeline() -> dict:
    if PIPELINE_FILE.exists():
        with open(PIPELINE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"prospects": {}}

def save_pipeline(data: dict):
    with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_email(vertical: str, name: str, city: str, rating: str, reviews: str, is_followup: bool = False) -> dict:
    if is_followup:
        tmpl = TEMPLATES["follow_up"]
        return {
            "subject": tmpl["subject"].format(name=name),
            "body": tmpl["body"].format(name=name)
        }
    
    tmpl = TEMPLATES.get(vertical.lower(), TEMPLATES["hotel"])
    return {
        "subject": tmpl["subject"].format(name=name),
        "body": tmpl["body"].format(name=name, city=city, rating=rating, reviews=reviews)
    }

def add_prospect(email: str, name: str, city: str, vertical: str, rating: str, reviews: str):
    pipeline = load_pipeline()
    email_key = email.lower().strip()
    
    if email_key in pipeline["prospects"]:
        print(f"[EXISTS] {email_key} is already in the pipeline.")
        return

    pipeline["prospects"][email_key] = {
        "name": name,
        "city": city,
        "vertical": vertical,
        "rating": rating,
        "reviews": reviews,
        "initial_sent_at": None,
        "followup_sent_at": None,
        "status": "QUEUED"  # QUEUED -> INITIAL_SENT -> FOLLOWUP_SENT -> MAX
    }
    save_pipeline(pipeline)
    print(f"[ADDED] {name} ({email_key}) queued successfully.")

def render_due_sends():
    """Outputs generated emails ready for sending, enforcing send windows and follow-up rules."""
    pipeline = load_pipeline()
    now_ist = datetime.now(IST)
    window_ok = is_within_send_window()

    print(f"\n--- Cold Email Agent Status [{now_ist.strftime('%Y-%m-%d %H:%M:%S IST')}] ---")
    print(f"Sending Window Active (10AM-5PM IST): {'YES' if window_ok else 'NO (Drafts only)'}\n")

    ready_count = 0
    for email, data in pipeline["prospects"].items():
        status = data["status"]
        
        # Initial send check
        if status == "QUEUED":
            ready_count += 1
            content = generate_email(data["vertical"], data["name"], data["city"], data["rating"], data["reviews"], is_followup=False)
            print(f"==================================================")
            print(f"ACTION: INITIAL SEND -> {data['name']} ({email})")
            print(f"SUBJECT: {content['subject']}")
            print(f"BODY:\n{content['body']}")
            print(f"==================================================\n")

        # Follow-up check (must be >= 3 days after initial)
        elif status == "INITIAL_SENT":
            sent_dt = datetime.fromisoformat(data["initial_sent_at"])
            days_passed = (now_ist - sent_dt).days
            if days_passed >= 3:
                ready_count += 1
                content = generate_email(data["vertical"], data["name"], data["city"], data["rating"], data["reviews"], is_followup=True)
                print(f"==================================================")
                print(f"ACTION: FOLLOW-UP DUE ({days_passed} days elapsed) -> {data['name']} ({email})")
                print(f"SUBJECT: {content['subject']}")
                print(f"BODY:\n{content['body']}")
                print(f"==================================================\n")

    if ready_count == 0:
        print("No pending emails or follow-ups due right now.")

def mark_sent(email: str, is_followup: bool = False):
    """Marks an email as verified sent in the pipeline log."""
    pipeline = load_pipeline()
    email_key = email.lower().strip()
    
    if email_key not in pipeline["prospects"]:
        print(f"[ERROR] Prospect {email_key} not found.")
        return

    now_str = datetime.now(IST).isoformat()
    if not is_followup:
        pipeline["prospects"][email_key]["initial_sent_at"] = now_str
        pipeline["prospects"][email_key]["status"] = "INITIAL_SENT"
        print(f"[UPDATED] {email_key} marked INITIAL_SENT at {now_str}")
    else:
        pipeline["prospects"][email_key]["followup_sent_at"] = now_str
        pipeline["prospects"][email_key]["status"] = "MAX"
        print(f"[UPDATED] {email_key} marked FOLLOWUP_SENT (MAX REACHED) at {now_str}")
        
    save_pipeline(pipeline)

if __name__ == "__main__":
    print("Cold Email Agent loaded. Usage: Import or run functions directly.")