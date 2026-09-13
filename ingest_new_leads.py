import json

batch_2 = [
  {"name": "Beyond Smiles Dental Clinic", "city": "Bengaluru", "vertical": "clinic", "rating": "4.9", "reviews": "528", "email": "drshobithshetty@gmail.com"},
  {"name": "Dr C Jagadeesh's Dental Clinic", "city": "Bengaluru", "vertical": "clinic", "rating": "4.8", "reviews": "850", "email": "drcjagadeeshdentalclinic@gmail.com"},
  {"name": "Rural Blues", "city": "Bengaluru", "vertical": "restaurant", "rating": "4.1", "reviews": "6851", "email": "gm@ruralblues.com"},
  {"name": "Tapadia Diagnostics", "city": "Hyderabad", "vertical": "clinic", "rating": "4.2", "reviews": "5768", "email": "support@tapadiadiagnostics.com"},
  {"name": "Zonkk", "city": "Chennai", "vertical": "restaurant", "rating": "4.6", "reviews": "5990", "email": "reservations@zonkk.in"},
  {"name": "Café Ciro", "city": "Noida", "vertical": "restaurant", "rating": "4.4", "reviews": "909", "email": "Unityventures120@gmail.com"},
  {"name": "The Ivy Restaurant", "city": "Gurugram", "vertical": "restaurant", "rating": "4.6", "reviews": "1691", "email": "theivygurugram@gmail.com"},
  {"name": "The Project Cafe", "city": "Ahmedabad", "vertical": "restaurant", "rating": "4.0", "reviews": "4002", "email": "info@theprojectcafe.co"},
  {"name": "The House of MG", "city": "Ahmedabad", "vertical": "hotel", "rating": "4.5", "reviews": "3587", "email": "customercare@houseofmg.com"},
  {"name": "Amaraanth", "city": "Goa", "vertical": "hotel", "rating": "4.9", "reviews": "26", "email": "reservations@amaraanth.com"},
  {"name": "Forte Kochi", "city": "Kochi", "vertical": "hotel", "rating": "4.5", "reviews": "1292", "email": "reservationfk@thepaul.in"},
  {"name": "Avalon Spa Chandigarh", "city": "Chandigarh", "vertical": "salon", "rating": "4.3", "reviews": "220", "email": "info@avalondayspa.in"},
  {"name": "The Salt House", "city": "Kolkata", "vertical": "restaurant", "rating": "4.2", "reviews": "1515", "email": "tshservice@magicpotfoodsco.com"},
  {"name": "The Flour Works", "city": "Pune", "vertical": "restaurant", "rating": "4.2", "reviews": "6151", "email": "meeta.makhecha@gmail.com"},
  {"name": "Little Monk", "city": "Indore", "vertical": "restaurant", "rating": "4.6", "reviews": "7524", "email": "info@oye24.com"}
]

with open("email_pipeline.json", "r", encoding="utf-8") as f:
    data = json.load(f)

prospects_dict = data.get("prospects", {})

added = 0
for lead in batch_2:
    email_key = lead["email"].strip().lower()
    if email_key not in prospects_dict:
        prospects_dict[email_key] = {
            "name": lead["name"],
            "city": lead["city"],
            "vertical": lead["vertical"],
            "rating": str(lead["rating"]),
            "reviews": str(lead["reviews"]),
            "initial_sent_at": None,
            "followup_sent_at": None,
            "status": "QUEUED"
        }
        added += 1

data["prospects"] = prospects_dict

with open("email_pipeline.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"SUCCESS: Added {added} fresh metro leads to email_pipeline.json.")
print(f"Total prospects in pipeline: {len(prospects_dict)}")