"""empty message

Revision ID: f836218ccbdf
Revises: a63d58766458
Create Date: 2024-07-08 11:06:11.481413

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f836218ccbdf'
down_revision = 'a63d58766458'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('livre', schema=None) as batch_op:
        batch_op.add_column(sa.Column('annee', sa.Integer(), nullable=False))
        batch_op.drop_column('date_parution')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('livre', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_parution', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
        batch_op.drop_column('annee')

    # ### end Alembic commands ###