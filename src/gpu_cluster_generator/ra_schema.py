from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Workload = Literal["training", "finetune", "inference"]


class NodeCountRange(BaseModel):
    min: int = Field(..., ge=1)
    max: int = Field(..., ge=1)


class Pattern(BaseModel):
    id: str
    family: str
    description: str

    c: int = Field(..., ge=1, description="CPU sockets per node")
    g: int = Field(..., ge=1, description="GPUs per node")
    n: int = Field(..., ge=1, description="NICs per node")
    b_gbps_per_gpu: int = Field(..., ge=0, description="East-west bandwidth per GPU in Gbps")

    node_count: NodeCountRange
    tags: list[str] = Field(default_factory=list)
    workload_fit: list[Workload] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class RASource(BaseModel):
    name: str
    notes: list[str] = Field(default_factory=list)


class RAPatternsCatalog(BaseModel):
    version: int
    source: RASource
    patterns: list[Pattern]


class NetworkingDefaults(BaseModel):
    version: int
    defaults: dict