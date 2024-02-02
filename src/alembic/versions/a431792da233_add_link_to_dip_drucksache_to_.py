"""Add link to dip-drucksache to abstimmung-drucksache

Revision ID: a431792da233
Revises: 4244e7fe7beb
Create Date: 2024-02-01 22:44:14.737898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a431792da233'
down_revision: Union[str, None] = '4244e7fe7beb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'abstimmung_drucksache',
        sa.Column(
            'dip_drucksache_id',
            sa.Integer(),
            nullable=True,
        ),
        schema='bt',
    )

    op.create_foreign_key(
        'abstimmung_drucksache_dip_drucksache_id_fkey',
        'abstimmung_drucksache',
        'drucksache',
        ['dip_drucksache_id'],
        ['id'],
        source_schema='bt',
        referent_schema='dip',
    )


def downgrade() -> None:
    op.drop_constraint(
        'abstimmung_drucksache_dip_drucksache_id_fkey',
        'abstimmung_drucksache',
        schema='bt',
        type_='foreignkey',
    )

    op.drop_column('abstimmung_drucksache', 'dip_drucksache_id', schema='bt')
