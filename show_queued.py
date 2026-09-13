import json
from cold_email_agent import generate_email_content

with open("email_pipeline.json", "r", encoding="utf-8") as f:
    pipeline = json.load(f)

queued = [p for p in pipeline if p.get("status") == "QUEUED"]
print(f"=== FOUND {len(queued)} QUEUED PROSPECTS ===\n")

for i, p in enumerate(queued, 1):
    subject, body = generate_email_content(p)
    print(f"[{i}/{len(queued)}] ----------------------------------------")
    print("TO:", p["email"])
    print("NAME:", p["name"], "(", p["vertical"].upper(), ") -", p["city"])
    print("SUBJECT:", subject)
    print("BODY:")
    print(body)
    print("------------------------------------------------\n")

