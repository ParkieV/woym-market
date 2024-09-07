"""renmae self_volume to volume

Revision ID: 18855c35df0f
Revises: af3dafb05016
Create Date: 2024-08-27 01:22:10.678251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18855c35df0f'
down_revision: Union[str, None] = 'af3dafb05016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('catalog_items', 'self_volume', new_column_name='volume')


def downgrade() -> None:
    op.alter_column('catalog_items', 'volume', new_column_name='self_volume')

