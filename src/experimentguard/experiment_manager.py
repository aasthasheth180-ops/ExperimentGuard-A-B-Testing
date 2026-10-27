from dataclasses import replace

from .experiment import Experiment, ALLOWED_STATUSES


ALLOWED_TRANSITIONS = {
    "draft": {"running"},
    "running": {"paused", "completed"},
    "paused": {"running", "completed"},
    "completed": set(),
}


class ExperimentManager:
    """Manage experiment lifecycle and configuration in memory."""

    def __init__(self):
        self.experiments: dict[str, Experiment] = {}

    def create_experiment(self, experiment: Experiment) -> Experiment:
        if experiment.experiment_id in self.experiments:
            raise ValueError("Experiment ID already exists.")

        if experiment.status != "draft":
            raise ValueError("New experiments must start in draft status.")

        self.experiments[experiment.experiment_id] = experiment
        return experiment

    def get_experiment(self, experiment_id: str) -> Experiment:
        if experiment_id not in self.experiments:
            raise KeyError("Experiment not found.")

        return self.experiments[experiment_id]

    def list_experiments(self) -> list[Experiment]:
        return list(self.experiments.values())

    def update_status(
        self, experiment_id: str, new_status: str
    ) -> Experiment:
        if new_status not in ALLOWED_STATUSES:
            raise ValueError("Invalid experiment status.")

        experiment = self.get_experiment(experiment_id)

        if new_status not in ALLOWED_TRANSITIONS[experiment.status]:
            raise ValueError(
                f"Cannot transition from {experiment.status} to {new_status}."
            )

        updated_experiment = replace(
            experiment,
            status=new_status,
        )

        self.experiments[experiment_id] = updated_experiment
        return updated_experiment