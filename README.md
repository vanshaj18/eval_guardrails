# LLM Guardrails & Profiling Toolkit

A lightweight, extensible toolkit for adding safety checks, output validation, and cost profiling to your LLM-based applications.

## Features

- **🛡️ Input Guarding**: Detect prompt injections and PII (Personally Identifiable Information) before they reach your LLM.
- **✅ Output Validation**: Ensure LLM responses follow specific structures using [Pydantic](https://docs.pydantic.dev/) models.
- **🔄 Failure Recovery**: Configure automatic retries, fallback values, or custom exception handling when checks fail.
- **📊 Token & Cost Profiling**: Estimate token utilization and API costs across different model providers.
- **🔍 Prompt Linting**: Validate prompt templates for structural errors (e.g., broken placeholders) and best practices.
- **🔌 Extensible Architecture**: Easily adapt the toolkit to work with any Python function or third-party LLM client.

## Installation

```bash
pip install -r requirements.txt
```

*(Ensure you have `pydantic` installed)*

## Quick Start

### Basic Usage with `@guardrail`

```python
from pydantic import BaseModel, Field
from guardrails import guardrail, check_injection, check_pii, OnFailAction

# 1. Define your output schema
class TranslationResponse(BaseModel):
    translated_text: str = Field(..., min_length=1)
    detected_language: str

# 2. Wrap your function
@guardrail(
    input_checks=[check_injection, check_pii],
    output_schema=TranslationResponse,
    on_fail=OnFailAction.RETRY,
    max_retries=2
)
async def translate_text(text: str, target_lang: str):
    # Your LLM call logic here
    return {
        "translated_text": "Bonjour tout le monde",
        "detected_language": "English"
    }

# 3. Use it!
import asyncio
result = asyncio.run(translate_text("Hello world", "French"))
print(result)
```

## Core Components

### 1. The `@guardrail` Decorator
The primary entry point. It handles:
- **`input_checks`**: A list of async functions that return a `GuardrailResult`.
- **`output_schema`**: A Pydantic model for validating the function's return value.
- **`on_fail`**: Action on failure: `RETRY`, `FALLBACK`, or `EXCEPTION`.
- **`enable_profiling`**: Set to `True` to enable token and cost tracking.

### 2. Token Profiling
Enable profiling to track costs automatically. The toolkit uses a heuristic approach for token counting and a local database (`tokenDetails.json`) for pricing.

```python
@guardrail(
    enable_profiling=True,
    model_name="gpt-4o"
)
async def my_llm_call(prompt: str):
    ...
```

### 3. Prompt Linting
Validate your prompts for quality and efficiency.

```python
from guardrails import FullPromptLinterConfig, PromptConfig

linter_cfg = FullPromptLinterConfig(
    prompt_config=PromptConfig(
        expected_variables=["name"],
        enforce_xml_tags=True,
        require_fallback_phrase=True
    )
)

@guardrail(prompt_linter_config=linter_cfg)
async def structured_prompt(name: str):
    return f"Hello <user>{name}</user>. If you don't know, say 'I don't know'."
```

## Directory Structure

- `decorator.py`: Main `@guardrail` implementation.
- `checks.py`: Built-in safety checks (PII, Injection).
- `profiler.py`: Token usage and cost estimation logic.
- `prompt_linter.py`: Structural and best-practice linting for prompts.
- `adapters/`: Logic to hook into different function types (sync/async).
- `data_models.py`: Pydantic models for configuration and results.

## Contributing

License: Apache-2.0
Copyright (c) 2026.
