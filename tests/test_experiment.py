import pandas as pd
import pytest

from src.experimentguard.validation import validate_experiment_data
from src.experimentguard.analysis import analyze_experiment


def test_valid_experiment_data():
    df = pd.DataFrame({
        "user_id": [1, 2, 3, 4],
        "variant": ["A", "A", "B", "B"],
        "converted": [0, 1, 1, 1],
    })

    assert validate_experiment_data(df) is True


def test_duplicate_user_ids():
    df = pd.DataFrame({
        "user_id": [1, 1, 3, 4],
        "variant": ["A", "A", "B", "B"],
        "converted": [0, 1, 1, 1],
    })

    with pytest.raises(ValueError, match="Duplicate user IDs"):
        validate_experiment_data(df)


def test_conversion_rate_calculation():
    df = pd.DataFrame({
        "user_id": [1, 2, 3, 4, 5, 6, 7, 8],
        "variant": ["A", "A", "A", "A", "B", "B", "B", "B"],
        "converted": [1, 0, 0, 0, 1, 1, 0, 0],
    })

    results = analyze_experiment(df)

    assert results["summary"].loc["A", "conversion_rate"] == 0.25
    assert results["summary"].loc["B", "conversion_rate"] == 0.50
    assert results["absolute_difference"] == pytest.approx(0.25)
    assert results["relative_lift"] == pytest.approx(1.0)