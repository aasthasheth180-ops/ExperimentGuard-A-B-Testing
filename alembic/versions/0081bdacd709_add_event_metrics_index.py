"""add event metrics index

Revision ID: 0081bdacd709
Revises: ce2578780d11
Create Date: 2026-11-17 11:43:19.823031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0081bdacd709'
down_revision: Union[str, Sequence[str], None] = 'ce2578780d11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_index(
        "ix_events_experiment_type_user",
        "events",
        ["experiment_id", "event_type", "user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_events_experiment_type_user",
        table_name="events",
    )