"""merge 69e1b and 168b8

Revision ID: 038e6a9eee2b
Revises: 69e1b60db1cb, 168b8f28461f
Create Date: 2023-12-11 01:56:44.357932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '038e6a9eee2b'
down_revision: Union[str, tuple[str, str], None] = ('69e1b60db1cb', '168b8f28461f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
