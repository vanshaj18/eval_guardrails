# SPDX-FileCopyrightText: Copyright (c) 2026. All rights reserved.
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
    """
    Detail check for PII including 
        - Email addresses
        - Phone numbers
        - Social Security Numbers
        - Credit Card Numbers
        - Driver's License Numbers
        - Passport Numbers
        - Bank Account Numbers
        - IP Addresses
        - URLs
    """
    if not isinstance(input_data, str):
        input_data = str(input_data)
    
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    ssn_pattern = r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b"
    ccn_pattern = r"\b\d{4}[-.]?\d{4}[-.]?\d{4}[-.]?\d{4}\b"
    dl_pattern = r"[A-Z]{2}\d{2}\d{4}\d{7}" # AA12 YYYYXXXXXXX
    pn_pattern = r"[A-Z]\d{7}" #AXXXXXXX
    bank_acc_pattern = r"[\d]{11}" #01234567891
    ip_address_pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
    
    if re.search(email_pattern, input_data):
        return GuardrailResult(passed=False, message="Email address detected")
    
    if re.search(phone_pattern, input_data):
        return GuardrailResult(passed=False, message="Phone number detected")

    if re.search(ssn_pattern, input_data):
        return GuardrailResult(passed=False, message="Social Security Number detected")

    if re.search(ccn_pattern, input_data):
        return GuardrailResult(passed=False, message="Credit Card Number detected")

    if re.search(dl_pattern, input_data):
        return GuardrailResult(passed=False, message="Driver's License Number detected")

    if re.search(pn_pattern, input_data):
        return GuardrailResult(passed=False, message="Passport Number detected")

    if re.search(bank_acc_pattern, input_data):
        return GuardrailResult(passed=False, message="Bank Account Number detected")

    if re.search(ip_address_pattern, input_data):
        return GuardrailResult(passed=False, message="IP Address detected")

    return GuardrailResult(passed=True)
