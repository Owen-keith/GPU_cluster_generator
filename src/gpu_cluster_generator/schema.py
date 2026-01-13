from pydantic import BaseModel, Field


class GPUSpec(BaseModel):
    gpu: str = Field(..., description="GPU model name provided by the user")
    memory_gb: int = Field(..., ge=0, description="Onboard GPU memory in GiB")
    notes: list[str] = Field(default_factory=list, description="Any caveats/assumptions")