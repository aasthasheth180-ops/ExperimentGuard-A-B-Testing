
from enum import Enum


class DecisionOutcome(str, Enum):
    ROLLOUT_B = "rollout_b"
    KEEP_A = "keep_a"
    CONTINUE_EXPERIMENT = "continue_experiment"
    INVESTIGATE = "investigate"


def evaluate_health_decision(health_status: str) -> DecisionOutcome | None:
    if health_status == "healthy":
        return None

    if health_status == "insufficient_data":
        return DecisionOutcome.CONTINUE_EXPERIMENT

    if health_status in {"warning", "invalid", "unsupported"}:
        return DecisionOutcome.INVESTIGATE

    raise ValueError(f"Unknown experiment health status: {health_status}")




import math


def evaluate_statistical_decision(
    p_value: float,
    conversion_rate_a: float,
    conversion_rate_b: float,
    alpha: float = 0.05,
) -> DecisionOutcome:
    if not math.isfinite(p_value) or not 0 <= p_value <= 1:
        raise ValueError("P-value must be between 0 and 1.")

    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1.")

    for rate in (conversion_rate_a, conversion_rate_b):
        if not math.isfinite(rate) or not 0 <= rate <= 1:
            raise ValueError("Conversion rates must be between 0 and 1.")

    if p_value >= alpha:
        return DecisionOutcome.CONTINUE_EXPERIMENT

    if conversion_rate_b > conversion_rate_a:
        return DecisionOutcome.ROLLOUT_B

    if conversion_rate_a > conversion_rate_b:
        return DecisionOutcome.KEEP_A

    return DecisionOutcome.CONTINUE_EXPERIMENT



def evaluate_experiment_decision(
    health_status: str,
    p_value: float | None = None,
    conversion_rate_a: float | None = None,
    conversion_rate_b: float | None = None,
    alpha: float = 0.05,
    total_users: int | None = None,
    planned_sample_size: int | None = None,
) -> dict:
    health_decision = evaluate_health_decision(health_status)

    if health_decision is not None:
        return {
            "decision": health_decision.value,
            "health_status": health_status,
            "reason": "Experiment health prevents statistical evaluation.",
        }

    if (
        p_value is None
        or conversion_rate_a is None
        or conversion_rate_b is None
    ):
        raise ValueError(
            "Statistical results are required for healthy experiments."
        )

    statistical_decision = evaluate_statistical_decision(
        p_value=p_value,
        conversion_rate_a=conversion_rate_a,
        conversion_rate_b=conversion_rate_b,
        alpha=alpha,
    )

    if total_users is None or planned_sample_size is None:
        return {
            "decision": DecisionOutcome.CONTINUE_EXPERIMENT.value,
            "health_status": health_status,
            "reason": "Planned sample size or total users is unavailable.",
        }

    sample_size_reached = evaluate_stopping_rule(
        total_users=total_users,
        planned_sample_size=planned_sample_size,
    )

    if not sample_size_reached:
        return {
            "decision": DecisionOutcome.CONTINUE_EXPERIMENT.value,
            "health_status": health_status,
            "reason": "Planned sample size has not been reached.",
        }

    return {
        "decision": statistical_decision.value,
        "health_status": health_status,
        "reason": "Planned sample size reached; statistical result evaluated.",
    }



def evaluate_stopping_rule(
    total_users: int,
    planned_sample_size: int,
) -> bool:
    if isinstance(total_users, bool) or not isinstance(total_users, int):
        raise ValueError("Total users must be a non-negative integer.")

    if total_users < 0:
        raise ValueError("Total users must be a non-negative integer.")

    if isinstance(planned_sample_size, bool) or not isinstance(planned_sample_size, int):
        raise ValueError("Planned sample size must be a positive integer.")

    if planned_sample_size <= 0:
        raise ValueError("Planned sample size must be a positive integer.")

    return total_users >= planned_sample_size
