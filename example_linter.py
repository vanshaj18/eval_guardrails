# SPDX-FileCopyrightText: Copyright (c) 2025-2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
from guardrails import guardrail, OnFailAction, FullPromptLinterConfig

# Setup logging
logging.basicConfig(level=logging.INFO)

linter_config = {
  "pipeline_config": {
    "model_provider": "OpenAI",
    "model_name": "gpt-4"
  },
  "prompt_config": {
    "template_id": "customer_support_v1",
    "expected_variables": ["context", "query", "history"],
    "enforce_xml_tags": True,
    "require_fallback_phrase": True
  }
}

# Convert dict to pydantic model
config = FullPromptLinterConfig(**linter_config)

@guardrail(
    prompt_linter_config=config,
    on_fail=OnFailAction.EXCEPTION
)
async def process_customer_support(input_data: dict):
    return "Response generated"

async def main():
    print("--- Test Broken Prompt (Missing Variables) ---")
    bad_input = {
        "prompt": "Hello, here is your {query}. But I forgot the rest.",
        "variables": {"query": "how to reset password"}
    }
    try:
        await process_customer_support(bad_input)
    except Exception as e:
        print(f"Caught expected error: {e}")

    print("\n--- Test Valid Prompt with Warnings (No XML, No Fallback) ---")
    warning_input = {
        "prompt": "Hello {context}, {query}, {history}. I will help you.",
        "variables": {"context": "C", "query": "Q", "history": "H"}
    }
    await process_customer_support(warning_input)

    print("\n--- Test Good Prompt ---")
    good_input = {
        "prompt": """
        <context>{context}</context>
        <history>{history}</history>
        <query>{query}</query>
        If you don't know the answer, please say I don't know.
        """,
        "variables": {"context": "C", "query": "Q", "history": "H"}
    }
    await process_customer_support(good_input)

if __name__ == "__main__":
    asyncio.run(main())
