import pytest

from src.experimentguard.experiment import Experiment
from src.experimentguard.experiment_manager import ExperimentManager


def make_experiment(experiment_id="checkout_v1"):
    return Experiment(
        experiment_id=experiment_id,
        name="Checkout Experiment",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="purchase_conversion",
    )


def test_create_and_retrieve_experiment():
    manager = ExperimentManager()
    experiment = make_experiment()

    manager.create_experiment(experiment)

    assert manager.get_experiment("checkout_v1").name == "Checkout Experiment"


def test_duplicate_experiment_rejected():
    manager = ExperimentManager()

    manager.create_experiment(make_experiment())

    with pytest.raises(ValueError, match="already exists"):
        manager.create_experiment(make_experiment())


def test_valid_status_transition():
    manager = ExperimentManager()
    manager.create_experiment(make_experiment())

    manager.update_status("checkout_v1", "running")
    manager.update_status("checkout_v1", "paused")
    manager.update_status("checkout_v1", "running")
    manager.update_status("checkout_v1", "completed")

    assert manager.get_experiment("checkout_v1").status == "completed"


def test_completed_experiment_cannot_restart():
    manager = ExperimentManager()
    manager.create_experiment(make_experiment())

    manager.update_status("checkout_v1", "running")
    manager.update_status("checkout_v1", "completed")

    with pytest.raises(ValueError, match="Cannot transition"):
        manager.update_status("checkout_v1", "running")


def test_non_draft_experiment_cannot_be_created():
    manager = ExperimentManager()
    experiment = make_experiment()
    experiment.status = "running"

    with pytest.raises(ValueError, match="must start in draft"):
        manager.create_experiment(experiment)