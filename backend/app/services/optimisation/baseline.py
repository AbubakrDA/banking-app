from typing import List
from app.services.optimisation.protocol import (
    AllocationDemand,
    AllocationItem,
    AllocationPlan,
)


class RuleBasedAllocationBaseline:
    """
    Deterministic, zero-dependency baseline OR allocator.
    Allocates integer minor units in descending priority order, then node_id.
    """

    provider_name = "baseline"

    def allocate(
        self,
        *,
        total_available_minor: int,
        demands: List[AllocationDemand],
    ) -> AllocationPlan:
        if total_available_minor < 0:
            raise ValueError("total_available_minor must be non-negative")

        remaining = total_available_minor
        ordered = sorted(demands, key=lambda d: (-d.priority, d.node_id))
        items: List[AllocationItem] = []

        for demand in ordered:
            if demand.requested_minor < 0:
                raise ValueError(f"Negative demand for node '{demand.node_id}'")
            grant = min(remaining, demand.requested_minor)
            remaining -= grant
            items.append(
                AllocationItem(
                    node_id=demand.node_id,
                    allocated_minor=grant,
                    unmet_minor=demand.requested_minor - grant,
                )
            )

        return AllocationPlan(
            provider_name=self.provider_name,
            total_available_minor=total_available_minor,
            total_allocated_minor=total_available_minor - remaining,
            items=items,
        )
