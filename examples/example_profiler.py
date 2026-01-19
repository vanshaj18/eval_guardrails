# SPDX-FileCopyrightText: Copyright (c) 2026. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
from pydantic import BaseModel, Field
from guardrails import guardrail, OnFailAction

# Setup logging to see profiling info
logging.basicConfig(level=logging.INFO)

class ResponseSchema(BaseModel):
    answer: str
    confidence: float

@guardrail(
    output_schema=ResponseSchema,
    model_name="gpt-5",
    enable_profiling=True,
    on_fail=OnFailAction.RETRY
)
async def profiled_rag_system(query: str):
    # Simulating RAG response
    return {
        "answer": f"Here is some information about {query}. It is quite extensive and detailed.",
        "confidence": 0.98
    }

async def main():
    print("--- Test Token Profiling ---")
    query = "What is quantum computing?"
    result = await profiled_rag_system(query)
    
    print(f"\nResponse: {result['answer']}")
    if "usage" in result:
        usage = result["usage"]
        print(f"Usage Details: {usage}")
        print(f"Estimated Cost: ${usage['estimated_cost']:.6f}")

if __name__ == "__main__":
    asyncio.run(main())
