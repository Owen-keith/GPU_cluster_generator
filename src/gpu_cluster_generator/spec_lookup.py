import json
from typing import Any

from .nim_client import DEFAULT_MODEL, get_client
from .schema import GPUSpec

# Minimal deterministic table to start (expand later).
# Values are "typical" common configs (H100 SXM is often 80GB; PCIe variants exist).
GPU_MEMORY_GB = {
    "nvidia h100": 80,
    "h100": 80,
    "nvidia a100": 80,
    "a100": 80,
    "nvidia l40s": 48,
    "l40s": 48,
    "nvidia rtx 4090": 24,
    "rtx 4090": 24,
}


def normalize(name: str) -> str:
    return " ".join(name.strip().lower().split())


def lookup_or_model(gpu_name: str) -> GPUSpec:
    key = normalize(gpu_name)
    if key in GPU_MEMORY_GB:
        return GPUSpec(gpu=gpu_name, memory_gb=GPU_MEMORY_GB[key], notes=["from local lookup table"])

    # Fallback: ask the model for memory only, strict JSON.
    client = get_client()
    schema_hint = {
        "gpu": gpu_name,
        "memory_gb": 0,
        "notes": ["string"]
    }

    prompt = f"""
Return ONLY valid JSON matching this exact shape (no markdown, no extra keys):
{json.dumps(schema_hint)}

Task: For the GPU model name "{gpu_name}", fill in memory_gb (GiB) and set notes with any assumptions
(e.g. multiple variants). If you are unsure, set memory_gb to 0 and explain uncertainty in notes.
"""

    resp = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You output strict JSON only."},
            {"role": "user", "content": prompt.strip()},
        ],
        temperature=0.0,
        max_tokens=200,
    )

    text = resp.choices[0].message.content.strip()

    # Parse + validate strictly
    data: Any = json.loads(text)
    return GPUSpec.model_validate(data)