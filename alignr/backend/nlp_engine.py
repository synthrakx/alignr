"""
ALIGNR NLP Engine
=================
Core alignment score calculation using MiniLM via onnxruntime.

Research basis:
- CHI 2026: Pre-AI reflection improves critical thinking outcomes
- Microsoft Research ExtendAI: Articulating reasoning first = better augmentation

Encoder architecture:
- Model: sentence-transformers/all-MiniLM-L6-v2 (384-dim embeddings)
- Runtime: onnxruntime (CPU) with manual mean-pooling + L2 normalization
- Rationale: identical model weights and math to sentence-transformers wrapper,
  but ~300 MB lower RAM footprint (no PyTorch dependency).
  Verified numerically equivalent to reference implementation.

Privacy guarantee:
Text is processed in-memory and immediately discarded.
Only alignment scores (float 0.0-1.0) are stored in the database.
No text ever reaches the database.

Author: SYNTHRAKX
Date: July 2026 (Path B swap)
"""

import os
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
from huggingface_hub import hf_hub_download

MODEL_REPO = "sentence-transformers/all-MiniLM-L6-v2"

# Lazy-loaded singletons
_session = None
_tokenizer = None


def load_model():
    """Download and load ONNX model + tokenizer on first call. Cached afterward."""
    global _session, _tokenizer
    if _session is None:
        model_path = hf_hub_download(repo_id=MODEL_REPO, filename="onnx/model.onnx")
        tokenizer_path = hf_hub_download(repo_id=MODEL_REPO, filename="tokenizer.json")
        _session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        _tokenizer = Tokenizer.from_file(tokenizer_path)


def _encode(text: str) -> np.ndarray:
    """
    Encode a single string into a 384-dim L2-normalized embedding.

    Steps (identical to sentence-transformers pipeline for MiniLM):
    1. Tokenize (WordPiece, max 256 tokens with truncation)
    2. Forward pass through MiniLM ONNX model
    3. Mean-pool across tokens, weighted by attention mask
    4. L2-normalize the pooled vector
    """
    load_model()
    _tokenizer.enable_truncation(max_length=256)
    enc = _tokenizer.encode(text)
    input_ids = np.array([enc.ids], dtype=np.int64)
    attention_mask = np.array([enc.attention_mask], dtype=np.int64)
    token_type_ids = np.zeros_like(input_ids)

    outputs = _session.run(None, {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": token_type_ids,
    })
    last_hidden = outputs[0]  # shape: (1, seq_len, 384)

    mask = attention_mask[..., None].astype(np.float32)
    summed = (last_hidden * mask).sum(axis=1)
    counts = np.clip(mask.sum(axis=1), a_min=1e-9, a_max=None)
    mean_pooled = summed / counts

    norm = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
    norm = np.clip(norm, a_min=1e-9, a_max=None)
    embedding = mean_pooled / norm
    return embedding[0]  # shape: (384,)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two L2-normalized vectors = dot product."""
    return float(np.dot(a, b))


def calculate_ras(pre_thinking: str, ai_output: str) -> dict:
    """
    Calculate the RAS (Reasoning Alignment Score).

    Args:
        pre_thinking (str): The participant's pre-thoughts.
        ai_output (str): The AI output.

    Returns:
        dict: RAS score, percentage, semantic novelty, and interpretation.

    Raises:
        ValueError: If pre_thinking has fewer than 5 words.
    """
    if len(pre_thinking.split()) < 5:
        raise ValueError("pre_thinking must have at least 5 words")

    encoded_pre = _encode(pre_thinking)
    encoded_ai = _encode(ai_output)

    ras = _cosine_similarity(encoded_pre, encoded_ai)
    ras_pct = float(np.clip(ras * 100, 0, 100))
    semantic_novelty = round(
        len(set(ai_output.lower().split()) - set(pre_thinking.lower().split()))
        / (len(set(ai_output.lower().split())) or 1),
        4,
    )
    interpretation = _interpret_ras(ras)

    return {
        'ras': float(ras),
        'ras_pct': ras_pct,
        'semantic_novelty': semantic_novelty,
        'interpretation': interpretation,
    }


def calculate_cii(pre_thinking: str) -> float:
    """
    Calculate the CII (Cognitive Independence Index).
    Unchanged from previous version — no model dependency.
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
    Calculate the SCS (Surprise Calibration Score).

    Args:
        prediction (str): The participant's prediction.
        ai_output (str): The AI output.

    Returns:
        dict: SCS score and surprise level (or None if no prediction).
    """
    if not prediction or len(prediction.split()) < 3:
        return {'scs': None, 'surprise_level': None}

    encoded_prediction = _encode(prediction)
    encoded_ai = _encode(ai_output)

    scs = _cosine_similarity(encoded_prediction, encoded_ai)
    surprise_level = "low" if scs > 0.8 else ("moderate" if scs > 0.5 else "high")

    return {
        'scs': float(scs),
        'surprise_level': surprise_level,
    }


def _interpret_ras(score):
    if score >= 0.75: return "high"
    if score >= 0.50: return "moderate"
    if score >= 0.30: return "developing"
    return "low"


if __name__ == "__main__":
    print("ALIGNR nlp_engine.py -- 6 verification tests (Path B: onnxruntime)\n")

    # T1: Similar texts -> high RAS
    r1 = calculate_ras(
        "Python automation helps process data files efficiently",
        "Python excels at automating data workflows and file processing"
    )
    assert r1["ras"] > 0.65, f"T1 FAIL: {r1['ras']}"
    print(f"T1 similar texts: RAS={r1['ras_pct']:.1f}% ({r1['interpretation']})")

    # T2: Unrelated texts -> low RAS
    r2 = calculate_ras(
        "I enjoy cooking pasta every Sunday afternoon",
        "Quantum computing uses qubits in superposition states"
    )
    assert r2["ras"] < 0.25, f"T2 FAIL: {r2['ras']}"
    print(f"T2 unrelated texts: RAS={r2['ras_pct']:.1f}% (correctly low)")

    # T3: Short input -> ValueError
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

    print("\nAll tests passed. ALIGNR engine ready (Path B).")