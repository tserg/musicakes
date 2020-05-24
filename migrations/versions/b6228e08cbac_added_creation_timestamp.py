"""Added creation timestamp

Revision ID: b6228e08cbac
Revises: 1dbb379d8565
Create Date: 2020-05-24 21:42:54.037044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6228e08cbac'
down_revision = '1dbb379d8565'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('releases', sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('tracks', sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.execute("UPDATE users SET created_on=CURRENT_TIMESTAMP")
    op.alter_column('users', sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'created_on')
    op.drop_column('tracks', 'created_on')
    op.drop_column('releases', 'created_on')
    op.drop_column('artists', 'created_on')
    # ### end Alembic commands ###
