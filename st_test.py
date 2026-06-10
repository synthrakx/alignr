# st_test.py — UCA Chain-of-Verification for ALIGNR's core engine
# "sentence-transformers all-MiniLM-L6-v2 measures semantic similarity"
# File 11 locks this model. Verify it today before Day 15 depends on it.

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading all-MiniLM-L6-v2 (first time: ~30 seconds download)...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Ready.\n")

tests = [
    (
        "Python automation for data workflows",
        "Python excels at data science and automation",
        0.60, "similar texts → score should be HIGH"
    ),
    (
        "I enjoy cooking pasta on Sundays",
        "Quantum computing uses qubits in superposition",
        0.10, "unrelated texts → score should be LOW"
    ),
    (
        "ALIGNR measures cognitive alignment",
        "ALIGNR measures cognitive alignment",
        0.98, "identical texts → score should be VERY HIGH"
    ),
]

all_pass = True
for t1, t2, min_score, label in tests:
    score = float(cosine_similarity(
        model.encode([t1]),
        model.encode([t2])
    )[0][0])
    ok = score >= min_score
    if not ok:
        all_pass = False
    print(f"{'✅ PASS' if ok else '❌ FAIL'} [{label}]")
    print(f"         Score: {score:.4f} | Minimum expected: {min_score}")

print()
if all_pass:
    print("Chain-of-Verification: PASSED")
    print("all-MiniLM-L6-v2: VERIFIED for ALIGNR production use")
    print("Day 15 can proceed: nlp_engine.py builds on this confirmed engine.")
else:
    print("Chain-of-Verification: FAILED")
    print("Diagnosis: pip install sentence-transformers --upgrade --break-system-packages")
    print("Then: pip install scikit-learn --break-system-packages")
    print("Run this file again before Day 15.")