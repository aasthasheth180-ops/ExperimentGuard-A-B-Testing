from dataclasses import dataclass, field
from math import isclose, isfinite


ALLOWED_STATUSES = {"draft", "running", "paused", "completed"}


@dataclass
class Experiment:
    experiment_id: str
    name: str
    variants: dict[str, float]
    primary_metric: str
    status: str = "draft"

    def __post_init__(self):
        if not self.experiment_id.strip():
            raise ValueError("Experiment ID cannot be empty.")

        if not self.name.strip():
            raise ValueError("Experiment name cannot be empty.")

        if not self.primary_metric.strip():
            raise ValueError("Primary metric cannot be empty.")

        if self.status not in ALLOWED_STATUSES:
            raise ValueError("Invalid experiment status.")

        if len(self.variants) < 2:
            raise ValueError("At least two variants are required.")

        if any(
            not isinstance(weight, (int, float))
            or not isfinite(weight)
            or weight < 0
            for weight in self.variants.values()
        ):
            raise ValueError("Variant weights must be finite and non-negative.")

        if not isclose(sum(self.variants.values()), 1.0, abs_tol=1e-9):
            raise ValueError("Variant weights must sum to 1.0.")