from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import AssignmentRecord, EventRecord, ExperimentRecord


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_event(
        self,
        event_id: str,
        experiment_id: str,
        user_id: str,
        event_type: str,
        properties: dict | None = None,
    ) -> EventRecord:

        if not event_id or not event_id.strip():
            raise ValueError("Event ID cannot be empty.")


        existing_event = self.session.get(
            EventRecord,
            event_id,
        )

        if existing_event is not None:
            raise ValueError("Event ID already exists.")

        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty.")

        if event_type not in {"exposure", "click", "conversion"}:
            raise ValueError("Invalid event type.")

        experiment = self.session.get(
            ExperimentRecord,
            experiment_id,
        )

        if experiment is None:
            raise KeyError("Experiment not found.")

        if experiment.status != "running":
            raise ValueError("Experiment must be running.")

        assignment = self.session.scalar(
            select(AssignmentRecord).where(
                AssignmentRecord.experiment_id == experiment_id,
                AssignmentRecord.user_id == user_id,
            )
        )

        if assignment is None:
            raise ValueError("User has not been assigned to this experiment.")

        event = EventRecord(
            event_id=event_id,
            experiment_id=experiment_id,
            user_id=user_id,
            event_type=event_type,
            event_timestamp=datetime.now(timezone.utc),
            properties=properties if properties is not None else {},
        )

        try:
            with self.session.begin_nested():
                self.session.add(event)
                self.session.flush()

        except IntegrityError:
            self.session.rollback()

            existing = self.session.get(
                EventRecord,
                event_id,
            )

            if existing is not None:
                raise ValueError("Event ID already exists.")

            raise

        self.session.commit()
        return event
