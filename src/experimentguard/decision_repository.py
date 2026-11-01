
from sqlalchemy.orm import Session

from .decision import evaluate_experiment_decision
from .health_repository import HealthRepository
from .metrics_repository import MetricsRepository
from .statistics_repository import StatisticsRepository
from sqlalchemy import select, func
from .models import ExperimentRecord, AssignmentRecord

class DecisionRepository:

    def __init__(self, session: Session):
        self.health_repository = HealthRepository(session)
        self.metrics_repository = MetricsRepository(session)
        self.statistics_repository = StatisticsRepository(session)

    def get_decision(
        self,
        experiment_id: str,
        alpha: float = 0.05,
    ) -> dict:

        health = self.health_repository.get_assignment_health(
            experiment_id
        )

        experiment = self.health_repository.session.get(
        ExperimentRecord,
        experiment_id,
    )

        total_users = self.health_repository.session.scalar(
            select(func.count(AssignmentRecord.id)).where(
                AssignmentRecord.experiment_id == experiment_id
            )
        )

        health_status = health["status"]

        if health_status != "healthy":
            return {
                "experiment_id": experiment_id,
                **evaluate_experiment_decision(
                    health_status=health_status
                ),
            }

        metrics = self.metrics_repository.get_conversion_rates(
            experiment_id
        )

        statistics = self.statistics_repository.get_significance(
            experiment_id,
            alpha=alpha,
        )

        decision = evaluate_experiment_decision(
            health_status=health_status,
            p_value=statistics["p_value"],
            conversion_rate_a=metrics["A"]["conversion_rate"],
            conversion_rate_b=metrics["B"]["conversion_rate"],
            alpha=alpha,
            total_users=total_users,
            planned_sample_size=experiment.planned_sample_size,
        )

        return {
            "experiment_id": experiment_id,
            **decision,
        }
