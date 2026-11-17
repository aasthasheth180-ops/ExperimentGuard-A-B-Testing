from uuid import uuid4

from src.experimentguard.database import SessionLocal
from src.experimentguard.experiment import Experiment
from src.experimentguard.experiment_repository import ExperimentRepository


def main():
    experiment_id = f"db_test_{uuid4().hex[:8]}"

    experiment = Experiment(
        experiment_id=experiment_id,
        name="Database Persistence Test",
        variants={"A": 0.5, "B": 0.5},
        primary_metric="purchase_conversion",
    )

    with SessionLocal() as session:
        repository = ExperimentRepository(session)

        repository.create(experiment)
        print("Experiment saved successfully")

        saved_experiment = repository.get(experiment_id)

        print("Experiment ID:", saved_experiment.experiment_id)
        print("Experiment Name:", saved_experiment.name)
        print("Variants:", dict(saved_experiment.variants))
        print("Status:", saved_experiment.status)

        assert saved_experiment.experiment_id == experiment_id
        assert saved_experiment.status == "draft"

        print("Database persistence test PASSED")


if __name__ == "__main__":
    main()