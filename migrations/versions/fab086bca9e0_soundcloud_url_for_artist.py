"""soundcloud url for artist

Revision ID: fab086bca9e0
Revises: c21cfe512f8b
Create Date: 2020-09-15 22:49:43.461783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fab086bca9e0'
down_revision = 'c21cfe512f8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('soundcloud_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artists', 'soundcloud_url')
    # ### end Alembic commands ###