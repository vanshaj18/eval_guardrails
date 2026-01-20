# SPDX-FileCopyrightText: Copyright (c) 2026. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Callable, Awaitable, TypeVar, Generic, Protocol, runtime_checkable, Optional
from pydantic import BaseModel, Field
from enum import Enum

T = TypeVar("T")

class OnFailAction(str, Enum):
    RETRY = "retry"
    EXCEPTION = "exception"
    FALLBACK = "fallback"

@runtime_checkable
class GuardrailCheck(Protocol):
    async def __call__(self, input_data: Any) -> bool:
        ...

class GuardrailResult(BaseModel):
    passed: bool
    message: str | None = None
    data: Any = None

class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    carbon_emissions_g: float = 0.0
    energy_kwh: float = 0.0
    model_name: str | None = None

class ProfileResult(BaseModel):
    usage: TokenUsage
    metadata: dict[str, Any] = Field(default_factory=dict)

class PromptConfig(BaseModel):
    template_id: str | None = None
    expected_variables: list[str] = Field(default_factory=list)
    enforce_xml_tags: bool = False
    require_fallback_phrase: bool = False
    max_static_token_percentage: float = 0.5  # Max 50% static tokens by default

class PipelineConfig(BaseModel):
    model_provider: str | None = None
    model_name: str | None = None

class FullPromptLinterConfig(BaseModel):
    pipeline_config: PipelineConfig = Field(default_factory=PipelineConfig)
    prompt_config: PromptConfig = Field(default_factory=PromptConfig)

class GuardrailException(Exception):
    """Base exception for guardrail failures."""
    pass

class ValidationException(GuardrailException):
    """Raised when output validation fails."""
    pass

class CheckFailureException(GuardrailException):
    """Raised when an input check fails."""
    pass
