# SPDX-FileCopyrightText: Copyright (c) 2025-2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
from typing import Any, Optional
from pathlib import Path
from .data_models import TokenUsage

class TokenProfiler:
    def __init__(self, token_details_path: Optional[str] = None):
        if token_details_path is None:
            token_details_path = str(Path(__file__).parent / "tokenDetails.json")
        
        self.token_details_path = token_details_path
        self.model_costs = self._load_token_details()

    def _load_token_details(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.token_details_path):
            return []
        with open(self.token_details_path, "r") as f:
            return json.load(f)

    def get_model_info(self, model_name: str) -> Optional[dict[str, Any]]:
        for provider in self.model_costs:
            for variant in provider.get("variants", []):
                if variant["model_name"] == model_name:
                    # Return variant info with provider metadata if needed
                    return variant
        return None

    def count_tokens(self, text: Any) -> int:
        """Simple token counting heuristic (approx 4 characters per token)."""
        if not text:
            return 0
        if not isinstance(text, str):
            text = str(text)
        # Rough heuristic: 1 token ~= 4 characters
        return max(1, len(text) // 4)

    def estimate_cost(self, model_name: str, input_text: Any, output_text: Any) -> TokenUsage:
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        total_tokens = input_tokens + output_tokens
        
        cost = 0.0
        info = self.get_model_info(model_name)
        if info:
            input_cost = (input_tokens / 1000) * info["input_cost_per_1k"]
            output_cost = (output_tokens / 1000) * info["output_cost_per_1k"]
            cost = input_cost + output_cost
        
        return TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=cost,
            model_name=model_name
        )

# Global profiler instance
token_profiler = TokenProfiler()
