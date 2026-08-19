"""Corporate OpenAI-compatible proxy configuration for JSONC CrewAI projects."""

import os

import truststore
from crewai.llm import LLM

truststore.inject_into_ssl()

llm = LLM(
    model=os.environ["MODEL"],
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
    provider=os.environ["PROVIDER"],
)
