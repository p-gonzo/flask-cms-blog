"""empty message

Revision ID: 1f822bdfd20e
Revises: a02b82b0e1a8
Create Date: 2020-01-01 16:50:32.994396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f822bdfd20e'
down_revision = 'a02b82b0e1a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photo', sa.Column('location', sa.Text(), nullable=True))
    op.drop_column('photo', 'comment')
    op.drop_column('photo', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photo', sa.Column('name', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('photo', sa.Column('comment', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('photo', 'location')
    # ### end Alembic commands ###
