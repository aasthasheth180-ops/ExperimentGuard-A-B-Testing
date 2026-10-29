import pytest

from sqlalchemy import text
from tests.conftest import test_engine
from uuid import uuid4
from src.experimentguard.models import AssignmentRecord, ExperimentRecord
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.experimentguard.event_repository import EventRepository
from src.experimentguard.models import EventRecord


def test_independent_database_connections():
    with test_engine.connect() as connection_one:
        with test_engine.connect() as connection_two:
            first_pid = connection_one.execute(
                text("SELECT pg_backend_pid()")
            ).scalar_one()

            second_pid = connection_two.execute(
                text("SELECT pg_backend_pid()")
            ).scalar_one()

            assert first_pid != second_pid


@pytest.fixture
def concurrency_experiment():
    experiment_id = f"concurrency_{uuid4().hex[:12]}"
    user_id = "concurrent_user_123"

    with test_engine.begin() as connection:
        from sqlalchemy.orm import Session

        with Session(bind=connection) as session:
            session.add(
                ExperimentRecord(
                    experiment_id=experiment_id,
                    name="Concurrent Event Test",
                    variants={"A": 0.5, "B": 0.5},
                    primary_metric="conversion",
                    status="running",
                )
            )

            session.flush()

            session.add(
                AssignmentRecord(
                    experiment_id=experiment_id,
                    user_id=user_id,
                    variant="A",
                )
            )

            session.flush()

    try:
        yield experiment_id, user_id
    finally:
        from sqlalchemy import delete
        from src.experimentguard.models import EventRecord

        with test_engine.begin() as connection:
            connection.execute(
                delete(EventRecord).where(
                    EventRecord.experiment_id == experiment_id
                )
            )
            connection.execute(
                delete(AssignmentRecord).where(
                    AssignmentRecord.experiment_id == experiment_id
                )
            )
            connection.execute(
                delete(ExperimentRecord).where(
                    ExperimentRecord.experiment_id == experiment_id
                )
            )


def test_concurrent_duplicate_events(concurrency_experiment):
    experiment_id, user_id = concurrency_experiment
    event_id = f"concurrent_event_{uuid4().hex[:12]}"

    barrier = Barrier(2)

    def submit_event():
        # Each worker gets its own database session.
        with Session(bind=test_engine) as session:
            repository = EventRepository(session)

            barrier.wait(timeout=10)

            try:
                repository.create_event(
                    event_id=event_id,
                    experiment_id=experiment_id,
                    user_id=user_id,
                    event_type="conversion",
                    properties={"purchase_amount": 49.99},
                )
                return "created"

            except ValueError as exc:
                if str(exc) == "Event ID already exists.":
                    return "duplicate"
                raise

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(submit_event)
            for _ in range(2)
        ]

        results = [
            future.result(timeout=20)
            for future in futures
        ]

    assert sorted(results) == ["created", "duplicate"]

    # Verify the actual database record count.
    with Session(bind=test_engine) as session:
        count = session.scalar(
            select(func.count())
            .select_from(EventRecord)
            .where(EventRecord.event_id == event_id)
        )

    assert count == 1