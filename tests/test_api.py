from fastapi.testclient import TestClient

from src.experimentguard.api import app, manager


client = TestClient(app)


def setup_function():
    manager.experiments.clear()


def create_test_experiment():
    return client.post(
        "/experiments",
        json={
            "experiment_id": "checkout_v1",
            "name": "Checkout Redesign",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "purchase_conversion",
        },
    )


def test_create_experiment_api():
    response = create_test_experiment()

    assert response.status_code == 201
    assert response.json()["status"] == "draft"


def test_duplicate_experiment_api():
    create_test_experiment()

    response = create_test_experiment()

    assert response.status_code == 400
    assert response.json()["detail"] == "Experiment ID already exists."


def test_deterministic_assignment_api():
    create_test_experiment()

    status_response = client.patch(
        "/experiments/checkout_v1/status",
        json={"status": "running"},
    )

    assert status_response.status_code == 200

    first = client.get(
        "/experiments/checkout_v1/assign/user_101"
    )

    second = client.get(
        "/experiments/checkout_v1/assign/user_101"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["variant"] == second.json()["variant"]
    assert first.json()["variant"] in {"A", "B"}


def test_get_unknown_experiment_api():
    response = client.get("/experiments/does_not_exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Experiment not found."


def test_invalid_status_transition_api():
    create_test_experiment()

    client.patch(
        "/experiments/checkout_v1/status",
        json={"status": "running"},
    )

    response = client.patch(
        "/experiments/checkout_v1/status",
        json={"status": "draft"},
    )

    assert response.status_code == 400
    assert "Cannot transition" in response.json()["detail"]


def test_paused_experiment_assignment_api():
    create_test_experiment()

    client.patch(
        "/experiments/checkout_v1/status",
        json={"status": "running"},
    )

    client.patch(
        "/experiments/checkout_v1/status",
        json={"status": "paused"},
    )

    response = client.get(
        "/experiments/checkout_v1/assign/user_101"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Experiment must be running to assign users."
    )


def test_list_experiments_api():
    create_test_experiment()

    response = client.get("/experiments")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["experiment_id"] == "checkout_v1"