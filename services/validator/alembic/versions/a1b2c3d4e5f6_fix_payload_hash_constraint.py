"""fix payload_hash unique constraint scope

Revision ID: a1b2c3d4e5f6
Revises: 3e6b8c9d37c7
Create Date: 2026-05-20 17:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '3e6b8c9d37c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Replace global unique on payload_hash with composite (schema_version_id, payload_hash)."""
    # Drop the old global unique constraint
    op.drop_constraint('validation_results_payload_hash_key', 'validation_results', type_='unique')
    # Add the scoped composite unique constraint
    op.create_unique_constraint('uq_version_payload', 'validation_results', ['schema_version_id', 'payload_hash'])


def downgrade() -> None:
    """Revert to global unique on payload_hash."""
    op.drop_constraint('uq_version_payload', 'validation_results', type_='unique')
    op.create_unique_constraint('validation_results_payload_hash_key', 'validation_results', ['payload_hash'])
