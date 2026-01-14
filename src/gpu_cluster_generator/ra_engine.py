from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from .ra_schema import Pattern

Workload = Literal["training", "finetune", "inference"]


@dataclass(frozen=True)
class RARecommendation:
    pattern_id: str
    nodes: int
    gpus_per_node: int
    b_gbps_per_gpu: int
    fabric: str
    platform: str
    notes: list[str]


def recommend_pattern(
    patterns: list[Pattern],
    *,
    total_gpus: int,
    workload: Workload,
    fabric: str = "ethernet",
    platform: str = "spectrum-x",
) -> RARecommendation:
    if total_gpus <= 0:
        raise ValueError("total_gpus must be >= 1")

    candidates: list[tuple[Pattern, int]] = []
    for p in patterns:
        if p.workload_fit and workload not in p.workload_fit:
            continue
        nodes = math.ceil(total_gpus / p.g)
        if p.node_count.min <= nodes <= p.node_count.max:
            candidates.append((p, nodes))

    if not candidates:
        # Keep this as JSON error in caller, but we raise here with a clear message.
        raise ValueError(
            "No Enterprise RA pattern fits the requested GPU count within its node range. "
            "Consider the NCP Reference Architecture track for larger scales."
        )

    # Scoring: prioritize bandwidth for training/finetune; otherwise simpler (fewer nodes).
    def score(item: tuple[Pattern, int]) -> tuple[int, int, int]:
        p, nodes = item
        bw = p.b_gbps_per_gpu
        # Higher is better for training/finetune; for inference still helps but less critical.
        bw_weight = 2 if workload in ("training", "finetune") else 1
        # tuple sorted ascending, so negate where higher is better
        return (-bw * bw_weight, nodes, -p.g)

    best_pattern, best_nodes = sorted(candidates, key=score)[0]

    notes = [
        "Selected pattern supports computed node count within its declared node range.",
    ]
    if best_nodes * best_pattern.g != total_gpus:
        notes.append(
            f"Rounding up nodes: {best_nodes} nodes * {best_pattern.g} GPUs/node = {best_nodes * best_pattern.g} GPUs capacity."
        )

    return RARecommendation(
        pattern_id=best_pattern.id,
        nodes=best_nodes,
        gpus_per_node=best_pattern.g,
        b_gbps_per_gpu=best_pattern.b_gbps_per_gpu,
        fabric=fabric,
        platform=platform,
        notes=notes,
    )