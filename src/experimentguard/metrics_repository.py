from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .models import AssignmentRecord, EventRecord
from .models import ExperimentRecord

class MetricsRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_assigned_users(self, experiment_id: str):
        statement = (
            select(
                AssignmentRecord.variant,
                func.count(AssignmentRecord.user_id).label("assigned_users"),
            )
            .where(AssignmentRecord.experiment_id == experiment_id)
            .group_by(AssignmentRecord.variant)
        )

        return self.session.execute(statement).all()


    def get_converted_users(self, experiment_id: str):
            statement = (
                select(
                    AssignmentRecord.variant,
                    func.count(
                        func.distinct(EventRecord.user_id)
                    ).label("converted_users"),
                )
                .join(
                    EventRecord,
                    (AssignmentRecord.experiment_id == EventRecord.experiment_id)
                    & (AssignmentRecord.user_id == EventRecord.user_id),
                )
                .where(
                    AssignmentRecord.experiment_id == experiment_id,
                    EventRecord.event_type == "conversion",
                )
                .group_by(AssignmentRecord.variant)
            )

            return self.session.execute(statement).all()

    def get_conversion_rates(self, experiment_id: str):
        assigned_rows = self.get_assigned_users(experiment_id)
        converted_rows = self.get_converted_users(experiment_id)

        converted_by_variant = {
            variant: count
            for variant, count in converted_rows
        }

        experiment = self.session.get(ExperimentRecord, experiment_id)

        results = {}

        if experiment is not None:
            for variant in experiment.variants:
                results[variant] = {
                    "assigned_users": 0,
                    "converted_users": 0,
                    "conversion_rate": 0.0,
                }

        for variant, assigned_count in assigned_rows:
            converted_count = converted_by_variant.get(variant, 0)

            conversion_rate = (
                converted_count / assigned_count
                if assigned_count > 0
                else 0.0
            )

            results[variant] = {
                "assigned_users": assigned_count,
                "converted_users": converted_count,
                "conversion_rate": conversion_rate,
            }

        return results


    def get_relative_lift(self, experiment_id: str):
        rates = self.get_conversion_rates(experiment_id)

        if "A" not in rates or "B" not in rates:
            return None

        rate_a = rates["A"]["conversion_rate"]
        rate_b = rates["B"]["conversion_rate"]

        if rate_a == 0:
            return None

        return ((rate_b - rate_a) / rate_a) * 100