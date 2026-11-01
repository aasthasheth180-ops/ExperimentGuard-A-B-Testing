
from uuid import uuid4

from src.experimentguard.decision_repository import DecisionRepository
from src.experimentguard.models import (
    ExperimentRecord,
    AssignmentRecord,
    EventRecord,
)


def test_decision_repository_no_assignments(db_session):
    experiment_id = f"decision_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
    experiment_id=experiment_id,
    name="Decision Repository Test",
    variants={"A": 0.5, "B": 0.5},
    primary_metric="conversion",
    status="running",
    planned_sample_size=200,
)

    db_session.add(experiment)
    db_session.flush()

    repository = DecisionRepository(db_session)

    result = repository.get_decision(experiment_id)

    assert result["experiment_id"] == experiment_id
    assert result["health_status"] == "invalid"
    assert result["decision"] == "investigate"




def test_decision_repository_significant_improvement(db_session):
    experiment_id = f"decision_{uuid4().hex[:12]}"


    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Checkout Redesign Decision Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
        planned_sample_size=200,
    )


    db_session.add(experiment)
    db_session.flush()

    # Create 200 assignments: 100 in A, 100 in B.
    for i in range(200):
        variant = "A" if i < 100 else "B"

        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                variant=variant,
            )
        )

    db_session.flush()

    # Variant A: 10 conversions out of 100 users.
    for i in range(10):
        db_session.add(
            EventRecord(
                event_id=f"{experiment_id}_a_{i}",
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                event_type="conversion",
            )
        )

    # Variant B: 30 conversions out of 100 users.
    for i in range(100, 130):
        db_session.add(
            EventRecord(
                event_id=f"{experiment_id}_b_{i}",
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                event_type="conversion",
            )
        )

    db_session.flush()

    repository = DecisionRepository(db_session)

    result = repository.get_decision(experiment_id)

    assert result["experiment_id"] == experiment_id
    assert result["health_status"] == "healthy"
    assert result["decision"] == "rollout_b"


def test_decision_repository_srm_warning(db_session):
    experiment_id = f"decision_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="SRM Warning Decision Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
    )

    db_session.add(experiment)
    db_session.flush()

    # Intentionally imbalanced: 90 users in A, 10 in B.
    for i in range(100):
        variant = "A" if i < 90 else "B"

        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                variant=variant,
            )
        )

    db_session.flush()

    repository = DecisionRepository(db_session)
    result = repository.get_decision(experiment_id)

    assert result["experiment_id"] == experiment_id
    assert result["health_status"] == "warning"
    assert result["decision"] == "investigate"



def test_decision_repository_insufficient_data(db_session):
    experiment_id = f"decision_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Insufficient Data Decision Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
    )

    db_session.add(experiment)
    db_session.flush()

    # Only 4 users: 2 assigned to A and 2 to B.
    for i in range(4):
        variant = "A" if i < 2 else "B"

        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                variant=variant,
            )
        )

    db_session.flush()

    repository = DecisionRepository(db_session)
    result = repository.get_decision(experiment_id)

    assert result["experiment_id"] == experiment_id
    assert result["health_status"] == "insufficient_data"
    assert result["decision"] == "continue_experiment"


def test_decision_repository_before_sample_size(db_session):
    experiment_id = f"decision_{uuid4().hex[:12]}"


    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Checkout Redesign Decision Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
        planned_sample_size=500,
    )


    db_session.add(experiment)
    db_session.flush()

    # Create 200 assignments: 100 in A, 100 in B.
    for i in range(200):
        variant = "A" if i < 100 else "B"

        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                variant=variant,
            )
        )

    db_session.flush()

    # Variant A: 10 conversions out of 100 users.
    for i in range(10):
        db_session.add(
            EventRecord(
                event_id=f"{experiment_id}_a_{i}",
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                event_type="conversion",
            )
        )

    # Variant B: 30 conversions out of 100 users.
    for i in range(100, 130):
        db_session.add(
            EventRecord(
                event_id=f"{experiment_id}_b_{i}",
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                event_type="conversion",
            )
        )

    db_session.flush()

    repository = DecisionRepository(db_session)

    result = repository.get_decision(experiment_id)

    assert result["experiment_id"] == experiment_id
    assert result["health_status"] == "healthy"
    assert result["decision"] == "continue_experiment"
