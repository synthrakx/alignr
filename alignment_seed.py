# alignment_seed.py — primitive RAS, the seed of everything ALIGNR becomes
# Day 15: sentence-transformers replaces word_overlap. Same principle survives.


def word_overlap_ras(text1: str, text2: str) -> float:
    """Primitive RAS using word overlap (Jaccard similarity).
    Privacy: text1, text2 are method-local. Only the float is returned."""
    if not text1 or not text2:
        return 0.0
    w1, w2 = set(text1.lower().split()), set(text2.lower().split())
    return len(w1 & w2) / len(w1 | w2) if w1 | w2 else 0.0


def interpret_ras(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.50:
        return "moderate"
    if score >= 0.30:
        return "developing"
    return "low"


# Run the ALIGNR core loop right now
pre = input("Your pre-thinking (5+ words): ")
ai_out = input("AI response (5+ words): ")
score = word_overlap_ras(pre, ai_out)
print(f"\nPrimitive RAS: {score:.3f} ({score:.1%}) — {interpret_ras(score)}")
print("Day 15: this becomes sentence-transformers. This principle stays.")
