import pytest
from unittest.mock import patch
from uuid import uuid4

from src.experimentguard.models import (
    ExperimentRecord,
    AssignmentRecord,
    EventRecord,
)
from src.experimentguard.metrics_repository import MetricsRepository
from src.experimentguard.statistics_repository import StatisticsRepository

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


def test_statistics_repository_nonexistent_experiment(db_session):
    repository = StatisticsRepository(db_session)

    with pytest.raises(
        ValueError,
        match="Experiment must contain variants A and B",
    ):
        repository.get_significance("nonexistent_experiment")




def test_statistics_repository_with_database(db_session):
    experiment_id = f"stats_{uuid4().hex[:12]}"

    db_session.add(
        ExperimentRecord(
            experiment_id=experiment_id,
            name="Statistical Significance Test",
            variants={"A": 0.5, "B": 0.5},
            primary_metric="conversion",
            status="running",
        )
    )

    db_session.flush()

    # Create 10 users in each variant
    for variant in ["A", "B"]:
        for i in range(10):
            db_session.add(
                AssignmentRecord(
                    experiment_id=experiment_id,
                    user_id=f"{variant}_user_{i}",
                    variant=variant,
                )
            )

    db_session.flush()

    # A: 2 conversions out of 10 users
    # B: 8 conversions out of 10 users
    for variant, conversions in [("A", 2), ("B", 8)]:
        for i in range(conversions):
            db_session.add(
                EventRecord(
                    event_id=f"event_{uuid4().hex}",
                    experiment_id=experiment_id,
                    user_id=f"{variant}_user_{i}",
                    event_type="conversion",
                    properties={},
                )
            )

    db_session.flush()

    repository = StatisticsRepository(db_session)
    result = repository.get_significance(experiment_id)

    assert result["conversion_rate_a"] == pytest.approx(0.2)
    assert result["conversion_rate_b"] == pytest.approx(0.8)
    assert result["absolute_difference"] == pytest.approx(0.6)
    assert result["p_value"] < 0.05
    assert result["is_significant"] is True



def test_statistics_repository_not_significant(db_session):
    experiment_id = f"stats_equal_{uuid4().hex[:12]}"

    db_session.add(
        ExperimentRecord(
            experiment_id=experiment_id,
            name="Non-Significant Experiment",
            variants={"A": 0.5, "B": 0.5},
            primary_metric="conversion",
            status="running",
        )
    )

    db_session.flush()

    # Create 10 users in each variant
    for variant in ["A", "B"]:
        for i in range(10):
            db_session.add(
                AssignmentRecord(
                    experiment_id=experiment_id,
                    user_id=f"{variant}_user_{i}",
                    variant=variant,
                )
            )

    db_session.flush()

    # Both variants have 3 conversions
    for variant in ["A", "B"]:
        for i in range(3):
            db_session.add(
                EventRecord(
                    event_id=f"event_{uuid4().hex}",
                    experiment_id=experiment_id,
                    user_id=f"{variant}_user_{i}",
                    event_type="conversion",
                    properties={},
                )
            )

    db_session.flush()

    repository = StatisticsRepository(db_session)
    result = repository.get_significance(experiment_id)

    assert result["conversion_rate_a"] == pytest.approx(0.3)
    assert result["conversion_rate_b"] == pytest.approx(0.3)
    assert result["absolute_difference"] == pytest.approx(0.0)
    assert result["z_statistic"] == pytest.approx(0.0)
    assert result["p_value"] == pytest.approx(1.0)
    assert result["is_significant"] is False



def test_statistics_api_experiment_not_found(api_client):
    response = api_client.get(
        "/experiments/nonexistent_experiment/statistics"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Experiment not found."




def test_statistics_api_success(api_client, db_session):
    experiment_id = f"stats_api_{uuid4().hex[:12]}"

    db_session.add(
        ExperimentRecord(
            experiment_id=experiment_id,
            name="Statistics API Test",
            variants={"A": 0.5, "B": 0.5},
            primary_metric="conversion",
            status="running",
        )
    )

    db_session.flush()

    # Create 10 assigned users per variant
    for variant in ["A", "B"]:
        for i in range(10):
            db_session.add(
                AssignmentRecord(
                    experiment_id=experiment_id,
                    user_id=f"{variant}_user_{i}",
                    variant=variant,
                )
            )

    db_session.flush()

    # A: 2/10 conversions; B: 8/10 conversions
    for variant, conversions in [("A", 2), ("B", 8)]:
        for i in range(conversions):
            db_session.add(
                EventRecord(
                    event_id=f"event_{uuid4().hex}",
                    experiment_id=experiment_id,
                    user_id=f"{variant}_user_{i}",
                    event_type="conversion",
                    properties={},
                )
            )

    db_session.flush()

    response = api_client.get(
        f"/experiments/{experiment_id}/statistics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["experiment_id"] == experiment_id

    statistics = data["statistics"]

    assert statistics["conversion_rate_a"] == pytest.approx(0.2)
    assert statistics["conversion_rate_b"] == pytest.approx(0.8)
    assert statistics["absolute_difference"] == pytest.approx(0.6)
    assert statistics["p_value"] < 0.05
    assert statistics["is_significant"] is True
    assert "normal_approximation_valid" in statistics
    assert statistics["normal_approximation_valid"] is True

    assert "z_statistic" in statistics
    assert "confidence_interval" in statistics



def test_statistics_api_insufficient_data(api_client, db_session):
    experiment_id = f"stats_empty_{uuid4().hex[:12]}"

    db_session.add(
        ExperimentRecord(
            experiment_id=experiment_id,
            name="Empty Statistics Experiment",
            variants={"A": 0.5, "B": 0.5},
            primary_metric="conversion",
            status="running",
        )
    )

    db_session.flush()

    response = api_client.get(
        f"/experiments/{experiment_id}/statistics"
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Both variants must have users."