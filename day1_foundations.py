# day1_foundations.py
# You know the basics from the learning path. Build fast.

project = "ALIGNR"
day = 8
ras_target = 0.75
print(f"Project: {project} | Day: {day} | Target RAS: {ras_target:.1%}")

# String operations
text = "  cognitive independence research  "
print(text.strip().lower(), len(text.strip().split()))

# F-strings with formatting
ras, cii, scs = 0.6734, 0.4521, 0.3891
print(f"RAS: {ras:.3f} ({ras:.1%}) | CII: {cii:.3f} | SCS: {scs:.3f}")

# Conditional — maps to interpret_ras used everywhere in ALIGNR
def interpret(score: float) -> str:
    if score >= 0.75: return "high"
    if score >= 0.50: return "moderate"
    if score >= 0.30: return "developing"
    return "low"

print(interpret(ras))