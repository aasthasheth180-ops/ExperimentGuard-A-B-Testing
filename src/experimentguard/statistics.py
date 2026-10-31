import math


def calculate_pooled_proportion(
    conversions_a: int,
    users_a: int,
    conversions_b: int,
    users_b: int,
) -> float:
    total_users = users_a + users_b

    if total_users <= 0:
        raise ValueError("Total users must be positive.")

    return (conversions_a + conversions_b) / total_users



def calculate_z_statistic(
    conversions_a: int,
    users_a: int,
    conversions_b: int,
    users_b: int,
) -> float:
    if users_a <= 0 or users_b <= 0:
        raise ValueError("Both variants must have users.")

    if not (0 <= conversions_a <= users_a):
        raise ValueError("Invalid conversions for variant A.")

    if not (0 <= conversions_b <= users_b):
        raise ValueError("Invalid conversions for variant B.")

    p_a = conversions_a / users_a
    p_b = conversions_b / users_b

    pooled = calculate_pooled_proportion(
        conversions_a,
        users_a,
        conversions_b,
        users_b,
    )

    standard_error = math.sqrt(
        pooled * (1 - pooled) * (1 / users_a + 1 / users_b)
    )

    if standard_error == 0:
        raise ValueError("Z-statistic is undefined when standard error is zero.")

    return (p_b - p_a) / standard_error


def calculate_p_value(z_statistic: float) -> float:
    return math.erfc(abs(z_statistic) / math.sqrt(2))


def calculate_confidence_interval(
    conversions_a: int,
    users_a: int,
    conversions_b: int,
    users_b: int,
) -> tuple[float, float]:

    if users_a <= 0 or users_b <= 0:
        raise ValueError("Both variants must have users.")

    if not (0 <= conversions_a <= users_a):
        raise ValueError("Invalid conversions for variant A.")

    if not (0 <= conversions_b <= users_b):
        raise ValueError("Invalid conversions for variant B.")

    p_a = conversions_a / users_a
    p_b = conversions_b / users_b

    difference = p_b - p_a

    standard_error = math.sqrt(
        (p_a * (1 - p_a) / users_a)
        + (p_b * (1 - p_b) / users_b)
    )

    margin_of_error = 1.96 * standard_error

    lower_bound = difference - margin_of_error
    upper_bound = difference + margin_of_error

    return lower_bound, upper_bound



def evaluate_significance(
    conversions_a: int,
    users_a: int,
    conversions_b: int,
    users_b: int,
    alpha: float = 0.05,
) -> dict:

    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1.")

    try:
        z_statistic = calculate_z_statistic(
            conversions_a,
            users_a,
            conversions_b,
            users_b,
        )

        p_value = calculate_p_value(z_statistic)

    except ValueError:
        if users_a <= 0 or users_b <= 0:
            raise

        if not (0 <= conversions_a <= users_a):
            raise

        if not (0 <= conversions_b <= users_b):
            raise

        p_a = conversions_a / users_a
        p_b = conversions_b / users_b

        if p_a == p_b and p_a in (0.0, 1.0):
            z_statistic = None
            p_value = 1.0
        else:
            raise

    lower_bound, upper_bound = calculate_confidence_interval(
        conversions_a,
        users_a,
        conversions_b,
        users_b,
    )

    p_a = conversions_a / users_a
    p_b = conversions_b / users_b

    return {
        "conversion_rate_a": p_a,
        "conversion_rate_b": p_b,
        "absolute_difference": p_b - p_a,
        "z_statistic": z_statistic,
        "p_value": p_value,
        "confidence_interval": {
            "lower": lower_bound,
            "upper": upper_bound,
        },
        "alpha": alpha,
        "is_significant": p_value < alpha,
        "normal_approximation_valid": check_sample_size(
            conversions_a,
            users_a,
            conversions_b,
            users_b,
),
    }


def check_sample_size(
    conversions_a: int,
    users_a: int,
    conversions_b: int,
    users_b: int,
) -> bool:
    if users_a <= 0 or users_b <= 0:
        raise ValueError("Both variants must have users.")

    if not (0 <= conversions_a <= users_a):
        raise ValueError("Invalid conversions for variant A.")

    if not (0 <= conversions_b <= users_b):
        raise ValueError("Invalid conversions for variant B.")

    pooled = calculate_pooled_proportion(
        conversions_a,
        users_a,
        conversions_b,
        users_b,
    )

    expected_counts = [
        users_a * pooled,
        users_a * (1 - pooled),
        users_b * pooled,
        users_b * (1 - pooled),
    ]

    return all(count >= 5 for count in expected_counts)