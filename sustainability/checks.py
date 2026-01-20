# SPDX-FileCopyrightText: Copyright (c) 2026. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional
from ..data_models import GuardrailResult
from .calculator import sustainability_calculator
from ..profiler import token_profiler

async def check_prompt_efficiency(input_data: Any, max_carbon_g: float = 0.05) -> GuardrailResult:
    """
    Checks if the prompt is efficient in terms of estimated carbon footprint.
    This check estimates the carbon emissions for the input prompt.
    """
    if not isinstance(input_data, str):
        text = str(input_data)
    else:
        text = input_data

    # Estimate tokens for the input
    tokens = token_profiler.count_tokens(text)
    
    # Estimate carbon for these tokens (assuming a standard model if none provided, or just base on tokens)
    # We'll use a conservative estimate or a default model name if we want more accuracy.
    # For a check, we might just look at the token count as a proxy, 
    # but since we have the calculator, let's use it.
    
    # Assuming a mid-range model like gpt-4o for reference if none specified
    stats = sustainability_calculator.calculate_emissions(total_tokens=tokens, model_name="gpt-4o")
    carbon_g = stats["carbon_g"]

    if carbon_g > max_carbon_g:
        return GuardrailResult(
            passed=False, 
            message=f"Prompt is inefficient: Estimated input carbon ({carbon_g:.4f}g) exceeds limit ({max_carbon_g}g). "
                    f"Consider shortening the prompt or removing redundant information.",
            data=stats
        )

    return GuardrailResult(
        passed=True, 
        message=f"Prompt efficiency check passed: {carbon_g:.4f}g CO2e estimated.",
        data=stats
    )
