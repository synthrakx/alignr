import json
from cold_email_agent import add_prospect

prospects = [
    {
        "email": "magadhorodentalpatna@gmail.com",
        "name": "Magadh Oro Dental Clinic",
        "city": "Patna",
        "vertical": "clinic",
        "rating": "4.8",
        "reviews": "344"
    },
    {
        "email": "info@faciodental.com",
        "name": "Facio Dental Super Speciality Clinic",
        "city": "Patna",
        "vertical": "clinic",
        "rating": "4.5",
        "reviews": "417"
    },
    {
        "email": "rajdentalgaya@gmail.com",
        "name": "Raj Dental Clinic",
        "city": "Gaya",
        "vertical": "clinic",
        "rating": "4.8",
        "reviews": "1,265"
    },
    {
        "email": "info@shahidentalclinic.com",
        "name": "Shahi Dental Clinic",
        "city": "Muzaffarpur",
        "vertical": "clinic",
        "rating": "4.9",
        "reviews": "1,343"
    },
    {
        "email": "brightsmiledentalbjp@gmail.com",
        "name": "Bright Smile Dental Hospital",
        "city": "Bhagalpur",
        "vertical": "clinic",
        "rating": "5.0",
        "reviews": "844"
    },
    {
        "email": "vrihiskydeck@gmail.com",
        "name": "Vrihi Skydeck Rooftop Restaurant",
        "city": "Patna",
        "vertical": "restaurant",
        "rating": "4.5",
        "reviews": "1,598"
    },
    {
        "email": "feedback@bansivihar.com",
        "name": "Bansi Vihar Restaurant",
        "city": "Patna",
        "vertical": "restaurant",
        "rating": "4.1",
        "reviews": "9,808"
    },
    {
        "email": "thegreentreepb@gmail.com",
        "name": "PatnaSocial Restro & Rooftop Cafe",
        "city": "Patna",
        "vertical": "restaurant",
        "rating": "3.5",
        "reviews": "99"
    },
    {
        "email": "pramodconfectioneryandfood@gmail.com",
        "name": "Paprika Fine Dine Restaurant",
        "city": "Gaya",
        "vertical": "restaurant",
        "rating": "4.2",
        "reviews": "3,379"
    },
    {
        "email": "hotelgoldenmeet@gmail.com",
        "name": "The Spice Delight Restaurant",
        "city": "Muzaffarpur",
        "vertical": "restaurant",
        "rating": "4.5",
        "reviews": "51"
    },
    {
        "email": "reservations@theroyalbihar.com",
        "name": "The Royal Bihar",
        "city": "Patna",
        "vertical": "hotel",
        "rating": "4.5",
        "reviews": "1,746"
    },
    {
        "email": "info@hotelviraatinn.com",
        "name": "Hotel Viraat Inn",
        "city": "Gaya",
        "vertical": "hotel",
        "rating": "4.1",
        "reviews": "1,102"
    },
    {
        "email": "info@hotelatithi.co.in",
        "name": "Hotel Atithi",
        "city": "Muzaffarpur",
        "vertical": "hotel",
        "rating": "4.0",
        "reviews": "3,145"
    },
    {
        "email": "reservations@hotelmaxinn.in",
        "name": "Hotel Max Inn",
        "city": "Bhagalpur",
        "vertical": "hotel",
        "rating": "3.9",
        "reviews": "978"
    }
]

for p in prospects:
    add_prospect(
        email=p["email"],
        name=p["name"],
        city=p["city"],
        vertical=p["vertical"],
        rating=p["rating"],
        reviews=p["reviews"]
    )

print("\nAll 14 fresh prospects loaded into email_pipeline.json successfully.")