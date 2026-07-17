"""
ALIGNR NLP Engine
=================
Core alignment score calculation using sentence-transformers.

Research basis:
- CHI 2026: Pre-AI reflection improves critical thinking outcomes
- Microsoft Research ExtendAI: Articulating reasoning first = better augmentation

Privacy guarantee:
Text is processed in-memory and immediately discarded.
Only alignment scores (float 0.0-1.0) are stored in the database.
No text ever reaches the database.

Author: SYNTHRAKX
Date: May 2026
"""

import numpy as np
from sentence_transformers import SentenceTransformer, util

# Singleton model loader for sentence-transformers all-MiniLM-L6-v2 (loaded once globally)
# ONNX backend used for memory efficiency on Render free tier (512 MB RAM ceiling).
# Same model, same weights, same output — different execution engine.
model = None

def load_model():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2', backend="onnx")

load_model()

def calculate_ras(pre_thinking: str, ai_output: str) -> dict:
    """
    Calculate the RAS (Reflection-Articulation-Similarity) score.
    
    Args:
        pre_thinking (str): The participant's pre-thoughts.
        ai_output (str): The AI output.
    
    Returns:
        dict: A dictionary containing the RAS score, percentage, semantic novelty, and interpretation.
    
    Raises:
        ValueError: If pre_thinking has fewer than 5 words.
    """
    if len(pre_thinking.split()) < 5:
        raise ValueError("pre_thinking must have at least 5 words")
    
    load_model()
    encoded_pre = model.encode([pre_thinking])
    encoded_ai = model.encode([ai_output])
    
    ras = util.cos_sim(encoded_pre, encoded_ai)[0][0]
    ras_pct = np.clip(ras * 100, 0, 100)
    semantic_novelty = round(len(set(ai_output.lower().split()) - set(pre_thinking.lower().split())) / (len(set(ai_output.lower().split())) or 1), 4)
    interpretation = _interpret_ras(ras)
    
    return {
        'ras': float(ras),
        'ras_pct': float(ras_pct),
        'semantic_novelty': semantic_novelty,
        'interpretation': interpretation
    }

def calculate_cii(pre_thinking: str) -> float:
    """
    Calculate the CII (Critical Thinking Improvement Index).
    
    Args:
        pre_thinking (str): The participant's pre-thoughts.
    
    Returns:
        float: The CII score.
    """
    words = pre_thinking.split()
    if len(words) < 3:
        return 0.5
    
    ttk = len(set(w.lower() for w in words)) / len(words)
    avg_len = np.mean([len(word) for word in words])
    
    cii = (ttk * 0.6) + (min(avg_len / 20, 1.0) * 0.4)
    return float(cii)

def calculate_scs(prediction: str, ai_output: str) -> dict:
    """
    Calculate the SCS (Semantic Consistency Score).
    
    Args:
        prediction (str): The participant's prediction.
        ai_output (str): The AI output.
    
    Returns:
        dict: A dictionary containing the SCS score and surprise level.
    """
    if not prediction or len(prediction.split()) < 3:
        return {'scs': None, 'surprise_level': None}
    
    load_model()
    encoded_prediction = model.encode([prediction])
    encoded_ai = model.encode([ai_output])
    
    scs = util.cos_sim(encoded_prediction, encoded_ai)[0][0]
    surprise_level = "low" if scs > 0.8 else ("moderate" if scs > 0.5 else "high")
    
    return {
        'scs': float(scs),
        'surprise_level': surprise_level
    }

def _interpret_ras(score):
    if score >= 0.75: return "high"
    if score >= 0.50: return "moderate"
    if score >= 0.30: return "developing"
    return "low"

if __name__ == "__main__":
    print("ALIGNR nlp_engine.py — 6 verification tests\n")

    # T1: Similar texts  high RAS
    r1 = calculate_ras(
        "Python automation helps process data files efficiently",
        "Python excels at automating data workflows and file processing"
    )
    assert r1["ras"] > 0.65, f"T1 FAIL: {r1['ras']}"
    print(f"T1 similar texts: RAS={r1['ras_pct']:.1f}% ({r1['interpretation']})")

    # T2: Unrelated texts  low RAS
    r2 = calculate_ras(
        "I enjoy cooking pasta every Sunday afternoon",
        "Quantum computing uses qubits in superposition states"
    )
    assert r2["ras"] < 0.25, f"T2 FAIL: {r2['ras']}"
    print(f"T2 unrelated texts: RAS={r2['ras_pct']:.1f}% (correctly low)")

    # T3: Short input  ValueError
    try:
        calculate_ras("hi there", "hello how are you today")
        assert False, "T3 FAIL: no exception"
    except ValueError:
        print("T3 short input: ValueError raised correctly")

    # T4: CII full formula returns float in valid range
    cii = calculate_cii("machine learning algorithms identify statistical regularities")
    assert 0 < cii < 1, f"T4 FAIL: {cii}"
    print(f"T4 CII full formula: {cii:.4f}")

    # T5: SCS None when no prediction
    r5 = calculate_scs("", "some AI output for testing")
    assert r5["scs"] is None, f"T5 FAIL: {r5}"
    print("T5 SCS no prediction: returns None correctly")

    # T6: End-to-end session
    print("\n=== Full session ===")
    ras_result = calculate_ras(
        "pre-AI reflection improves reasoning quality by forcing articulation",
        "structured pre-task reflection enhances cognitive engagement with AI outputs"
    )
    cii_result = calculate_cii("pre-AI reflection improves reasoning quality by forcing articulation")
    scs_result = calculate_scs(
        "AI will mention reflection and cognitive quality",
        "structured pre-task reflection enhances cognitive engagement with AI outputs"
    )
    print(f"RAS: {ras_result['ras_pct']:.1f}% | CII: {cii_result:.4f} | SCS: {scs_result['scs']:.4f}")

    print("\nAll tests passed. ALIGNR engine ready.")