import pytest
from app.services.optimisation import (
    AllocationDemand,
    OptimisationProvider,
    OptimisationRegistry,
)


def test_optimisation_baseline_deterministic_allocation() -> None:
    provider = OptimisationRegistry.get_provider("baseline")
    assert isinstance(provider, OptimisationProvider)

    demands = [
        AllocationDemand(node_id="branch_south", requested_minor=50_000, priority=1),
        AllocationDemand(node_id="branch_north", requested_minor=80_000, priority=3),
        AllocationDemand(node_id="agent_west", requested_minor=40_000, priority=2),
    ]

    plan = provider.allocate(total_available_minor=100_000, demands=demands)
    assert plan.provider_name == "baseline"
    assert plan.total_allocated_minor == 100_000

    by_node = {item.node_id: item for item in plan.items}
    assert by_node["branch_north"].allocated_minor == 80_000
    assert by_node["branch_north"].unmet_minor == 0
    assert by_node["agent_west"].allocated_minor == 20_000
    assert by_node["agent_west"].unmet_minor == 20_000
    assert by_node["branch_south"].allocated_minor == 0
    assert by_node["branch_south"].unmet_minor == 50_000


def test_optimisation_unknown_provider_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown optimisation provider"):
        OptimisationRegistry.get_provider("external_commercial_solver")
