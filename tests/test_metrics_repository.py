import pytest
from unittest.mock import patch
from uuid import uuid4

from src.experimentguard.models import (
    ExperimentRecord,
    AssignmentRecord,
    EventRecord,
)
from src.experimentguard.metrics_repository import MetricsRepository



def test_conversion_rates(db_session):
    experiment_id = f"metrics_{uuid4().hex[:12]}"

    experiment = ExperimentRecord(
        experiment_id=experiment_id,
        name="Metrics Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
    )

    db_session.add(experiment)
    db_session.flush()

    for user_id, variant in [
        ("user_1", "A"),
        ("user_2", "A"),
        ("user_3", "B"),
        ("user_4", "B"),
    ]:
        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=user_id,
                variant=variant,
            )
        )

    db_session.flush()

    for user_id in ["user_1", "user_1", "user_3"]:
        db_session.add(
            EventRecord(
                event_id=f"event_{uuid4().hex}",
                experiment_id=experiment_id,
                user_id=user_id,
                event_type="conversion",
                properties={},
            )
        )

    db_session.flush()

    repository = MetricsRepository(db_session)
    results = repository.get_conversion_rates(experiment_id)

    assert results["A"]["assigned_users"] == 2
    assert results["A"]["converted_users"] == 1
    assert results["A"]["conversion_rate"] == 0.5

    assert results["B"]["assigned_users"] == 2
    assert results["B"]["converted_users"] == 1
    assert results["B"]["conversion_rate"] == 0.5


def test_conversion_rates_with_zero_conversions(db_session):
    experiment_id = f"metrics_zero_{uuid4().hex[:12]}"

    db_session.add(
        ExperimentRecord(
            experiment_id=experiment_id,
            name="Zero Conversion Test",
            variants={"A": 0.5, "B": 0.5},
            primary_metric="conversion",
            status="running",
        )
    )

    db_session.flush()

    for user_id, variant in [
        ("user_1", "A"),
        ("user_2", "A"),
        ("user_3", "B"),
    ]:
        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=user_id,
                variant=variant,
            )
        )

    db_session.flush()

    repository = MetricsRepository(db_session)
    results = repository.get_conversion_rates(experiment_id)

    assert results["A"]["assigned_users"] == 2
    assert results["A"]["converted_users"] == 0
    assert results["A"]["conversion_rate"] == 0.0

    assert results["B"]["assigned_users"] == 1
    assert results["B"]["converted_users"] == 0
    assert results["B"]["conversion_rate"] == 0.0

def test_relative_lift(db_session):
    repository = MetricsRepository(db_session)

    # Test positive lift: +25%
    with patch.object(
        repository,
        "get_conversion_rates",
        return_value={
            "A": {"conversion_rate": 0.08},
            "B": {"conversion_rate": 0.10},
        },
    ):
        assert repository.get_relative_lift("test_exp") == pytest.approx(25.0)

    # Test negative lift: -20%
    with patch.object(
        repository,
        "get_conversion_rates",
        return_value={
            "A": {"conversion_rate": 0.10},
            "B": {"conversion_rate": 0.08},
        },
    ):
        assert repository.get_relative_lift("test_exp") == pytest.approx(-20.0)

    # Test zero baseline
    with patch.object(
        repository,
        "get_conversion_rates",
        return_value={
            "A": {"conversion_rate": 0.0},
            "B": {"conversion_rate": 0.10},
        },
    ):
        assert repository.get_relative_lift("test_exp") is None



def test_metrics_api(api_client, db_session):
    experiment_id = f"metrics_api_{uuid4().hex[:12]}"

    db_session.add(
        ExperimentRecord(
            experiment_id=experiment_id,
            name="Metrics API Test",
            variants={"A": 0.5, "B": 0.5},
            primary_metric="conversion",
            status="running",
        )
    )
    db_session.flush()

    for user_id, variant in [
        ("user_1", "A"),
        ("user_2", "A"),
        ("user_3", "B"),
        ("user_4", "B"),
    ]:
        db_session.add(
            AssignmentRecord(
                experiment_id=experiment_id,
                user_id=user_id,
                variant=variant,
            )
        )

    db_session.flush()

    for user_id in ["user_1", "user_3", "user_4"]:
        db_session.add(
            EventRecord(
                event_id=f"event_{uuid4().hex}",
                experiment_id=experiment_id,
                user_id=user_id,
                event_type="conversion",
                properties={},
            )
        )

    db_session.flush()

    response = api_client.get(
        f"/experiments/{experiment_id}/metrics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["experiment_id"] == experiment_id

    assert data["variants"]["A"]["assigned_users"] == 2
    assert data["variants"]["A"]["converted_users"] == 1
    assert data["variants"]["A"]["conversion_rate"] == 0.5

    assert data["variants"]["B"]["assigned_users"] == 2
    assert data["variants"]["B"]["converted_users"] == 2
    assert data["variants"]["B"]["conversion_rate"] == 1.0

    assert data["relative_lift_percent"] == pytest.approx(100.0)


def test_metrics_api_experiment_not_found(api_client):
    response = api_client.get(
        "/experiments/nonexistent_experiment_123/metrics"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Experiment not found."
    }


def test_metrics_api_zero_assignments(api_client, db_session):
    experiment_id = f"metrics_empty_{uuid4().hex[:12]}"

    db_session.add(
        ExperimentRecord(
            experiment_id=experiment_id,
            name="Empty Experiment Test",
            variants={"A": 0.5, "B": 0.5},
            primary_metric="conversion",
            status="running",
        )
    )

    db_session.flush()

    response = api_client.get(
        f"/experiments/{experiment_id}/metrics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["experiment_id"] == experiment_id
    assert data["variants"] == {
    "A": {
        "assigned_users": 0,
        "converted_users": 0,
        "conversion_rate": 0.0,
    },
    "B": {
        "assigned_users": 0,
        "converted_users": 0,
        "conversion_rate": 0.0,
    },
}
    assert data["relative_lift_percent"] is None