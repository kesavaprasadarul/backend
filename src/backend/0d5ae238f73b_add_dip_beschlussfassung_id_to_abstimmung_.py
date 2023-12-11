"""Add DIP-Columns to abstimmung-table

Revision ID: 0d5ae238f73b
Revises: 168b8f28461f
Create Date: 2023-12-10 18:33:55.416791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d5ae238f73b'
down_revision: Union[str, None] = '168b8f28461f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # abstract
    op.add_column('abstimmung', sa.Column('abstract', sa.Integer(), nullable=True))

    # aktualisiert
    op.alter_column('abstimmung', 'aktualisiert', nullable=True)

    # initiative
    op.add_column('abstimmung', sa.Column('initiative', sa.ARRAY(sa.Text()), nullable=True))

    # ergebnis_anmerkung
    op.add_column('abstimmung', sa.Column('ergebnis_anmerkung', sa.Text(), nullable=True))

    # sachgebiet
    op.add_column('abstimmung', sa.Column('sachgebiet', sa.ARRAY(sa.Text()), nullable=True))

    # abstimmungsart
    op.add_column('abstimmung', sa.Column('abstimmungsart', sa.Text(), nullable=True))

    # beschlussfassung_id
    op.add_column('abstimmung', sa.Column('dip_beschlussfassung_id', sa.Integer(), nullable=False))
    op.create_unique_constraint(None, 'abstimmung', ['dip_beschlussfassung_id'])

    # vorgangsposition_id
    op.add_column('abstimmung', sa.Column('dip_vorgangsposition_id', sa.Integer(), nullable=False))


def downgrade() -> None:
    op.drop_column('abstimmung', 'dip_vorgangsposition_id')

    op.drop_column('abstimmung', 'dip_beschlussfassung_id')

    op.drop_column('abstimmung', 'sachgebiet')

    op.drop_column('abstimmung', 'ergebnis_anmerkung')

    op.drop_column('abstimmung', 'initiative')

    op.execute(""" DELETE FROM abstimmung WHERE aktualisiert IS NULL """)
    op.alter_column('abstimmung', 'aktualisiert', nullable=False)

    op.drop_column('abstimmung', 'datum')

    op.drop_column('abstimmung', 'abstract')
