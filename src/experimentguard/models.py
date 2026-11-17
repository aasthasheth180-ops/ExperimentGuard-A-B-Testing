from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint,Text,Index,DateTime, String, Integer
from .database import Base

class ExperimentRecord(Base):
    __tablename__ = "experiments"

    experiment_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )

    planned_sample_size: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    hypothesis: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
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

    __table_args__ = (
        Index(
            "ix_events_experiment_type_user",
            "experiment_id",
            "event_type",
            "user_id",
        ),
    )



class UserRecord(Base):
    __tablename__ = "platform_users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
