from dataclasses import dataclass
from typing import List, Protocol, runtime_checkable


@dataclass(frozen=True)
class AllocationDemand:
    node_id: str
    requested_minor: int
    priority: int = 1  # Higher integer = higher priority


@dataclass(frozen=True)
class AllocationItem:
    node_id: str
    allocated_minor: int
    unmet_minor: int


@dataclass(frozen=True)
class AllocationPlan:
    provider_name: str
    total_available_minor: int
    total_allocated_minor: int
    items: List[AllocationItem]


@runtime_checkable
class OptimisationProvider(Protocol):
    """Pluggable Operations Research (OR) solver interface; no external solver required by default."""

    provider_name: str

    def allocate(
        self,
        *,
        total_available_minor: int,
        demands: List[AllocationDemand],
    ) -> AllocationPlan:
        ...
