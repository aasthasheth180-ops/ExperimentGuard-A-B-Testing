import pytest

from src.experimentguard.experiment import Experiment
from src.experimentguard.assignment import assign_user


def make_experiment(
    experiment_id="checkout_v1",
    status="running",
):
    return Experiment(
        experiment_id=experiment_id,
        name="Checkout Experiment",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="purchase_conversion",
        status=status,
    )


def test_same_user_gets_same_variant():
    experiment = make_experiment()

    first_assignment = assign_user(experiment, "user_101")

    for _ in range(100):
        assert assign_user(experiment, "user_101") == first_assignment


def test_different_experiments_have_independent_assignments():
    experiment_1 = make_experiment("checkout_v1")
    experiment_2 = make_experiment("checkout_v2")

    # Both experiments must produce valid assignments.
    for user_id in range(100):
        assignment_1 = assign_user(experiment_1, str(user_id))
        assignment_2 = assign_user(experiment_2, str(user_id))

        assert assignment_1 in {"A", "B"}
        assert assignment_2 in {"A", "B"}

    # Independent experiments do not need to assign
    # the same user to different variants.


def test_draft_experiment_cannot_assign_users():
    experiment = make_experiment(status="draft")

    with pytest.raises(ValueError, match="must be running"):
        assign_user(experiment, "user_101")


def test_empty_user_id_is_rejected():
    experiment = make_experiment()

    with pytest.raises(ValueError, match="non-empty string"):
        assign_user(experiment, "")