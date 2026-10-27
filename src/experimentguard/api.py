from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .experiment import Experiment
from .experiment_manager import ExperimentManager
from .assignment import assign_user


app = FastAPI(
    title="ExperimentGuard API",
    description="A/B Testing and Experiment Decision Intelligence Platform",
    version="0.1.0",
)

manager = ExperimentManager()


class ExperimentCreate(BaseModel):
    experiment_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    variants: dict[str, float]
    primary_metric: str = Field(min_length=1)


class ExperimentStatusUpdate(BaseModel):
    status: str


@app.post("/experiments", status_code=201)
def create_experiment(request: ExperimentCreate):
    try:
        experiment = Experiment(
            experiment_id=request.experiment_id,
            name=request.name,
            variants=request.variants,
            primary_metric=request.primary_metric,
        )

        manager.create_experiment(experiment)

        return {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "variants": dict(experiment.variants),
            "primary_metric": experiment.primary_metric,
            "status": experiment.status,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

@app.get("/experiments/{experiment_id}")
def get_experiment(experiment_id: str):
    try:
        experiment = manager.get_experiment(experiment_id)

        return {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "variants": dict(experiment.variants),
            "primary_metric": experiment.primary_metric,
            "status": experiment.status,
        }

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found.",
        )

@app.get("/experiments")
def list_experiments():
    experiments = manager.list_experiments()

    return [
        {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "variants": dict(experiment.variants),
            "primary_metric": experiment.primary_metric,
            "status": experiment.status,
        }
        for experiment in experiments
    ]

@app.patch("/experiments/{experiment_id}/status")
def update_experiment_status(
    experiment_id: str,
    request: ExperimentStatusUpdate,
):
    try:
        experiment = manager.update_status(
            experiment_id,
            request.status,
        )

        return {
            "experiment_id": experiment.experiment_id,
            "status": experiment.status,
        }

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found.",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

@app.get("/experiments/{experiment_id}/assign/{user_id}")
def get_user_assignment(experiment_id: str, user_id: str):
    try:
        experiment = manager.get_experiment(experiment_id)

        variant = assign_user(experiment, user_id)

        return {
            "experiment_id": experiment_id,
            "user_id": user_id,
            "variant": variant,
        }

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found.",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
