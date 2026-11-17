import os
import logging

from fastapi import FastAPI, HTTPException,Request,Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from .experiment import Experiment
from .experiment_manager import ExperimentManager
from .assignment import assign_user
from typing import Generator
from sqlalchemy.orm import Session
from .database import SessionLocal
from .experiment_repository import ExperimentRepository
from .event_repository import EventRepository
from .metrics_repository import MetricsRepository
from .statistics_repository import StatisticsRepository
from .models import ExperimentRecord
from src.experimentguard.health_repository import HealthRepository
from src.experimentguard.decision_repository import DecisionRepository
from .auth_routes import router as auth_router
from .auth import get_current_user, validate_auth_configuration
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from .logging_config import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger = logging.getLogger("experimentguard")

    validate_auth_configuration()

    logger.info("ExperimentGuard API starting")

    try:
        yield
    finally:
        logger.info("ExperimentGuard API shutting down")

app = FastAPI(
    title="ExperimentGuard API",
    description="A/B Testing and Experiment Decision Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger = logging.getLogger("experimentguard")

    logger.error(
        "Unhandled exception: method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred."
        },
    )


DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)

cors_origins_raw = os.getenv("CORS_ORIGINS")



APP_ENV = os.getenv("APP_ENV", "development").strip().lower()

if APP_ENV not in {"development", "test", "production"}:
    raise RuntimeError(
        "APP_ENV must be development, test, or production."
    )

if APP_ENV == "production" and not cors_origins_raw:
    raise RuntimeError(
        "CORS_ORIGINS must be explicitly configured in production."
    )




if cors_origins_raw is None:
    cors_origins = list(DEFAULT_CORS_ORIGINS)
else:
    cors_origins = [
        origin.strip().rstrip("/")
        for origin in cors_origins_raw.split(",")
        if origin.strip()
    ]

if "*" in cors_origins:
    raise RuntimeError(
        "CORS_ORIGINS must contain explicit frontend origins, not '*'."
    )




app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)


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
    hypothesis: str | None = Field(default=None, max_length=5000)
    variants: dict[str, float]
    primary_metric: str = Field(min_length=1)
    planned_sample_size: int | None = Field(default=None, gt=0)


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
    current_user=Depends(get_current_user),
):
    try:
        experiment = Experiment(
            experiment_id=request.experiment_id,
            name=request.name,
            hypothesis=request.hypothesis,
            variants=request.variants,
            primary_metric=request.primary_metric,
            planned_sample_size=request.planned_sample_size,
        )

        repository = ExperimentRepository(db)
        repository.create(experiment)

        return {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "hypothesis": experiment.hypothesis,
            "variants": dict(experiment.variants),
            "primary_metric": experiment.primary_metric,
            "planned_sample_size": experiment.planned_sample_size,
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
    current_user = Depends(get_current_user),
):
    try:
        repository = ExperimentRepository(db)
        experiment = repository.get(experiment_id)

        return {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "hypothesis": experiment.hypothesis,
            "variants": dict(experiment.variants),
            "primary_metric": experiment.primary_metric,
            "planned_sample_size": experiment.planned_sample_size,
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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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


@app.get("/experiments/{experiment_id}/statistics")
def get_experiment_statistics(
    experiment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),

):
    experiment = db.get(ExperimentRecord, experiment_id)

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found.",
        )

    repository = StatisticsRepository(db)

    try:
        result = repository.get_significance(experiment_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "experiment_id": experiment_id,
        "statistics": result,
    }


@app.get("/experiments/{experiment_id}/health")
def get_experiment_health(
    experiment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repository = HealthRepository(db)

    try:
        result = repository.get_assignment_health(
            experiment_id
        )

        return {
            "experiment_id": experiment_id,
            **result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error




@app.get("/experiments/{experiment_id}/decision")
def get_experiment_decision(
    experiment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repository = DecisionRepository(db)

    try:
        result = repository.get_decision(experiment_id)
        return result

    except ValueError as error:
        if str(error) == "Experiment not found.":
            raise HTTPException(
                status_code=404,
                detail=str(error),
            ) from error

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
