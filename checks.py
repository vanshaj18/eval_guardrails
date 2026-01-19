# SPDX-FileCopyrightText: Copyright (c) 2025-2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import re
from typing import Any
from .data_models import GuardrailResult

async def check_injection(input_data: Any) -> GuardrailResult:
    """Simple check for prompt injection patterns."""
    if not isinstance(input_data, str):
        input_data = str(input_data)
    
    patterns = [
        r"ignore previous instructions",
        r"system prompt",
        r"instead of what you were told",
        r"bypass",
    ]
    
    for pattern in patterns:
        if re.search(pattern, input_data, re.IGNORECASE):
            return GuardrailResult(passed=False, message=f"Potential injection detected: {pattern}")
    
    return GuardrailResult(passed=True)

async def check_pii(input_data: Any) -> GuardrailResult:
    """Simple check for PII (emails, phone numbers)."""
    if not isinstance(input_data, str):
        input_data = str(input_data)
    
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    
    if re.search(email_pattern, input_data):
        return GuardrailResult(passed=False, message="Email address detected")
    
    if re.search(phone_pattern, input_data):
        return GuardrailResult(passed=False, message="Phone number detected")
    
    return GuardrailResult(passed=True)
