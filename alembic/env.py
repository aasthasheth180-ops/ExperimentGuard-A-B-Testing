from logging.config import fileConfig
import os
from sqlalchemy.engine import make_url
from alembic import context
from sqlalchemy import create_engine, pool

from src.experimentguard.database import Base, DATABASE_URL
from src.experimentguard import models  # Register SQLAlchemy models

config = context.config

database_url = make_url(
    os.getenv("ALEMBIC_DATABASE_URL")
    or DATABASE_URL.render_as_string(hide_password=False)
)


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Tell Alembic which tables to track
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=database_url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )


    with context.begin_transaction():
        context.run_migrations()



def run_migrations_online():
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()