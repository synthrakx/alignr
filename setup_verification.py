# setup_verification.py — Final SYNTHRAKX setup check
print("=" * 50)
print("SYNTHRAKX SETUP VERIFICATION")
print("=" * 50)
print()

tests = []

# 1. Ollama running + qwen3:8b available
import subprocess

try:
    result = subprocess.run(
        ["ollama", "list"], capture_output=True, text=True, timeout=10
    )
    tests.append(("Ollama + qwen3:8b", "qwen3:8b" in result.stdout))
except Exception as e:
    tests.append(("Ollama + qwen3:8b", False))

# 2. ALIGNR engine (sentence-transformers)
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    m = SentenceTransformer("all-MiniLM-L6-v2")
    s = float(
        cosine_similarity(
            m.encode(["Python data analysis"]), m.encode(["Python data science"])
        )[0][0]
    )
    tests.append(("ALIGNR engine (CAS > 0.6)", s > 0.6))
except Exception as e:
    tests.append(("ALIGNR engine", False))

# 3. New frameworks
frameworks = [
    ("pydantic_ai", "pydantic_ai"),
    ("agno", "agno"),
    ("google.adk", "google.adk"),
    ("pipecat", "pipecat"),
    ("markitdown", "markitdown"),
    ("browser_use", "browser_use"),
    ("litellm", "litellm"),
]
for name, module in frameworks:
    try:
        __import__(module)
        tests.append((f"{name}", True))
    except ImportError:
        tests.append((f"{name}", False))

# 4. Aider
try:
    result = subprocess.run(
        ["aider", "--version"], capture_output=True, text=True, timeout=10
    )
    tests.append(("Aider", "aider" in result.stdout.lower()))
except Exception:
    tests.append(("Aider", False))

# 5. faster-whisper
try:
    import faster_whisper

    tests.append(("faster-whisper", True))
except ImportError:
    tests.append(("faster-whisper", False))

# Print results
print(f"{'Component':<35} {'Status'}")
print("-" * 50)
passed = 0
for name, ok in tests:
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    print(f"{name:<35} {status}")

print()
print(f"RESULT: {passed}/{len(tests)} components ready")
print()
if passed == len(tests):
    print("SETUP COMPLETE. Day 1 ready.")
else:
    print(f"Fix the FAIL items. {len(tests) - passed} remaining.")
