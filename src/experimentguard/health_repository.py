from sqlalchemy.orm import Session

from src.experimentguard.health import evaluate_assignment_health
from src.experimentguard.metrics_repository import MetricsRepository
from src.experimentguard.models import ExperimentRecord


class HealthRepository:

    def __init__(self, session: Session):
        self.session = session
        self.metrics_repository = MetricsRepository(session)

    def get_assignment_health(
        self,
        experiment_id: str,
    ) -> dict:

        experiment = self.session.get(
            ExperimentRecord,
            experiment_id,
        )

        if experiment is None:
            raise ValueError("Experiment not found.")

        expected_weights = experiment.variants

        assignment_rows = (
        self.metrics_repository.get_assigned_users(
            experiment_id
        )
    )

        observed_counts = {
        variant: 0
        for variant in expected_weights
        }

        observed_counts.update(dict(assignment_rows))

        return evaluate_assignment_health(
            observed=observed_counts,
            expected_weights=expected_weights,
        )