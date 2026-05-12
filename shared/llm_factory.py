"""LLM provider factory for the regulated AI pipelines.

Default provider: Groq llama-3.3-70b-versatile (matches the report).
Alternative:      AWS Bedrock meta.llama3-3-70b-instruct-v1:0 (same model, different host).

Switch via environment variable:
    export LLM_PROVIDER=bedrock   # routes ChatGroq and OpenAI direct calls through Bedrock
    # (default if unset)          # routes through Groq

Designed so the Attestix integration code reads identically regardless of
provider, and so the viva committee question "what if Groq is down?" has a
demonstrable one-env-var answer.

Implementation surface:
    get_langchain_llm(temperature=0)   -> a LangChain Chat model
    get_openai_client()                -> a `.chat.completions.create(...)` compatible client
    configure_crewai_env()             -> sets the env vars CrewAI/LiteLLM picks up
"""
from __future__ import annotations

import os
from typing import Any

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_BEDROCK_MODEL = "us.meta.llama3-3-70b-instruct-v1:0"  # cross-region inference profile
DEFAULT_REGION = "us-east-1"


def _provider() -> str:
    return os.environ.get("LLM_PROVIDER", "groq").lower()


def get_langchain_llm(temperature: float = 0, model: str | None = None):
    """Return a LangChain Chat model for the configured provider.

    Both providers expose .invoke / pipe / streaming, so the regulated agent
    code that does `chain = prompt | llm | parser` works unchanged.
    """
    p = _provider()
    if p == "bedrock":
        from langchain_aws import ChatBedrock
        return ChatBedrock(
            model_id=model or DEFAULT_BEDROCK_MODEL,
            region_name=os.environ.get("AWS_REGION", DEFAULT_REGION),
            model_kwargs={"temperature": temperature},
        )
    # default: groq
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=model or DEFAULT_GROQ_MODEL,
        temperature=temperature,
        api_key=os.environ.get("GROQ_API_KEY"),
    )


def get_openai_client() -> Any:
    """Return an object with .chat.completions.create(model, messages, ...) interface.

    For Groq: a real openai.OpenAI client pointed at Groq's OpenAI-compat endpoint.
    For Bedrock: a thin shim that translates to ChatBedrock.invoke and shapes the
    response object like an OpenAI ChatCompletion so call sites do not need to change.
    """
    p = _provider()
    if p == "bedrock":
        return _BedrockOpenAIShim(
            model=os.environ.get("BEDROCK_MODEL", DEFAULT_BEDROCK_MODEL),
            region=os.environ.get("AWS_REGION", DEFAULT_REGION),
        )
    from openai import OpenAI
    return OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ.get("GROQ_API_KEY"),
    )


def configure_crewai_env() -> None:
    """Set environment variables so CrewAI/LiteLLM picks up the right backend.

    CrewAI uses LiteLLM under the hood. For Groq we tunnel through the
    OpenAI-compat endpoint. For Bedrock we set the AWS region; CrewAI Agents
    must then receive a 'bedrock/...' model string. Caller is expected to use
    the model string returned by `crewai_model_string()` when constructing
    Agent(llm=...) in regulated pipelines that fully switch providers.
    """
    p = _provider()
    if p == "bedrock":
        os.environ.setdefault("AWS_REGION", DEFAULT_REGION)
        os.environ.setdefault("AWS_REGION_NAME", os.environ.get("AWS_REGION", DEFAULT_REGION))
        # CrewAI's OpenAI provider asserts OPENAI_API_KEY is present even when not used.
        # Setting a dummy key + the bedrock model string lets LiteLLM route to Bedrock.
        os.environ.setdefault("OPENAI_API_KEY", "bedrock-routed-via-litellm")
        os.environ["LITELLM_MODEL"] = f"bedrock/{os.environ.get('BEDROCK_MODEL', DEFAULT_BEDROCK_MODEL)}"
        os.environ["OPENAI_MODEL_NAME"] = f"bedrock/{os.environ.get('BEDROCK_MODEL', DEFAULT_BEDROCK_MODEL)}"
        return
    # default: groq via openai-compat
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = DEFAULT_GROQ_MODEL
    os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY", "dummy")


def crewai_model_string() -> str:
    """LiteLLM model-id string suitable for `Agent(llm=...)` in CrewAI."""
    p = _provider()
    if p == "bedrock":
        return f"bedrock/{os.environ.get('BEDROCK_MODEL', DEFAULT_BEDROCK_MODEL)}"
    return f"groq/{DEFAULT_GROQ_MODEL}"


class _BedrockOpenAIShim:
    """OpenAI-style facade over ChatBedrock.invoke for the_judge/the_cio/CMO/CCO agents."""

    def __init__(self, model: str, region: str) -> None:
        from langchain_aws import ChatBedrock
        self._model = model
        self._region = region
        self._chat = ChatBedrock(model_id=model, region_name=region, model_kwargs={"temperature": 0})
        self.chat = self  # so callers can do client.chat.completions.create(...)

    @property
    def completions(self):
        return self

    def create(self, *, model: str | None = None, messages: list[dict], temperature: float = 0, **_ignored):
        # Re-create the underlying chat model only if a temperature override was requested
        chat = self._chat
        if temperature != 0:
            from langchain_aws import ChatBedrock
            chat = ChatBedrock(
                model_id=self._model, region_name=self._region,
                model_kwargs={"temperature": temperature},
            )
        # ChatBedrock accepts LangChain message dicts directly
        resp = chat.invoke(messages)
        # shape into an OpenAI ChatCompletion-like object
        return _OpenAILikeResponse(content=resp.content if hasattr(resp, "content") else str(resp))


class _OpenAILikeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [_OpenAILikeChoice(content)]


class _OpenAILikeChoice:
    def __init__(self, content: str) -> None:
        self.message = _OpenAILikeMessage(content)


class _OpenAILikeMessage:
    def __init__(self, content: str) -> None:
        self.content = content
