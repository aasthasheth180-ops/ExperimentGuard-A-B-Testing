from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .experiment import Experiment
from .experiment_manager import ExperimentManager
from .assignment import assign_user
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .experiment_repository import ExperimentRepository
from .event_repository import EventRepository
from .metrics_repository import MetricsRepository
from .models import ExperimentRecord



app = FastAPI(
    title="ExperimentGuard API",
    description="A/B Testing and Experiment Decision Intelligence Platform",
    version="0.1.0",
)

manager = ExperimentManager()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class ExperimentCreate(BaseModel):
    experiment_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    variants: dict[str, float]
    primary_metric: str = Field(min_length=1)


class ExperimentStatusUpdate(BaseModel):
    status: str


class EventCreate(BaseModel):
    event_id: str
    experiment_id: str
    user_id: str
    event_type: str
    properties: dict = Field(default_factory=dict)


@app.post("/experiments", status_code=201)
def create_experiment(
    request: ExperimentCreate,
    db: Session = Depends(get_db),
):
    try:
        experiment = Experiment(
            experiment_id=request.experiment_id,
            name=request.name,
            variants=request.variants,
            primary_metric=request.primary_metric,
        )

        repository = ExperimentRepository(db)
        repository.create(experiment)

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
def get_experiment(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    try:
        repository = ExperimentRepository(db)
        experiment = repository.get(experiment_id)

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
def list_experiments(
    db: Session = Depends(get_db),
):
    repository = ExperimentRepository(db)

    experiments = repository.list_all()

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
    db: Session = Depends(get_db),
):
    try:
        repository = ExperimentRepository(db)

        experiment = repository.update_status(
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
def get_user_assignment(
    experiment_id: str,
    user_id: str,
    db: Session = Depends(get_db),
):
    try:
        repository = ExperimentRepository(db)
        variant = repository.assign_user(experiment_id, user_id)
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


@app.post("/events", status_code=201)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
):
    repository = EventRepository(db)

    try:
        event = repository.create_event(
            event_id=payload.event_id,
            experiment_id=payload.experiment_id,
            user_id=payload.user_id,
            event_type=payload.event_type,
            properties=payload.properties,
        )

        return {
            "event_id": event.event_id,
            "experiment_id": event.experiment_id,
            "user_id": event.user_id,
            "event_type": event.event_type,
            "event_timestamp": event.event_timestamp,
            "properties": event.properties,
        }

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc



@app.get("/experiments/{experiment_id}/metrics")
def get_experiment_metrics(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    experiment = db.get(ExperimentRecord, experiment_id)

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found.",
        )

    repository = MetricsRepository(db)

    return {
        "experiment_id": experiment_id,
        "variants": repository.get_conversion_rates(experiment_id),
        "relative_lift_percent": repository.get_relative_lift(
            experiment_id
        ),
    }
