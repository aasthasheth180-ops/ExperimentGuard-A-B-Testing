import pytest

from src.experimentguard.health import (
    calculate_srm_chi_square,
    calculate_srm_p_value,
    evaluate_srm,
    validate_assignment_distribution,
    evaluate_assignment_health,
    check_srm_sample_size,
)


def test_srm_balanced_assignment():
    result = calculate_srm_chi_square(
        observed={"A": 5000, "B": 5000},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result == pytest.approx(0.0)


def test_srm_unbalanced_assignment():
    result = calculate_srm_chi_square(
        observed={"A": 7000, "B": 3000},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result == pytest.approx(1600.0)


def test_srm_invalid_weights():
    with pytest.raises(ValueError, match="sum to 1"):
        calculate_srm_chi_square(
            observed={"A": 500, "B": 500},
            expected_weights={"A": 0.6, "B": 0.6},
        )


def test_srm_p_value_balanced():
    result = calculate_srm_p_value(0.0)

    assert result == pytest.approx(1.0)


def test_srm_p_value_unbalanced():
    result = calculate_srm_p_value(10.0)

    assert result == pytest.approx(0.0015654, abs=1e-7)


def test_srm_p_value_extreme_mismatch():
    result = calculate_srm_p_value(1600.0)

    assert result < 0.001


def test_srm_p_value_invalid_chi_square():
    with pytest.raises(ValueError):
        calculate_srm_p_value(-1.0)



def test_evaluate_srm_balanced():
    result = evaluate_srm(
        observed={"A": 5000, "B": 5000},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["total_users"] == 10000
    assert result["chi_square"] == pytest.approx(0.0)
    assert result["p_value"] == pytest.approx(1.0)
    assert result["has_srm"] is False


def test_evaluate_srm_mismatch():
    result = evaluate_srm(
        observed={"A": 7000, "B": 3000},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["chi_square"] == pytest.approx(1600.0)
    assert result["p_value"] < 0.001
    assert result["has_srm"] is True


def test_evaluate_srm_invalid_alpha():
    with pytest.raises(ValueError, match="Alpha"):
        evaluate_srm(
            observed={"A": 500, "B": 500},
            expected_weights={"A": 0.5, "B": 0.5},
            alpha=1.5,
        )


def test_evaluate_srm_three_variants():
    with pytest.raises(ValueError, match="exactly two variants"):
        evaluate_srm(
            observed={"A": 300, "B": 300, "C": 400},
            expected_weights={"A": 0.3, "B": 0.3, "C": 0.4},
        )


def test_assignment_distribution_valid():
    result = validate_assignment_distribution(
        observed={"A": 500, "B": 500},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["is_valid"] is True
    assert result["total_users"] == 1000
    assert result["issues"] == []


def test_assignment_distribution_missing_variant():
    result = validate_assignment_distribution(
        observed={"A": 1000},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["is_valid"] is False
    assert result["missing_variants"] == ["B"]


def test_assignment_distribution_unexpected_variant():
    result = validate_assignment_distribution(
        observed={"A": 500, "B": 500, "C": 100},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["is_valid"] is False
    assert result["unexpected_variants"] == ["C"]


def test_assignment_distribution_negative_count():
    result = validate_assignment_distribution(
        observed={"A": -10, "B": 500},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["is_valid"] is False
    assert result["negative_count_variants"] == ["A"]


def test_assignment_distribution_no_users():
    result = validate_assignment_distribution(
        observed={"A": 0, "B": 0},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["is_valid"] is False
    assert "No assigned users." in result["issues"]


def test_assignment_health_healthy():
    result = evaluate_assignment_health(
        observed={"A": 5000, "B": 5000},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["status"] == "healthy"
    assert result["validation"]["is_valid"] is True
    assert result["srm"]["has_srm"] is False


def test_assignment_health_warning():
    result = evaluate_assignment_health(
        observed={"A": 7000, "B": 3000},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["status"] == "warning"
    assert result["validation"]["is_valid"] is True
    assert result["srm"]["has_srm"] is True


def test_assignment_health_invalid():
    result = evaluate_assignment_health(
        observed={"A": 5000, "B": 5000, "C": 100},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["status"] == "invalid"
    assert result["validation"]["is_valid"] is False
    assert result["srm"] is None


def test_assignment_health_missing_variant():
    result = evaluate_assignment_health(
        observed={"A": 1000},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["status"] == "invalid"
    assert result["validation"]["missing_variants"] == ["B"]
    assert result["srm"] is None


def test_assignment_health_three_variants_unsupported():
    result = evaluate_assignment_health(
        observed={
            "A": 300,
            "B": 300,
            "C": 400,
        },
        expected_weights={
            "A": 0.3,
            "B": 0.3,
            "C": 0.4,
        },
    )

    assert result["status"] == "unsupported"
    assert result["validation"]["is_valid"] is True
    assert result["srm"] is None

    assert result["reason"] == (
        "SRM evaluation currently supports exactly two variants."
    )


def test_srm_sample_size_sufficient():
    result = check_srm_sample_size(
        observed={"A": 50, "B": 50},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["total_users"] == 100
    assert result["expected_counts"] == {
        "A": 50.0,
        "B": 50.0,
    }
    assert result["is_sufficient"] is True


def test_srm_sample_size_insufficient():
    result = check_srm_sample_size(
        observed={"A": 2, "B": 2},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["total_users"] == 4
    assert result["is_sufficient"] is False


def test_srm_sample_size_boundary():
    result = check_srm_sample_size(
        observed={"A": 5, "B": 5},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["is_sufficient"] is True


def test_srm_sample_size_invalid_minimum():
    with pytest.raises(ValueError, match="Minimum expected count"):
        check_srm_sample_size(
            observed={"A": 50, "B": 50},
            expected_weights={"A": 0.5, "B": 0.5},
            minimum_expected=0,
        )




def test_assignment_health_insufficient_data():
    result = evaluate_assignment_health(
        observed={"A": 2, "B": 2},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["status"] == "insufficient_data"
    assert result["validation"]["is_valid"] is True
    assert result["sample_size"]["is_sufficient"] is False
    assert result["srm"] is None


def test_assignment_health_sufficient_data():
    result = evaluate_assignment_health(
        observed={"A": 50, "B": 50},
        expected_weights={"A": 0.5, "B": 0.5},
    )

    assert result["status"] == "healthy"
    assert result["validation"]["is_valid"] is True
    assert result["srm"]["has_srm"] is False