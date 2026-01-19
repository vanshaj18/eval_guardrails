# SPDX-FileCopyrightText: Copyright (c) 2025-2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import inspect
from typing import Any, Callable
from .base import FrameworkAdapter

class PythonFunctionAdapter(FrameworkAdapter):
    """Adapter for standard Python functions (sync and async)."""
    
    def can_handle(self, target: Any) -> bool:
        return inspect.isfunction(target) or inspect.ismethod(target) or callable(target)

    async def call(self, target: Any, *args: Any, **kwargs: Any) -> Any:
        if inspect.iscoroutinefunction(target):
            return await target(*args, **kwargs)
        return target(*args, **kwargs)

    def extract_input(self, *args: Any, **kwargs: Any) -> Any:
        # For simple functions, usually the first arg is the input
        if args:
            return args[0]
        if kwargs:
            # Return the first kwarg if no positional args
            return next(iter(kwargs.values()))
        return None

class AdapterRegistry:
    def __init__(self):
        self._adapters: list[FrameworkAdapter] = [PythonFunctionAdapter()]

    def register(self, adapter: FrameworkAdapter):
        self._adapters.insert(0, adapter)

    def get_adapter(self, target: Any) -> FrameworkAdapter:
        for adapter in self._adapters:
            if adapter.can_handle(target):
                return adapter
        raise ValueError(f"No adapter found for target: {type(target)}")

registry = AdapterRegistry()
