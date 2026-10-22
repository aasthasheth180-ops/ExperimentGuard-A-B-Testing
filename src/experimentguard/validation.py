import pandas as pd


REQUIRED_COLUMNS = {"user_id", "variant", "converted"}
ALLOWED_VARIANTS = {"A", "B"}
ALLOWED_CONVERSIONS = {0, 1}


def validate_experiment_data(df: pd.DataFrame) -> bool:
    """Validate the structure and values of an A/B experiment dataset."""

    if df.empty:
        raise ValueError("Experiment dataset cannot be empty.")

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if df[list(REQUIRED_COLUMNS)].isnull().any().any():
        raise ValueError("Dataset contains missing values.")

    if df["user_id"].duplicated().any():
        raise ValueError("Duplicate user IDs detected.")

    if not df["variant"].isin(ALLOWED_VARIANTS).all():
        raise ValueError("Invalid experiment variant detected.")

    if not df["converted"].isin(ALLOWED_CONVERSIONS).all():
        raise ValueError("Invalid conversion values detected.")

    return True