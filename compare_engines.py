from backend.nlp_engine import calculate_ras as new_ras

def old_ras(t1, t2):
    w1, w2 = set(t1.lower().split()), set(t2.lower().split())
    return len(w1 & w2) / len(w1 | w2) if w1 | w2 else 0.0

test_pairs = [
    ("Python helps with data tasks", "Python excels at data science"),
    ("I think AI will help me reason better", "Machine learning reduces cognitive burden"),
    ("The system processes information quickly", "The algorithm analyzes input data fast"),
    ("AI assists with everyday workflows", "Artificial intelligence supports daily operations"),
    ("Pre-thinking improves alignment scores", "Reflection before AI use enhances calibration"),
]

print(f"{'Old (word overlap)':>20} | {'New (semantic)':>15} | {'Diff':>6}")
print("-" * 70)
for p, a in test_pairs:
    old = old_ras(p, a)
    new = new_ras(p, a)["ras"]
    print(f"{old:>20.3f} | {new:>15.3f} | {new-old:>+6.3f}")
    print(f"  pre: {p}")
    print(f"  ai:  {a}\n")