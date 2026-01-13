import os
from dotenv import load_dotenv
from openai import OpenAI

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "deepseek-ai/deepseek-v3.1-terminus"


def get_client() -> OpenAI:
    load_dotenv()
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise RuntimeError(
            "NVIDIA_API_KEY not found. Set it in your environment or in a local .env file."
        )

    return OpenAI(api_key=api_key, base_url=NVIDIA_BASE_URL)