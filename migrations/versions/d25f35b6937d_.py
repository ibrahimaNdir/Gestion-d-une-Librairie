"""empty message

Revision ID: d25f35b6937d
Revises: f836218ccbdf
Create Date: 2024-07-08 13:10:57.730521

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd25f35b6937d'
down_revision = 'f836218ccbdf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('livre', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_path', sa.String(length=255), nullable=True))
        batch_op.drop_column('image_data')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('livre', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_data', postgresql.BYTEA(), autoincrement=False, nullable=True))
        batch_op.drop_column('image_path')

    # ### end Alembic commands ###
