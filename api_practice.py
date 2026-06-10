# api_practice.py — 3 exception types, 3 different messages
# This exact pattern is used in ALIGNR's FastAPI backend (Day 12)
# and in every external API call throughout the plan.

import requests

def get_patna_weather() -> dict:
    """
    Fetches current weather for Patna.
    3 exception types — each with a specific, different message.
    This is the error handling pattern used everywhere in ALIGNR.
    """
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 25.5941,
                "longitude": 85.1376,
                "current_weather": True
            },
            timeout=10
        )
        r.raise_for_status()
        return r.json()

    except requests.exceptions.Timeout:
        # Different message: tells user what happened AND what to do
        return {"error": "Request timed out after 10 seconds. Check your connection."}

    except requests.exceptions.HTTPError as e:
        # Different message: includes the status code
        return {"error": f"Server returned HTTP {e.response.status_code}. Try again later."}

    except requests.exceptions.ConnectionError:
        # Different message: no internet vs server error
        return {"error": "No internet connection. ALIGNR runs locally — this API is optional."}

result = get_patna_weather()
print(result)

# Manual test: to see each exception
# Timeout:    change timeout=10 to timeout=0.001
# HTTPError:  change URL to api.open-meteo.com/v1/BADROUTE
# Connection: disconnect Wi-Fi