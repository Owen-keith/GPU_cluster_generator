# GPU Cluster Generator (Prototype)

A small prototype CLI that uses **NVIDIA Build / cloud-hosted NVIDIA NIM endpoints** to help generate early “solutions architect” style outputs for AI infrastructure design.

This repo currently focuses on two foundational capabilities:

1. **GPU spec lookup** (starting with GPU memory as a minimal example).
2. **Reference Architecture (RA) pattern selection** using a small catalog of NVIDIA Enterprise RA patterns.

The longer-term goal is to evolve this into a **cluster design generator** that can take customer constraints (training vs inference, model size, throughput targets, budget, deployment constraints) and produce a defensible **reference design**: compute node selection, node counts, network fabric, and eventually a draft BOM.

---

## Why this exists

- **Learning project:** explore how to integrate NVIDIA’s developer environment and NIM APIs into a real tool.
- **Interview demo:** build something concrete that demonstrates systems thinking, use of NVIDIA reference architectures, and practical developer execution.

---

## NVIDIA products / technology used

### NVIDIA Build + Cloud-hosted NIM endpoints
- This project calls **cloud-hosted NVIDIA NIM endpoints** (serverless) using an **NVIDIA API key**.
- The endpoints are **OpenAI API compatible**, so the code uses the OpenAI Python SDK pointed at NVIDIA’s base URL.

### Model used
- Default reasoning model used for API calls:
  - `deepseek-ai/deepseek-v3.1-terminus`

> Note: For reliability, the project prefers deterministic “facts” from local catalogs whenever possible. The model is used as a fallback for unknown inputs (prototype mode).

### NVIDIA Enterprise Reference Architecture (RA) concepts
- The RA pattern catalog is based on NVIDIA Enterprise RA conventions (e.g., the C-G-N-B style node descriptors and node-count scaling ranges).
- Current patterns included are intentionally minimal and meant to be expanded over time.

### NVIDIA Networking defaults (from RA guidance)
The catalog currently encodes a default “Spectrum-X” approach:
- **Spectrum-X Ethernet**
- **Spectrum-4 switches**
- **BlueField-3 SuperNIC / DPU** (north-south guidance)

These defaults are not yet used to generate a full topology/BOM, but they inform the `ra recommend` output fields (`fabric`, `platform`).

---

## Current functionality (strict JSON CLI)

All commands print **strict JSON only** to stdout (including errors). This is deliberate so the CLI can be chained into other tools.

### 1) GPU spec lookup (prototype)
Looks up a GPU model name and returns basic specs (currently: `memory_gb`).

- First checks a small deterministic lookup table.
- If unknown, it can fall back to the NIM-hosted model and asks it for strict JSON.

Example:

```bash
uv run python -m gpu_cluster_generator gpu spec --gpu "NVIDIA H100"

Example output:

{
  "gpu": "NVIDIA H100",
  "memory_gb": 80,
  "notes": ["from local lookup table"]
}

2) List RA patterns

Lists available patterns from catalog/ra_patterns.yaml:

uv run python -m gpu_cluster_generator ra list

3) Recommend an RA pattern (deterministic)

Given total GPU count + workload type, selects a pattern and computes nodes:

uv run python -m gpu_cluster_generator ra recommend --gpus 128 --workload training

Example output:

{
  "input": { "gpus": 128, "workload": "training" },
  "recommendation": {
    "pattern_id": "2-8-9-400",
    "nodes": 16,
    "gpus_per_node": 8,
    "b_gbps_per_gpu": 400,
    "fabric": "ethernet",
    "platform": "spectrum-x"
  },
  "notes": ["Selected pattern supports computed node count within its declared node range."]
}


⸻

Repo structure

catalog/
  ra_patterns.yaml              # small Enterprise RA pattern catalog (C-G-N-B + node ranges)
  networking_defaults.yaml      # fabric/platform defaults (Spectrum-X, etc.)

src/gpu_cluster_generator/
  __main__.py                   # CLI entrypoint (argparse subcommands)
  nim_client.py                 # NVIDIA NIM endpoint client (OpenAI-compatible)
  spec_lookup.py                # GPU spec lookup (local table + optional LLM fallback)
  schema.py                     # Pydantic model for GPU spec JSON
  ra_schema.py                  # Pydantic models to validate RA YAML
  catalog_loader.py             # loads YAML catalogs from /catalog
  ra_engine.py                  # deterministic RA recommender logic


⸻

Setup

Prerequisites
	•	macOS / Linux
	•	Python >= 3.11
	•	uv installed (recommended)

Install dependencies

From repo root:

uv sync

Set your NVIDIA API key

Create a local .env file (do not commit this):

cat > .env << 'EOF'
NVIDIA_API_KEY=your_key_here
EOF

This repo expects NVIDIA_API_KEY in the environment or .env.

(Optional) If you use direnv, you can auto-activate your environment when entering the repo.

⸻

Usage

GPU spec

uv run python -m gpu_cluster_generator gpu spec --gpu "NVIDIA H100"

Try an unknown GPU (will use the model fallback):

uv run python -m gpu_cluster_generator gpu spec --gpu "NVIDIA H200"

List RA patterns

uv run python -m gpu_cluster_generator ra list

Recommend an RA pattern

uv run python -m gpu_cluster_generator ra recommend --gpus 128 --workload training
uv run python -m gpu_cluster_generator ra recommend --gpus 64 --workload inference


⸻

Data model / catalogs

RA patterns (catalog/ra_patterns.yaml)

This file is the current “source of truth” for:
	•	node descriptor fields: c, g, n, b_gbps_per_gpu
	•	scaling ranges: node_count.min to node_count.max
	•	tags + workload fit metadata

Add new patterns here as you incorporate more NVIDIA reference architectures.

Networking defaults (catalog/networking_defaults.yaml)

Currently provides simple defaults used by ra recommend output:
	•	fabric: e.g., "ethernet"
	•	platform: e.g., "spectrum-x"

⸻

Design philosophy (important for correctness)

This repo is intentionally structured to separate:
	1.	Facts / catalogs (deterministic, auditable)

	•	YAML catalogs and local lookup tables

	2.	Reasoning / synthesis (LLM-assisted, bounded)

	•	model calls are used as a fallback or for future synthesis steps
	•	outputs remain machine-validated (Pydantic)

This is the intended direction for scaling into a “cluster design generator” without relying on the model to hallucinate specs.

⸻

Roadmap (near-term)
	•	Expand GPU and system catalogs (HGX/DGX/GBxxx families)
	•	Add “design v0” command:
	•	input: workload type + GPU count + deployment constraints
	•	output: node type suggestion + network fabric suggestion + RA alignment notes
	•	Add validators (“reject designs that violate RA ranges”)
	•	Add grounding to official spec sheets / PDFs for more facts (reduce model fallback)

⸻

Security / operational notes
	•	Never commit your .env (API keys).
	•	Model fallback is for prototype convenience; for production-quality accuracy, prefer facts derived from official spec sheets / reference architecture documents encoded into catalogs.

