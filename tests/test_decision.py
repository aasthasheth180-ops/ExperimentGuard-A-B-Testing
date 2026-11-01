
import pytest

from src.experimentguard.decision import (
    DecisionOutcome,
    evaluate_health_decision,
    evaluate_statistical_decision,
    evaluate_experiment_decision,
    evaluate_stopping_rule
)


def test_healthy_experiment_proceeds():
    result = evaluate_health_decision("healthy")

    assert result is None


def test_insufficient_data_continues_experiment():
    result = evaluate_health_decision("insufficient_data")

    assert result == DecisionOutcome.CONTINUE_EXPERIMENT


@pytest.mark.parametrize(
    "health_status",
    ["warning", "invalid", "unsupported"],
)
def test_unhealthy_experiment_requires_investigation(health_status):
    result = evaluate_health_decision(health_status)

    assert result == DecisionOutcome.INVESTIGATE


def test_unknown_health_status_raises_error():
    with pytest.raises(ValueError, match="Unknown experiment health status"):
        evaluate_health_decision("unknown")



def test_significant_improvement_recommends_b():
    result = evaluate_statistical_decision(
        p_value=0.01,
        conversion_rate_a=0.08,
        conversion_rate_b=0.092,
    )

    assert result == DecisionOutcome.ROLLOUT_B


def test_significant_decline_recommends_a():
    result = evaluate_statistical_decision(
        p_value=0.01,
        conversion_rate_a=0.092,
        conversion_rate_b=0.08,
    )

    assert result == DecisionOutcome.KEEP_A


def test_not_significant_continues_experiment():
    result = evaluate_statistical_decision(
        p_value=0.20,
        conversion_rate_a=0.08,
        conversion_rate_b=0.092,
    )

    assert result == DecisionOutcome.CONTINUE_EXPERIMENT


def test_p_value_equal_to_alpha_is_not_significant():
    result = evaluate_statistical_decision(
        p_value=0.05,
        conversion_rate_a=0.08,
        conversion_rate_b=0.092,
    )

    assert result == DecisionOutcome.CONTINUE_EXPERIMENT


@pytest.mark.parametrize("p_value", [-0.1, 1.1, float("nan"), float("inf")])
def test_invalid_p_value_raises_error(p_value):
    with pytest.raises(ValueError, match="P-value"):
        evaluate_statistical_decision(p_value, 0.08, 0.092)


@pytest.mark.parametrize("rate", [-0.1, 1.1, float("nan"), float("inf")])
def test_invalid_conversion_rate_raises_error(rate):
    with pytest.raises(ValueError, match="Conversion rates"):
        evaluate_statistical_decision(0.01, 0.08, rate)


def test_equal_conversion_rates_continue_experiment():
    result = evaluate_statistical_decision(
        p_value=0.01,
        conversion_rate_a=0.08,
        conversion_rate_b=0.08,
    )

    assert result == DecisionOutcome.CONTINUE_EXPERIMENT



def test_healthy_significant_improvement():
    result = evaluate_experiment_decision(
        health_status="healthy",
        p_value=0.01,
        conversion_rate_a=0.08,
        conversion_rate_b=0.092,
        total_users=2000,
        planned_sample_size=2000,
    )

    assert result["decision"] == "rollout_b"
    assert result["health_status"] == "healthy"


def test_healthy_significant_decline():
    result = evaluate_experiment_decision(
        health_status="healthy",
        p_value=0.01,
        conversion_rate_a=0.092,
        conversion_rate_b=0.08,
        total_users=2000,
        planned_sample_size=2000,
    )

    assert result["decision"] == "keep_a"



def test_healthy_inconclusive_experiment():
    result = evaluate_experiment_decision(
        health_status="healthy",
        p_value=0.25,
        conversion_rate_a=0.08,
        conversion_rate_b=0.092,
    )

    assert result["decision"] == "continue_experiment"


def test_srm_warning_blocks_rollout():
    result = evaluate_experiment_decision(
        health_status="warning",
        p_value=0.001,
        conversion_rate_a=0.08,
        conversion_rate_b=0.15,
    )

    assert result["decision"] == "investigate"


def test_invalid_assignments_block_rollout():
    result = evaluate_experiment_decision(
        health_status="invalid",
        p_value=0.001,
        conversion_rate_a=0.08,
        conversion_rate_b=0.15,
    )

    assert result["decision"] == "investigate"


def test_insufficient_data_blocks_rollout():
    result = evaluate_experiment_decision(
        health_status="insufficient_data"
    )

    assert result["decision"] == "continue_experiment"


def test_healthy_experiment_requires_statistics():
    with pytest.raises(
        ValueError,
        match="Statistical results are required",
    ):
        evaluate_experiment_decision(
            health_status="healthy"
        )


def test_unsupported_experiment_requires_investigation():
    result = evaluate_experiment_decision(
        health_status="unsupported"
    )

    assert result["decision"] == "investigate"



def test_stopping_rule_sample_size_not_reached():
    result = evaluate_stopping_rule(
        total_users=500,
        planned_sample_size=2000,
    )

    assert result is False


def test_stopping_rule_sample_size_reached():
    result = evaluate_stopping_rule(
        total_users=2000,
        planned_sample_size=2000,
    )

    assert result is True


def test_stopping_rule_sample_size_exceeded():
    result = evaluate_stopping_rule(
        total_users=2500,
        planned_sample_size=2000,
    )

    assert result is True


@pytest.mark.parametrize("total_users", [-1, 2.5, True])
def test_stopping_rule_invalid_total_users(total_users):
    with pytest.raises(ValueError, match="Total users"):
        evaluate_stopping_rule(
            total_users=total_users,
            planned_sample_size=2000,
        )


@pytest.mark.parametrize("planned_sample_size", [0, -10, 2.5, True])
def test_stopping_rule_invalid_planned_sample_size(planned_sample_size):
    with pytest.raises(ValueError, match="Planned sample size"):
        evaluate_stopping_rule(
            total_users=500,
            planned_sample_size=planned_sample_size,
        )




def test_significant_result_before_sample_target():
    result = evaluate_experiment_decision(
        health_status="healthy",
        p_value=0.01,
        conversion_rate_a=0.08,
        conversion_rate_b=0.092,
        total_users=500,
        planned_sample_size=2000,
    )

    assert result["decision"] == "continue_experiment"
    assert result["reason"] == "Planned sample size has not been reached."


def test_missing_sample_size_prevents_rollout():
    result = evaluate_experiment_decision(
        health_status="healthy",
        p_value=0.01,
        conversion_rate_a=0.08,
        conversion_rate_b=0.092,
    )

    assert result["decision"] == "continue_experiment"
    assert result["reason"] == "Planned sample size or total users is unavailable."
