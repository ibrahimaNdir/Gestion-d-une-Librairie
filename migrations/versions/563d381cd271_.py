"""empty message

Revision ID: 563d381cd271
Revises: d25f35b6937d
Create Date: 2024-07-08 20:46:21.698734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '563d381cd271'
down_revision = 'd25f35b6937d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('livre', schema=None) as batch_op:
        batch_op.alter_column('image_path',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=150),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('livre', schema=None) as batch_op:
        batch_op.alter_column('image_path',
               existing_type=sa.String(length=150),
               type_=sa.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###
