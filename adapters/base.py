# SPDX-FileCopyrightText: Copyright (c) 2025-2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable

class FrameworkAdapter(ABC):
    """Abstract base class for framework adapters."""
    
    @abstractmethod
    def can_handle(self, target: Any) -> bool:
        """Check if this adapter can handle the target object."""
        pass

    @abstractmethod
    async def call(self, target: Any, *args: Any, **kwargs: Any) -> Any:
        """Call the target object with the given arguments."""
        pass

    @abstractmethod
    def extract_input(self, *args: Any, **kwargs: Any) -> Any:
        """Extract the main input data from the arguments."""
        pass
