import math


def calculate_srm_chi_square(
    observed: dict[str, int],
    expected_weights: dict[str, float],
) -> float:
    if set(observed) != set(expected_weights):
        raise ValueError("Observed and expected variants must match.")

    total_users = sum(observed.values())

    if total_users <= 0:
        raise ValueError("Total assigned users must be positive.")

    if any(count < 0 for count in observed.values()):
        raise ValueError("Observed counts cannot be negative.")

    if any(weight <= 0 for weight in expected_weights.values()):
        raise ValueError("Expected weights must be positive.")

    if abs(sum(expected_weights.values()) - 1.0) > 1e-9:
        raise ValueError("Expected weights must sum to 1.")

    chi_square = 0.0

    for variant, observed_count in observed.items():
        expected_count = total_users * expected_weights[variant]

        chi_square += (
            (observed_count - expected_count) ** 2
            / expected_count
        )

    return chi_square


def calculate_srm_p_value(chi_square: float) -> float:
    if not math.isfinite(chi_square) or chi_square < 0:
        raise ValueError("Chi-square must be finite and non-negative.")

    return math.erfc(math.sqrt(chi_square / 2))



def evaluate_srm(
    observed: dict[str, int],
    expected_weights: dict[str, float],
    alpha: float = 0.001,
) -> dict:

    if len(expected_weights) != 2:
        raise ValueError(
            "SRM evaluation currently supports exactly two variants."
        )

    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1.")

    chi_square = calculate_srm_chi_square(
        observed,
        expected_weights,
    )

    p_value = calculate_srm_p_value(chi_square)

    total_users = sum(observed.values())

    observed_ratios = {
        variant: count / total_users
        for variant, count in observed.items()
    }

    return {
        "total_users": total_users,
        "observed_counts": observed,
        "expected_weights": expected_weights,
        "observed_ratios": observed_ratios,
        "chi_square": chi_square,
        "p_value": p_value,
        "alpha": alpha,
        "has_srm": p_value < alpha,
    }


def validate_assignment_distribution(
    observed: dict[str, int],
    expected_weights: dict[str, float],
) -> dict:

    expected_variants = set(expected_weights)
    observed_variants = set(observed)

    missing_variants = sorted(
        expected_variants - observed_variants
    )

    unexpected_variants = sorted(
        observed_variants - expected_variants
    )

    negative_counts = sorted(
        variant
        for variant, count in observed.items()
        if count < 0
    )

    total_users = sum(
        count for count in observed.values()
        if count >= 0
    )

    issues = []

    if missing_variants:
        issues.append("Missing expected variants.")

    if unexpected_variants:
        issues.append("Unexpected variants detected.")

    if negative_counts:
        issues.append("Negative assignment counts detected.")

    if total_users == 0:
        issues.append("No assigned users.")

    return {
        "is_valid": len(issues) == 0,
        "total_users": total_users,
        "missing_variants": missing_variants,
        "unexpected_variants": unexpected_variants,
        "negative_count_variants": negative_counts,
        "issues": issues,
    }


def evaluate_assignment_health(
    observed: dict[str, int],
    expected_weights: dict[str, float],
    alpha: float = 0.001,
) -> dict:

    validation = validate_assignment_distribution(
        observed=observed,
        expected_weights=expected_weights,
    )

    if not validation["is_valid"]:
        return {
            "status": "invalid",
            "validation": validation,
            "srm": None,
        }

    if len(expected_weights) != 2:
        return {
            "status": "unsupported",
            "validation": validation,
            "srm": None,
            "reason": (
                "SRM evaluation currently supports exactly two variants."
            ),
        }

    sample_size = check_srm_sample_size(
    observed=observed,
    expected_weights=expected_weights,
)

    if not sample_size["is_sufficient"]:
        return {
            "status": "insufficient_data",
            "validation": validation,
            "sample_size": sample_size,
            "srm": None,
        }



    srm_result = evaluate_srm(
        observed=observed,
        expected_weights=expected_weights,
        alpha=alpha,
    )

    if srm_result["has_srm"]:
        status = "warning"
    else:
        status = "healthy"

    return {
        "status": status,
        "validation": validation,
        "srm": srm_result,
    }


def check_srm_sample_size(
    observed: dict[str, int],
    expected_weights: dict[str, float],
    minimum_expected: float = 5.0,
) -> dict:

    if not math.isfinite(minimum_expected) or minimum_expected <= 0:
        raise ValueError("Minimum expected count must be positive and finite.")

    total_users = sum(observed.values())

    expected_counts = {
        variant: total_users * weight
        for variant, weight in expected_weights.items()
    }

    is_sufficient = all(
        count >= minimum_expected
        for count in expected_counts.values()
    )

    return {
        "total_users": total_users,
        "expected_counts": expected_counts,
        "minimum_expected": minimum_expected,
        "is_sufficient": is_sufficient,
    }