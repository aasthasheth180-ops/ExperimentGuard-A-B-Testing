from dataclasses import dataclass, field
from math import isclose, isfinite
from types import MappingProxyType
from typing import Mapping


ALLOWED_STATUSES = {"draft", "running", "paused", "completed"}

@dataclass(frozen=True)
class Experiment:
    experiment_id: str
    name: str
    variants: Mapping[str, float]
    primary_metric: str
    status: str = "draft"
    planned_sample_size: int | None = None
    hypothesis: str | None = None

    def __post_init__(self):
        if not isinstance(self.experiment_id, str) or not self.experiment_id.strip():
            raise ValueError("Experiment ID cannot be empty.")

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Experiment name cannot be empty.")

        if self.hypothesis is not None:
            if not isinstance(self.hypothesis, str):
                raise ValueError("Hypothesis must be a string.")

            if len(self.hypothesis) > 5000:
                raise ValueError("Hypothesis cannot exceed 5000 characters.")

        if not isinstance(self.primary_metric, str) or not self.primary_metric.strip():
            raise ValueError("Primary metric cannot be empty.")

        if self.planned_sample_size is not None:
                if (
                    isinstance(self.planned_sample_size, bool)
                    or not isinstance(self.planned_sample_size, int)
                    or self.planned_sample_size <= 0
                ):
                    raise ValueError(
                        "Planned sample size must be a positive integer."
                        )

        if len(self.variants) < 2:
            raise ValueError("An experiment must have at least two variants.")

        if any(
            not isinstance(weight, (int, float))
            or isinstance(weight, bool)
            or not isfinite(weight)
            or weight < 0
            for weight in self.variants.values()
        ):
            raise ValueError("Variant weights must be finite, non-negative numbers.")

        if not isclose(
            sum(self.variants.values()),
            1.0,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise ValueError("Variant weights must sum to 1.0.")

        object.__setattr__(
            self,
            "variants",
            MappingProxyType(dict(self.variants)),
        )