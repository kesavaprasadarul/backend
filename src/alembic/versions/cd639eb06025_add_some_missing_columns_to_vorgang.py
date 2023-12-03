"""Add some missing columns to Vorgang

Revision ID: cd639eb06025
Revises: 2d2a36a65c30
Create Date: 2023-11-30 22:57:51.993491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd639eb06025'
down_revision: Union[str, None] = '2d2a36a65c30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'vorgang',
        sa.Column('plenarprotokoll_id', sa.Integer(), nullable=True),
        schema='dip',
    )

    op.create_foreign_key(
        'vorgang_plenarprotokoll_id_fkey',
        'vorgang',
        'plenarprotokoll',
        ['plenarprotokoll_id'],
        ['id'],
        source_schema='dip',
        referent_schema='dip',
    )

    op.add_column(
        'vorgang',
        sa.Column('drucksache_id', sa.Integer(), nullable=True),
        schema='dip',
    )

    op.create_foreign_key(
        'vorgang_drucksache_id_fkey',
        'vorgang',
        'drucksache',
        ['drucksache_id'],
        ['id'],
        source_schema='dip',
        referent_schema='dip',
    )


def downgrade() -> None:
    op.drop_constraint(
        'vorgang_drucksache_id_fkey',
        'vorgang',
        schema='dip',
        type_='foreignkey',
    )
    op.drop_column('vorgang', 'drucksache_id', schema='dip')

    op.drop_constraint(
        'vorgang_plenarprotokoll_id_fkey',
        'vorgang',
        schema='dip',
        type_='foreignkey',
    )
    op.drop_column('vorgang', 'plenarprotokoll_id', schema='dip')
