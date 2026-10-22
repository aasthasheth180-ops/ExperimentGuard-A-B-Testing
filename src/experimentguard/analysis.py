import pandas as pd

from .validation import validate_experiment_data


def analyze_experiment(df: pd.DataFrame) -> dict:
    """Calculate conversion metrics for an A/B experiment."""

    validate_experiment_data(df)

    summary = (
        df.groupby("variant")["converted"]
        .agg(["count", "sum"])
        .rename(
            columns={
                "count": "users",
                "sum": "conversions",
            }
        )
    )

    summary["conversion_rate"] = (
        summary["conversions"] / summary["users"]
    )

    if not {"A", "B"}.issubset(summary.index):
        raise ValueError("Both experiment variants A and B are required.")

    rate_a = summary.loc["A", "conversion_rate"]
    rate_b = summary.loc["B", "conversion_rate"]

    absolute_difference = rate_b - rate_a

    relative_lift = (
        absolute_difference / rate_a
        if rate_a > 0
        else None
    )

    return {
        "summary": summary,
        "absolute_difference": absolute_difference,
        "relative_lift": relative_lift,
    }


if __name__ == "__main__":
    df = pd.read_csv("data/synthetic/checkout_experiment.csv")

    results = analyze_experiment(df)

    print("\nExperiment Results")
    print("------------------")
    print(results["summary"])

    print(
        f"\nAbsolute difference: "
        f"{results['absolute_difference'] * 100:.2f} percentage points"
    )

    if results["relative_lift"] is not None:
        print(
            f"Relative lift: "
            f"{results['relative_lift'] * 100:.2f}%"
        )
    else:
        print("Relative lift: undefined (control conversion rate is zero)")