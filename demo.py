import os
from pathlib import Path
import httpx
from dotenv import load_dotenv

# Explicitly load .env from the project directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(f"GROQ_API_KEY not found or empty in {env_path}")

SYSTEM_PROMPT = """You are the AI WhatsApp Receptionist for Hotel The Panache, Patna.
Answer guest inquiries politely, concisely, and accurately based ONLY on the following information:

- Standard Room: ₹3,500/night (AC, WiFi, breakfast included)
- Deluxe Room: ₹5,500/night (AC, WiFi, breakfast, city view)
- Suite: ₹9,000/night (AC, WiFi, breakfast, living area)
- Check-in: 12:00 PM | Check-out: 11:00 AM
- Location: RamGulam Chowk, South Gandhi Maidan, Patna
- Banquet & Event Halls: Available for weddings, corporate events (contact banquet team)
- Contact for booking/availability confirmation: sales@thepanachepatna.com | +91-7544002851

Guidelines:
- You do NOT have live access to room availability. Politely state room types and rates, then direct guests to email/phone for booking confirmation.
- Keep responses concise and suitable for WhatsApp (bullet points, clear formatting).
- Do not invent amenities, prices, or policies not listed above."""

def ask_receptionist(user_message: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen3.6-27b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "reasoning_effort": "none",
        "temperature": 0.3
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

if __name__ == "__main__":
    test_query = "Is a room available tonight?"
    print(f"User: {test_query}\n")
    reply = ask_receptionist(test_query)
    print(f"Bot:\n{reply}")