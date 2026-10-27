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

    def __post_init__(self):
        if not isinstance(self.experiment_id, str) or not self.experiment_id.strip():
            raise ValueError("Experiment ID cannot be empty.")

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Experiment name cannot be empty.")

        if not isinstance(self.primary_metric, str) or not self.primary_metric.strip():
            raise ValueError("Primary metric cannot be empty.")

        if self.status not in ALLOWED_STATUSES:
            raise ValueError("Invalid experiment status.")

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