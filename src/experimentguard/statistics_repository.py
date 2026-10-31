from sqlalchemy.orm import Session

from .metrics_repository import MetricsRepository
from .statistics import evaluate_significance


class StatisticsRepository:

    def __init__(self, session: Session):
        self.metrics_repository = MetricsRepository(session)

    def get_significance(
        self,
        experiment_id: str,
        alpha: float = 0.05,
    ) -> dict:

        metrics = self.metrics_repository.get_conversion_rates(
            experiment_id
        )

        if "A" not in metrics or "B" not in metrics:
            raise ValueError(
                "Experiment must contain variants A and B."
            )

        variant_a = metrics["A"]
        variant_b = metrics["B"]

        return evaluate_significance(
            conversions_a=variant_a["converted_users"],
            users_a=variant_a["assigned_users"],
            conversions_b=variant_b["converted_users"],
            users_b=variant_b["assigned_users"],
            alpha=alpha,
        )