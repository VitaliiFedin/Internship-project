"""Updated company

Revision ID: 50fc8eeacdc6
Revises: 4bac05cc7bea
Create Date: 2023-10-11 19:21:40.017000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50fc8eeacdc6'
down_revision: Union[str, None] = '4bac05cc7bea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'companies', ['phone'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'companies', type_='unique')
    # ### end Alembic commands ###

