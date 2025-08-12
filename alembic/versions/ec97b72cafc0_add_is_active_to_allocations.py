"""add is_active to allocations

Revision ID: ec97b72cafc0
Revises: fa7e67ea6a3d
Create Date: 2025-08-11 21:31:26.190450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec97b72cafc0'
down_revision: Union[str, Sequence[str], None] = 'fa7e67ea6a3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('allocations', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))

def downgrade() -> None:
    op.drop_column('allocations', 'is_active')
