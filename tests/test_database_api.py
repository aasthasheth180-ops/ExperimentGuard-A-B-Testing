import pytest
from uuid import uuid4
from src.experimentguard.models import ExperimentRecord


def test_original_post_endpoint_uses_database(api_client, db_session):
    experiment_id = f"original_api_{uuid4().hex[:8]}"

    response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Original API Persistence Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion_rate",
        },
    )

    assert response.status_code == 201
    assert response.json()["experiment_id"] == experiment_id
    assert response.json()["status"] == "draft"

    record = db_session.get(ExperimentRecord, experiment_id)

    assert record is not None
    assert record.name == "Original API Persistence Test"

    print("\nOriginal POST endpoint saved to PostgreSQL successfully")



def test_get_experiment_from_database(api_client):
    experiment_id = f"get_api_{uuid4().hex[:8]}"

    # Create an experiment through the API.
    create_response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "GET Endpoint Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion_rate",
        },
    )

    assert create_response.status_code == 201

    # Retrieve the same experiment from PostgreSQL.
    get_response = api_client.get(
        f"/experiments/{experiment_id}"
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["experiment_id"] == experiment_id
    assert data["name"] == "GET Endpoint Test"
    assert data["variants"] == {"A": 0.5, "B": 0.5}
    assert data["primary_metric"] == "conversion_rate"
    assert data["status"] == "draft"

    print("\nGET endpoint retrieved experiment successfully")

    # Verify that an unknown experiment returns 404.
    missing_response = api_client.get(
        f"/experiments/missing_{uuid4().hex}"
    )

    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == (
        "Experiment not found."
    )

    print("Unknown experiment correctly returned 404")



def test_list_experiments_from_database(api_client):
    experiment_id = f"list_api_{uuid4().hex[:8]}"

    response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "List Endpoint Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion_rate",
        },
    )

    assert response.status_code == 201

    list_response = api_client.get("/experiments")

    assert list_response.status_code == 200

    experiments = list_response.json()

    matching = [
        experiment
        for experiment in experiments
        if experiment["experiment_id"] == experiment_id
    ]

    assert len(matching) == 1
    assert matching[0]["name"] == "List Endpoint Test"
    assert matching[0]["status"] == "draft"

    print("\nExperiment listing from PostgreSQL PASSED")



def test_update_experiment_status_in_database(
    api_client,
    db_session,
):
    experiment_id = f"status_api_{uuid4().hex[:8]}"

    create_response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Status Update Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion_rate",
        },
    )

    assert create_response.status_code == 201

    # Change draft -> running.
    response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "running"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "running"

    # Verify the new status is stored in PostgreSQL.
    db_session.expire_all()

    record = db_session.get(
        ExperimentRecord,
        experiment_id,
    )

    assert record.status == "running"

    print("\nDatabase status update PASSED")

    # Attempt an invalid transition.
    invalid_response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "draft"},
    )

    assert invalid_response.status_code == 400
    assert "Cannot transition" in (
        invalid_response.json()["detail"]
    )

    db_session.expire_all()

    record = db_session.get(
        ExperimentRecord,
        experiment_id,
    )

    assert record.status == "running"

    print("Invalid transition correctly rejected")




def test_database_user_assignment(api_client):
    experiment_id = f"assign_api_{uuid4().hex[:8]}"

    # Create an experiment in PostgreSQL.
    response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Assignment API Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion_rate",
        },
    )

    assert response.status_code == 201

    # Start the experiment.
    response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "running"},
    )

    assert response.status_code == 200

    # Assign the same user twice.
    first = api_client.get(
        f"/experiments/{experiment_id}/assign/user_101"
    )

    second = api_client.get(
        f"/experiments/{experiment_id}/assign/user_101"
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["variant"] == second.json()["variant"]
    assert first.json()["variant"] in {"A", "B"}

    print("\nDeterministic assignment PASSED")

    # Pause the experiment.
    response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "paused"},
    )

    assert response.status_code == 200

    # Paused experiments must reject assignments.
    paused_response = api_client.get(
        f"/experiments/{experiment_id}/assign/user_102"
    )

    assert paused_response.status_code == 400
    assert paused_response.json()["detail"] == (
        "Experiment must be running to assign users."
    )

    print("Paused experiment assignment correctly rejected")



def test_assignment_is_persisted(api_client, db_session):
    from sqlalchemy import select, func
    from src.experimentguard.models import AssignmentRecord

    experiment_id = "persistent_assignment_test"

    create_response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Persistent Assignment Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion",
        },
    )
    assert create_response.status_code == 201

    status_response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "running"},
    )
    assert status_response.status_code == 200

    first = api_client.get(
        f"/experiments/{experiment_id}/assign/user_123"
    )
    second = api_client.get(
        f"/experiments/{experiment_id}/assign/user_123"
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["variant"] == second.json()["variant"]

    saved_assignment = db_session.scalar(
        select(AssignmentRecord).where(
            AssignmentRecord.experiment_id == experiment_id,
            AssignmentRecord.user_id == "user_123",
        )
    )

    assert saved_assignment is not None
    assert saved_assignment.variant == first.json()["variant"]

    assignment_count = db_session.scalar(
        select(func.count()).select_from(AssignmentRecord).where(
            AssignmentRecord.experiment_id == experiment_id,
            AssignmentRecord.user_id == "user_123",
        )
    )

    assert assignment_count == 1


def test_assignment_survives_new_database_session(api_client, db_session):
    from sqlalchemy import select
    from src.experimentguard.models import AssignmentRecord

    experiment_id = "assignment_session_test"

    response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Assignment Session Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion",
        },
    )
    assert response.status_code == 201

    response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "running"},
    )
    assert response.status_code == 200

    first = api_client.get(
        f"/experiments/{experiment_id}/assign/user_456"
    )
    assert first.status_code == 200

    # Expire cached objects so the next query reads fresh database state.
    db_session.expire_all()

    saved = db_session.scalar(
        select(AssignmentRecord).where(
            AssignmentRecord.experiment_id == experiment_id,
            AssignmentRecord.user_id == "user_456",
        )
    )

    assert saved is not None
    assert saved.variant == first.json()["variant"]

    second = api_client.get(
        f"/experiments/{experiment_id}/assign/user_456"
    )

    assert second.status_code == 200
    assert second.json()["variant"] == saved.variant



def test_assignment_visible_in_separate_session(api_client, db_session):
    from sqlalchemy import select
    from sqlalchemy.orm import Session
    from src.experimentguard.models import AssignmentRecord

    experiment_id = "separate_session_test"

    response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Separate Session Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion",
        },
    )
    assert response.status_code == 201

    response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "running"},
    )
    assert response.status_code == 200

    response = api_client.get(
        f"/experiments/{experiment_id}/assign/user_789"
    )
    assert response.status_code == 200

    expected_variant = response.json()["variant"]

    # Create another session on the same test transaction.
    with Session(
        bind=db_session.connection(),
        join_transaction_mode="create_savepoint",
    ) as second_session:
        saved = second_session.scalar(
            select(AssignmentRecord).where(
                AssignmentRecord.experiment_id == experiment_id,
                AssignmentRecord.user_id == "user_789",
            )
        )

        assert saved is not None
        assert saved.variant == expected_variant

def test_event_is_persisted(api_client, db_session):
    from sqlalchemy import select

    from src.experimentguard.event_repository import EventRepository
    from src.experimentguard.models import EventRecord

    experiment_id = "event_persistence_test"
    user_id = "event_user_123"

    # Create an experiment.
    response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Event Persistence Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion",
        },
    )
    assert response.status_code == 201

    # Start the experiment.
    response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "running"},
    )
    assert response.status_code == 200

    # Assign the user to a variant.
    response = api_client.get(
        f"/experiments/{experiment_id}/assign/{user_id}"
    )
    assert response.status_code == 200

    # Record a conversion event.
    repository = EventRepository(db_session)

    event = repository.create_event(
        event_id="conversion_event_001",
        experiment_id=experiment_id,
        user_id=user_id,
        event_type="conversion",
        properties={"purchase_amount": 49.99},
    )

    assert event.event_id == "conversion_event_001"

    # Read the event from PostgreSQL.
    saved = db_session.scalar(
        select(EventRecord).where(
            EventRecord.event_id == "conversion_event_001"
        )
    )

    assert saved is not None
    assert saved.experiment_id == experiment_id
    assert saved.user_id == user_id
    assert saved.event_type == "conversion"
    assert saved.properties["purchase_amount"] == 49.99


def test_event_api_creates_conversion(api_client, db_session):
    from src.experimentguard.models import EventRecord

    experiment_id = "event_api_test"
    user_id = "event_api_user_123"
    event_id = "event_api_conversion_001"

    # Create experiment.
    response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Event API Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion",
        },
    )
    assert response.status_code == 201

    # Start experiment.
    response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "running"},
    )
    assert response.status_code == 200

    # Assign user.
    response = api_client.get(
        f"/experiments/{experiment_id}/assign/{user_id}"
    )
    assert response.status_code == 200

    # Submit conversion event through FastAPI.
    response = api_client.post(
        "/events",
        json={
            "event_id": event_id,
            "experiment_id": experiment_id,
            "user_id": user_id,
            "event_type": "conversion",
            "properties": {"purchase_amount": 99.99},
        },
    )

    assert response.status_code == 201
    assert response.json()["event_id"] == event_id
    assert response.json()["event_type"] == "conversion"

    # Verify PostgreSQL persistence.
    saved = db_session.get(EventRecord, event_id)

    assert saved is not None
    assert saved.experiment_id == experiment_id
    assert saved.user_id == user_id
    assert saved.properties["purchase_amount"] == 99.99

    # Reject an unsupported event type.
    invalid = api_client.post(
        "/events",
        json={
            "event_id": "invalid_event_001",
            "experiment_id": experiment_id,
            "user_id": user_id,
            "event_type": "unknown_event",
        },
    )

    assert invalid.status_code == 400

    # Reject events from users without an assignment.
    unassigned = api_client.post(
        "/events",
        json={
            "event_id": "unassigned_event_001",
            "experiment_id": experiment_id,
            "user_id": "never_assigned_user",
            "event_type": "click",
        },
    )

    assert unassigned.status_code == 400


def test_duplicate_event_is_rejected(api_client, db_session):
    from sqlalchemy import select, func
    from src.experimentguard.models import EventRecord

    experiment_id = "duplicate_event_test"
    user_id = "duplicate_user_123"
    event_id = "duplicate_conversion_001"

    # Create experiment.
    response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Duplicate Event Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion",
        },
    )
    assert response.status_code == 201

    # Start experiment.
    response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "running"},
    )
    assert response.status_code == 200

    # Assign user.
    response = api_client.get(
        f"/experiments/{experiment_id}/assign/{user_id}"
    )
    assert response.status_code == 200

    payload = {
        "event_id": event_id,
        "experiment_id": experiment_id,
        "user_id": user_id,
        "event_type": "conversion",
        "properties": {"purchase_amount": 49.99},
    }

    # First submission succeeds.
    first = api_client.post("/events", json=payload)
    assert first.status_code == 201

    # Second submission with the same event ID is rejected.
    second = api_client.post("/events", json=payload)
    assert second.status_code == 400
    assert "Event ID already exists" in second.json()["detail"]

    # Verify that PostgreSQL contains exactly one record.
    event_count = db_session.scalar(
        select(func.count())
        .select_from(EventRecord)
        .where(EventRecord.event_id == event_id)
    )

    assert event_count == 1


def test_event_integrity_error_handling(api_client, db_session, monkeypatch):
    from sqlalchemy.exc import IntegrityError

    from src.experimentguard.event_repository import EventRepository

    experiment_id = "integrity_error_test"
    user_id = "integrity_user_123"

    response = api_client.post(
        "/experiments",
        json={
            "experiment_id": experiment_id,
            "name": "Integrity Error Test",
            "variants": {"A": 0.5, "B": 0.5},
            "primary_metric": "conversion",
        },
    )
    assert response.status_code == 201

    response = api_client.patch(
        f"/experiments/{experiment_id}/status",
        json={"status": "running"},
    )
    assert response.status_code == 200

    response = api_client.get(
        f"/experiments/{experiment_id}/assign/{user_id}"
    )
    assert response.status_code == 200

    # Simulate a database integrity error during insertion.
    original_flush = db_session.flush

    def simulate_integrity_error(*args, **kwargs):
        raise IntegrityError(
            statement="INSERT INTO events ...",
            params={},
            orig=Exception("Simulated database conflict"),
        )

    monkeypatch.setattr(db_session, "flush", simulate_integrity_error)

    repository = EventRepository(db_session)

    with pytest.raises(IntegrityError):
        repository.create_event(
            event_id="integrity_event_001",
            experiment_id=experiment_id,
            user_id=user_id,
            event_type="conversion",
        )

    monkeypatch.setattr(db_session, "flush", original_flush)