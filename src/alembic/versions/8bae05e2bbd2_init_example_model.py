"""init example model

Revision ID: 8bae05e2bbd2
Revises:
Create Date: 2023-06-29 11:21:40.356611

"""
from typing import Sequence, Union
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '8bae05e2bbd2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'example_model',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name='example_model_pkey'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('example_model')
