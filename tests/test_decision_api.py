
from uuid import uuid4
from src.experimentguard.models import (
    ExperimentRecord,
    AssignmentRecord,
    EventRecord,
)


def test_decision_api_no_assignments(api_client, db_session):
    experiment_id = f"decision_api_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Decision API Empty Experiment",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="draft",
    )

    db_session.add(experiment)
    db_session.flush()

    response = api_client.get(
        f"/experiments/{experiment_id}/decision"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["experiment_id"] == experiment_id
    assert data["health_status"] == "invalid"
    assert data["decision"] == "investigate"


def test_decision_api_experiment_not_found(api_client):
    experiment_id = f"missing_{uuid4().hex}"

    response = api_client.get(
        f"/experiments/{experiment_id}/decision"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Experiment not found."




def test_decision_api_significant_improvement(api_client, db_session):
    experiment_id = f"decision_api_{uuid4().hex[:12]}"


    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Decision API Conversion Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
        planned_sample_size=200,
    )

    db_session.add(experiment)
    db_session.flush()

    # Assign 100 users to A and 100 users to B.
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

    # 10 conversions for variant A.
    for i in range(10):
        db_session.add(
            EventRecord(
                event_id=f"{experiment_id}_a_{i}",
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                event_type="conversion",
            )
        )

    # 30 conversions for variant B.
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

    response = api_client.get(
        f"/experiments/{experiment_id}/decision"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["experiment_id"] == experiment_id
    assert data["health_status"] == "healthy"
    assert data["decision"] == "rollout_b"
