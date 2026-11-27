from typing import Dict
from app.services.optimisation.baseline import RuleBasedAllocationBaseline
from app.services.optimisation.protocol import OptimisationProvider


class OptimisationRegistry:
    """Registry for pluggable OR solvers (defaults to deterministic rule-based baseline)."""

    PROVIDERS: Dict[str, type] = {
        "baseline": RuleBasedAllocationBaseline,
    }

    @classmethod
    def get_provider(cls, provider_name: str = "baseline") -> OptimisationProvider:
        if provider_name not in cls.PROVIDERS:
            raise ValueError(f"Unknown optimisation provider: '{provider_name}'")
        return cls.PROVIDERS[provider_name]()
