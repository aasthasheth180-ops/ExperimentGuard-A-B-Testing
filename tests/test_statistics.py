import pytest

from src.experimentguard.statistics import (
    calculate_pooled_proportion,
    calculate_z_statistic,
    calculate_p_value,
    calculate_confidence_interval,
    evaluate_significance,
    check_sample_size,
)


def test_pooled_proportion():
    result = calculate_pooled_proportion(
        conversions_a=80,
        users_a=1000,
        conversions_b=100,
        users_b=1000,
    )

    assert result == pytest.approx(0.09)


def test_z_statistic():
    result = calculate_z_statistic(
        conversions_a=80,
        users_a=1000,
        conversions_b=100,
        users_b=1000,
    )

    assert result == pytest.approx(1.5627, abs=0.0001)


def test_z_statistic_invalid_users():
    with pytest.raises(ValueError):
        calculate_z_statistic(
            conversions_a=0,
            users_a=0,
            conversions_b=10,
            users_b=100,
        )



def test_p_value_positive_z():
    result = calculate_p_value(1.562690769794985)

    assert result == pytest.approx(0.1181253465, abs=1e-8)


def test_p_value_negative_z():
    result = calculate_p_value(-1.562690769794985)

    assert result == pytest.approx(0.1181253465, abs=1e-8)


def test_p_value_zero_z():
    result = calculate_p_value(0.0)

    assert result == pytest.approx(1.0)



def test_confidence_interval():
    lower, upper = calculate_confidence_interval(
        conversions_a=80,
        users_a=1000,
        conversions_b=100,
        users_b=1000,
    )

    assert lower == pytest.approx(-0.0051, abs=0.0002)
    assert upper == pytest.approx(0.0451, abs=0.0002)


def test_confidence_interval_equal_rates():
    lower, upper = calculate_confidence_interval(
        conversions_a=100,
        users_a=1000,
        conversions_b=100,
        users_b=1000,
    )

    assert lower < 0
    assert upper > 0
    assert (lower + upper) / 2 == pytest.approx(0.0)


def test_confidence_interval_invalid_users():
    with pytest.raises(ValueError):
        calculate_confidence_interval(
            conversions_a=0,
            users_a=0,
            conversions_b=10,
            users_b=100,
        )



def test_evaluate_significance_not_significant():
    result = evaluate_significance(
        conversions_a=80,
        users_a=1000,
        conversions_b=100,
        users_b=1000,
    )

    assert result["is_significant"] is False
    assert result["p_value"] == pytest.approx(0.1181253465)
    assert result["absolute_difference"] == pytest.approx(0.02)


def test_evaluate_significance_significant():
    result = evaluate_significance(
        conversions_a=80,
        users_a=1000,
        conversions_b=150,
        users_b=1000,
    )

    assert result["is_significant"] is True
    assert result["p_value"] < 0.05
    assert result["absolute_difference"] == pytest.approx(0.07)


def test_evaluate_significance_invalid_alpha():
    with pytest.raises(ValueError):
        evaluate_significance(
            conversions_a=80,
            users_a=1000,
            conversions_b=100,
            users_b=1000,
            alpha=1.5,
        )


def test_evaluate_significance_zero_conversions():
    result = evaluate_significance(
        conversions_a=0,
        users_a=1000,
        conversions_b=0,
        users_b=1000,
    )

    assert result["z_statistic"] is None
    assert result["p_value"] == pytest.approx(1.0)
    assert result["is_significant"] is False
    assert result["absolute_difference"] == pytest.approx(0.0)


def test_evaluate_significance_all_conversions():
    result = evaluate_significance(
        conversions_a=1000,
        users_a=1000,
        conversions_b=1000,
        users_b=1000,
    )

    assert result["z_statistic"] is None
    assert result["p_value"] == pytest.approx(1.0)
    assert result["is_significant"] is False
    assert result["absolute_difference"] == pytest.approx(0.0)


def test_evaluate_significance_invalid_conversions():
    with pytest.raises(ValueError):
        evaluate_significance(
            conversions_a=1100,
            users_a=1000,
            conversions_b=100,
            users_b=1000,
        )


def test_sample_size_sufficient():
    result = check_sample_size(
        conversions_a=80,
        users_a=1000,
        conversions_b=100,
        users_b=1000,
    )

    assert result is True


def test_sample_size_insufficient():
    result = check_sample_size(
        conversions_a=1,
        users_a=5,
        conversions_b=2,
        users_b=5,
    )

    assert result is False


def test_sample_size_zero_conversions():
    result = check_sample_size(
        conversions_a=0,
        users_a=1000,
        conversions_b=0,
        users_b=1000,
    )

    assert result is False


def test_sample_size_invalid_users():
    with pytest.raises(ValueError):
        check_sample_size(
            conversions_a=0,
            users_a=0,
            conversions_b=10,
            users_b=100,
        )


def test_evaluate_significance_sufficient_sample():
    result = evaluate_significance(
        conversions_a=80,
        users_a=1000,
        conversions_b=100,
        users_b=1000,
    )

    assert result["normal_approximation_valid"] is True


def test_evaluate_significance_insufficient_sample():
    result = evaluate_significance(
        conversions_a=1,
        users_a=5,
        conversions_b=2,
        users_b=5,
    )

    assert result["normal_approximation_valid"] is False