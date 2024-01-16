"""Add fraktion_abstimmung

Revision ID: e7026a158d4d
Revises: e09b444525fc
Create Date: 2024-01-16 01:07:13.385419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7026a158d4d'
down_revision: Union[str, None] = 'e09b444525fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.schema.CreateSequence(sa.Sequence('fraktion_abstimmung_id_seq', schema='bt')))

    op.create_table(
        'fraktion_abstimmung',
        sa.Column(
            'id',
            sa.Integer(),
            sa.Sequence('fraktion_abstimmung_id_seq', schema='bt'),
            unique=True,
            nullable=False,
        ),
        sa.Column('abstimmung_id', sa.Integer(), nullable=False),
        sa.Column('fraktion', sa.String(), nullable=False),
        sa.Column('ja', sa.Integer(), nullable=False),
        sa.Column('nein', sa.Integer(), nullable=False),
        sa.Column('enthalten', sa.Integer(), nullable=False),
        sa.Column('nicht_abgegeben', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('abstimmung_id', 'fraktion'),
        schema='bt',
    )


def downgrade() -> None:
    op.drop_table('fraktion_abstimmung', schema='bt')

    op.execute(sa.schema.DropSequence(sa.Sequence('fraktion_abstimmung_id_seq', schema='bt')))
