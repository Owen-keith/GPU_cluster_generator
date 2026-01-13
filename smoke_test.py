import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["NVIDIA_API_KEY"],
    base_url="https://integrate.api.nvidia.com/v1",
)

resp = client.chat.completions.create(
    model="deepseek-ai/deepseek-v3.1-terminus",
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
    max_tokens=60,
)

print(resp.choices[0].message.content)