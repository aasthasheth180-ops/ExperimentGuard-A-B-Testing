from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from .database import Base


class ExperimentRecord(Base):
    __tablename__ = "experiments"

    experiment_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    variants: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    primary_metric: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AssignmentRecord(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    experiment_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("experiments.experiment_id"),
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    variant: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "experiment_id",
            "user_id",
            name="uq_assignment_experiment_user",
        ),
    )



class EventRecord(Base):
    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    experiment_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("experiments.experiment_id"),
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    properties: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )