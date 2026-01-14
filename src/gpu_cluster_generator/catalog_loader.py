from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .ra_schema import NetworkingDefaults, RAPatternsCatalog


def _repo_root() -> Path:
    # This file lives at src/gpu_cluster_generator/catalog_loader.py
    # Repo root is 3 parents up: gpu_cluster_generator -> src -> repo_root
    return Path(__file__).resolve().parents[2]


def load_yaml(relative_path: str) -> dict[str, Any]:
    path = _repo_root() / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Catalog file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping at top level in {relative_path}")
    return data


def load_ra_patterns() -> RAPatternsCatalog:
    raw = load_yaml("catalog/ra_patterns.yaml")
    return RAPatternsCatalog.model_validate(raw)


def load_networking_defaults() -> NetworkingDefaults:
    raw = load_yaml("catalog/networking_defaults.yaml")
    return NetworkingDefaults.model_validate(raw)