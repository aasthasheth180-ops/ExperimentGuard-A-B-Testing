from collections import Counter

from src.experimentguard.experiment import Experiment
from src.experimentguard.assignment import assign_user


def test_50_50_distribution():
    experiment = Experiment(
        experiment_id="distribution_50_50",
        name="50/50 Distribution Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="conversion",
        status="running",
    )

    assignments = [
        assign_user(experiment, str(user_id))
        for user_id in range(10_000)
    ]

    counts = Counter(assignments)

    proportion_a = counts["A"] / 10_000
    proportion_b = counts["B"] / 10_000

    print("\n50/50 allocation:")
    print(f"A: {counts['A']} ({proportion_a:.2%})")
    print(f"B: {counts['B']} ({proportion_b:.2%})")

    assert abs(proportion_a - 0.5) < 0.03
    assert abs(proportion_b - 0.5) < 0.03


def test_70_30_distribution():
    experiment = Experiment(
        experiment_id="distribution_70_30",
        name="70/30 Distribution Test",
        variants={"A": 0.7, "B": 0.3},
        primary_metric="conversion",
        status="running",
    )

    assignments = [
        assign_user(experiment, str(user_id))
        for user_id in range(10_000)
    ]

    counts = Counter(assignments)

    proportion_a = counts["A"] / 10_000
    proportion_b = counts["B"] / 10_000

    print("\n70/30 allocation:")
    print(f"A: {counts['A']} ({proportion_a:.2%})")
    print(f"B: {counts['B']} ({proportion_b:.2%})")

    assert abs(proportion_a - 0.7) < 0.03
    assert abs(proportion_b - 0.3) < 0.03