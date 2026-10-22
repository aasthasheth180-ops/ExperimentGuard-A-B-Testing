from pathlib import Path

import numpy as np
import pandas as pd


def generate_experiment_data(
    n_users: int = 20_000,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic checkout A/B experiment data."""

    if n_users <= 0:
        raise ValueError("n_users must be positive")

    rng = np.random.default_rng(seed)

    # Randomly assign each user to A or B
    variants = rng.choice(
        ["A", "B"],
        size=n_users,
        p=[0.5, 0.5],
    )

    # Define the true conversion probability
    conversion_probabilities = np.where(
        variants == "A",
        0.08,
        0.092,
    )

    # Simulate whether each user purchases
    converted = rng.binomial(
        n=1,
        p=conversion_probabilities,
    )

    return pd.DataFrame(
        {
            "user_id": np.arange(1, n_users + 1),
            "variant": variants,
            "converted": converted,
        }
    )


if __name__ == "__main__":
    df = generate_experiment_data()

    output_path = Path("data/synthetic/checkout_experiment.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    print("Dataset generated successfully!")
    print(f"Total users: {len(df):,}")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nUsers per variant:")
    print(df["variant"].value_counts())