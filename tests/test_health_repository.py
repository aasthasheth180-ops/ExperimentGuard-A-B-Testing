import pytest
from uuid import uuid4

from src.experimentguard.health_repository import HealthRepository
from src.experimentguard.models import (
    ExperimentRecord,
    AssignmentRecord,
)

def test_health_repository_balanced(db_session):
    experiment_id = f"health_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Health Repository Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
    )

    db_session.add(experiment)
    db_session.flush()

    for i in range(100):
        variant = "A" if i < 50 else "B"

        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                variant=variant,
            )
        )

    db_session.flush()

    repository = HealthRepository(db_session)

    counts = repository.metrics_repository.get_assigned_users(
    experiment_id
)

    print("Assignment counts:", counts)
    print("Data type:", type(counts))

    result = repository.get_assignment_health(
        experiment_id
    )

    assert result["status"] == "healthy"
    assert result["validation"]["total_users"] == 100
    assert result["srm"]["has_srm"] is False


def test_health_repository_zero_assignment_variant(db_session):
    experiment_id = f"health_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Zero Assignment Variant Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
    )

    db_session.add(experiment)
    db_session.flush()

    # All 100 users are assigned to A.
    # Variant B receives zero users.
    for i in range(100):
        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                variant="A",
            )
        )

    db_session.flush()

    repository = HealthRepository(db_session)

    result = repository.get_assignment_health(
        experiment_id
    )

    assert result["status"] == "warning"
    assert result["validation"]["is_valid"] is True
    assert result["validation"]["total_users"] == 100

    assert result["srm"]["observed_counts"] == {
        "A": 100,
        "B": 0,
    }

    assert result["srm"]["has_srm"] is True



def test_health_repository_no_assignments(db_session):
    experiment_id = f"health_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Empty Experiment Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="draft",
    )

    db_session.add(experiment)
    db_session.flush()

    repository = HealthRepository(db_session)

    result = repository.get_assignment_health(
        experiment_id
    )

    assert result["status"] == "invalid"
    assert result["validation"]["is_valid"] is False
    assert result["validation"]["total_users"] == 0

    assert result["validation"]["issues"] == [
        "No assigned users."
    ]

    assert result["srm"] is None


def test_health_repository_experiment_not_found(db_session):
    repository = HealthRepository(db_session)

    experiment_id = f"missing_{uuid4().hex}"

    with pytest.raises(
        ValueError,
        match="Experiment not found",
    ):
        repository.get_assignment_health(
            experiment_id
        )