from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .assignment import assign_user
from .experiment import Experiment
from .experiment_manager import ExperimentManager
from .models import AssignmentRecord, ExperimentRecord


class ExperimentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, experiment: Experiment) -> Experiment:
        existing = self.session.get(
            ExperimentRecord,
            experiment.experiment_id,
        )

        if existing is not None:
            raise ValueError("Experiment ID already exists.")

        record = ExperimentRecord(
            experiment_id=experiment.experiment_id,
            name=experiment.name,
            variants=dict(experiment.variants),
            primary_metric=experiment.primary_metric,
            status=experiment.status,
        )

        self.session.add(record)
        self.session.commit()

        return experiment

    def get(self, experiment_id: str) -> Experiment:
        record = self.session.get(
            ExperimentRecord,
            experiment_id,
        )

        if record is None:
            raise KeyError("Experiment not found.")

        return self._to_experiment(record)

    def list_all(self) -> list[Experiment]:
        statement = select(ExperimentRecord).order_by(
            ExperimentRecord.experiment_id
        )

        records = self.session.scalars(statement).all()

        return [
            self._to_experiment(record)
            for record in records
        ]


    def update_status(
        self,
        experiment_id: str,
        new_status: str,
    ) -> Experiment:
        record = self.session.get(
            ExperimentRecord,
            experiment_id,
        )

        if record is None:
            raise KeyError("Experiment not found.")

        # Reuse the existing Phase 2 lifecycle validation.
        manager = ExperimentManager()
        manager.experiments[experiment_id] = self._to_experiment(record)

        updated_experiment = manager.update_status(
            experiment_id,
            new_status,
        )

        record.status = updated_experiment.status
        self.session.commit()

        return updated_experiment


    def assign_user(self, experiment_id: str, user_id: str) -> str:
        experiment = self.get(experiment_id)

        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty.")

        if experiment.status != "running":
            raise ValueError("Experiment must be running to assign users.")

        existing = self.session.scalar(
            select(AssignmentRecord).where(
                AssignmentRecord.experiment_id == experiment_id,
                AssignmentRecord.user_id == user_id,
            )
        )

        if existing is not None:
            return existing.variant

        variant = assign_user(experiment, user_id)

        record = AssignmentRecord(
            experiment_id=experiment_id,
            user_id=user_id,
            variant=variant,
        )

        try:
            with self.session.begin_nested():
                self.session.add(record)
                self.session.flush()

        except IntegrityError:
            existing = self.session.scalar(
                select(AssignmentRecord).where(
                    AssignmentRecord.experiment_id == experiment_id,
                    AssignmentRecord.user_id == user_id,
                )
            )

            if existing is None:
                self.session.rollback()
                raise

            self.session.commit()
            return existing.variant

        self.session.commit()
        return variant



    @staticmethod
    def _to_experiment(record: ExperimentRecord) -> Experiment:
        return Experiment(
            experiment_id=record.experiment_id,
            name=record.name,
            variants=record.variants,
            primary_metric=record.primary_metric,
            status=record.status,
        )
