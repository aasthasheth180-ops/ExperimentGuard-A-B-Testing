import pytest

from uuid import uuid4

from src.experimentguard.models import (
    ExperimentRecord,
    AssignmentRecord,
)

def test_health_api_no_assignments(api_client, db_session):
    experiment_id = f"health_api_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Health API Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="draft",
    )

    db_session.add(experiment)
    db_session.flush()

    response = api_client.get(
        f"/experiments/{experiment_id}/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["experiment_id"] == experiment_id
    assert data["status"] == "invalid"
    assert data["validation"]["total_users"] == 0
    assert data["srm"] is None



def test_health_api_experiment_not_found(api_client):
    experiment_id = f"missing_{uuid4().hex}"

    response = api_client.get(
        f"/experiments/{experiment_id}/health"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Experiment not found."


def test_health_api_balanced_assignments(api_client, db_session):
    experiment_id = f"health_api_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Balanced Health API Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
    )

    db_session.add(experiment)
    db_session.flush()

    # Assign 50 users to A and 50 users to B.
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

    response = api_client.get(
        f"/experiments/{experiment_id}/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["experiment_id"] == experiment_id
    assert data["status"] == "healthy"
    assert data["validation"]["is_valid"] is True
    assert data["validation"]["total_users"] == 100

    assert data["srm"]["observed_counts"] == {
        "A": 50,
        "B": 50,
    }

    assert data["srm"]["has_srm"] is False


def test_health_api_srm_warning(api_client, db_session):
    experiment_id = f"health_api_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="SRM Warning API Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
    )

    db_session.add(experiment)
    db_session.flush()

    # Assign 70 users to A and 30 users to B.
    for i in range(100):
        variant = "A" if i < 70 else "B"

        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=f"user_{i}",
                variant=variant,
            )
        )

    db_session.flush()

    response = api_client.get(
        f"/experiments/{experiment_id}/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["experiment_id"] == experiment_id
    assert data["status"] == "warning"
    assert data["validation"]["is_valid"] is True
    assert data["validation"]["total_users"] == 100

    assert data["srm"]["observed_counts"] == {
        "A": 70,
        "B": 30,
    }

    assert data["srm"]["chi_square"] == pytest.approx(16.0)
    assert data["srm"]["p_value"] < 0.001
    assert data["srm"]["has_srm"] is True