# SPDX-FileCopyrightText: Copyright (c) 2026. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import functools
import logging
from typing import Any, Callable, Type, List, Optional
from pydantic import BaseModel, ValidationError

from .data_models import OnFailAction, GuardrailCheck, CheckFailureException, ValidationException, FullPromptLinterConfig
from .adapters.registry import registry
from .profiler import token_profiler
from .prompt_linter import PromptLinter

logger = logging.getLogger(__name__)

def guardrail(
    input_checks: List[Callable[[Any], Any]] = None,
    output_schema: Optional[Type[BaseModel]] = None,
    on_fail: OnFailAction = OnFailAction.EXCEPTION,
    max_retries: int = 2,
    fallback_value: Any = None,
    model_name: Optional[str] = None,
    enable_profiling: bool = False,
    prompt_linter_config: Optional[FullPromptLinterConfig] = None
):
    """
    Decorator to apply guardrails to a function.
    
    Args:
        input_checks: List of functions to check the input data.
        output_schema: Pydantic model to validate the output.
        on_fail: Action to take on failure (retry, exception, fallback).
        max_retries: Number of retries if on_fail is 'retry'.
        fallback_value: Value to return if on_fail is 'fallback'.
        model_name: Name of the model for token profiling.
        enable_profiling: Whether to enable token utilization and cost profiling.
        prompt_linter_config: Configuration for prompt linting.
    """
    input_checks = input_checks or []
    linter = PromptLinter(prompt_linter_config) if prompt_linter_config else None

    def decorator(func: Callable):
        adapter = registry.get_adapter(func)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            input_data = adapter.extract_input(*args, **kwargs)
            
            # Prompt Linter Check
            if linter:
                # If input_data is a dict with 'prompt' key
                prompt_text = None
                variables = {}
                if isinstance(input_data, str):
                    prompt_text = input_data
                elif isinstance(input_data, dict):
                    prompt_text = input_data.get("prompt")
                    variables = input_data.get("variables", {})
                
                if prompt_text:
                    lint_result = await linter.lint(prompt_text, variables)
                    if not lint_result.passed:
                        msg = f"Prompt Linter failed: {lint_result.message}"
                        if on_fail == OnFailAction.EXCEPTION:
                            raise CheckFailureException(msg)
                        logger.warning(msg)
                        if on_fail == OnFailAction.FALLBACK:
                            return fallback_value
                    elif lint_result.message: # Contains warnings
                        logger.warning(f"Prompt Linter warnings: {lint_result.message}")

            # Perform input checks
            for check in input_checks:
                result = await check(input_data)
                # Check if it's a GuardrailResult or just a bool
                if hasattr(result, "passed"):
                    if not result.passed:
                        msg = f"Input check failed: {result.message}"
                        if on_fail == OnFailAction.EXCEPTION:
                            raise CheckFailureException(msg)
                        logger.warning(msg)
                        if on_fail == OnFailAction.FALLBACK:
                            return fallback_value
                elif not result:
                    msg = f"Input check failed: {check.__name__}"
                    if on_fail == OnFailAction.EXCEPTION:
                        raise CheckFailureException(msg)
                    logger.warning(msg)
                    if on_fail == OnFailAction.FALLBACK:
                        return fallback_value

            # Execute the function with retry logic
            retries = 0
            while True:
                try:
                    output = await adapter.call(func, *args, **kwargs)
                    
                    # Token Profiling
                    if enable_profiling and model_name:
                        usage = token_profiler.estimate_cost(model_name, input_data, output)
                        logger.info(
                            f"Token Utilization [{model_name}]: "
                            f"Input: {usage.input_tokens}, Output: {usage.output_tokens}, "
                            f"Total: {usage.total_tokens}, Estimated Cost: ${usage.estimated_cost:.6f}"
                        )
                        # Optionally attach usage to output if it's a dict and not already present
                        if isinstance(output, dict) and "usage" not in output:
                            output["usage"] = usage.model_dump()

                    # Validate output schema
                    if output_schema:
                        try:
                            output_schema.model_validate(output)
                        except ValidationError as e:
                            msg = f"Output validation failed: {str(e)}"
                            if on_fail == OnFailAction.EXCEPTION:
                                raise ValidationException(msg)
                            logger.warning(msg)
                            
                            if on_fail == OnFailAction.RETRY and retries < max_retries:
                                retries += 1
                                logger.info(f"Retrying execution (attempt {retries})")
                                continue
                            
                            if on_fail == OnFailAction.FALLBACK:
                                return fallback_value
                            raise ValidationException(msg)

                    return output

                except Exception as e:
                    if on_fail == OnFailAction.RETRY and retries < max_retries:
                        retries += 1
                        logger.info(f"Retrying execution due to exception: {str(e)} (attempt {retries})")
                        continue
                    
                    if on_fail == OnFailAction.FALLBACK:
                        return fallback_value
                    
                    if not isinstance(e, (ValidationException, CheckFailureException)):
                        raise e
                    
                    if on_fail == OnFailAction.EXCEPTION:
                        raise e
                    
                    return None

        return wrapper

    return decorator
