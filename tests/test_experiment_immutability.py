import pytest
from dataclasses import FrozenInstanceError

from src.experimentguard.experiment import Experiment
from src.experimentguard.experiment_manager import ExperimentManager


def make_experiment(variants=None):
    return Experiment(
        experiment_id="checkout_v1",
        name="Checkout Experiment",
        variants=variants if variants is not None else {"A": 0.5, "B": 0.5},
        primary_metric="purchase_conversion",
    )


def test_cannot_change_experiment_id():
    experiment = make_experiment()

    with pytest.raises(FrozenInstanceError):
        experiment.experiment_id = "different_id"


def test_cannot_change_variant_weights():
    experiment = make_experiment()

    with pytest.raises(TypeError):
        experiment.variants["A"] = 0.7


def test_original_dictionary_cannot_change_experiment():
    original_variants = {"A": 0.5, "B": 0.5}
    experiment = make_experiment(original_variants)

    original_variants["A"] = 0.7
    original_variants["B"] = 0.3

    assert experiment.variants["A"] == 0.5
    assert experiment.variants["B"] == 0.5


def test_manager_can_still_update_status():
    manager = ExperimentManager()
    manager.create_experiment(make_experiment())

    updated = manager.update_status("checkout_v1", "running")

    assert updated.status == "running"
    assert updated.variants["A"] == 0.5
    assert updated.variants["B"] == 0.5