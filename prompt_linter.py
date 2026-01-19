# SPDX-FileCopyrightText: Copyright (c) 2026. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import re
from typing import Any, Optional
from .data_models import FullPromptLinterConfig, GuardrailResult
from .profiler import token_profiler

class PromptLinter:
    def __init__(self, config: Optional[FullPromptLinterConfig] = None):
        self.config = config or FullPromptLinterConfig()

    async def lint(self, prompt: str, variables: Optional[dict[str, Any]] = None) -> GuardrailResult:
        """
        Lints the prompt based on configuration.
        """
        errors = []
        warnings = []
        
        # 1. Structural Errors: Broken placeholders
        # Look for things like {{var} or {var
        broken_placeholders = re.findall(r"\{[^{}]*$", prompt) + re.findall(r"^[^{}]*\}", prompt)
        if broken_placeholders:
            errors.append(f"Structural Error: Potential broken placeholders detected: {broken_placeholders}")

        # Missing variables
        if self.config.prompt_config.expected_variables:
            for var in self.config.prompt_config.expected_variables:
                if f"{{{var}}}" not in prompt:
                    errors.append(f"Structural Error: Expected variable '{{{var}}}' not found in prompt.")

        # 2. Best Practices
        # XML tags/Markdown delimiters
        if self.config.prompt_config.enforce_xml_tags:
            # Check for common XML tag patterns like <context>, <query>
            if not re.search(r"<[a-zA-Z0-9]+>.*?</[a-zA-Z0-9]+>", prompt, re.DOTALL):
                warnings.append("Best Practice: No XML tags detected despite 'enforce_xml_tags' being enabled.")

        # Fallback instructions
        if self.config.prompt_config.require_fallback_phrase:
            fallback_keywords = ["if you don't know", "fallback", "I'm sorry", "cannot answer"]
            if not any(kw.lower() in prompt.lower() for kw in fallback_keywords):
                warnings.append("Best Practice: No fallback instructions (e.g., 'if you don't know') detected.")

        # 3. Optimization: Static vs Dynamic token budget
        # We estimate static budget by looking at prompt without variables
        static_prompt = prompt
        if variables:
            for k, v in variables.items():
                static_prompt = static_prompt.replace(f"{{{k}}}", "")
        
        total_tokens = token_profiler.count_tokens(prompt)
        static_tokens = token_profiler.count_tokens(static_prompt)
        
        if total_tokens > 0:
            static_ratio = static_tokens / total_tokens
            if static_ratio > self.config.prompt_config.max_static_token_percentage:
                warnings.append(
                    f"Optimization: Static parts consume {static_ratio:.1%} of the prompt tokens, "
                    f"exceeding the limit of {self.config.prompt_config.max_static_token_percentage:.1%}"
                )

        if errors:
            return GuardrailResult(passed=False, message="; ".join(errors), data={"warnings": warnings})
        
        if warnings:
            return GuardrailResult(passed=True, message="; ".join(warnings), data={"warnings": warnings})

        return GuardrailResult(passed=True)

# Standard linter
standard_linter = PromptLinter()
