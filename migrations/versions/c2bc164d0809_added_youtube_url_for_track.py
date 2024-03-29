"""Added youtube URL for Track

Revision ID: c2bc164d0809
Revises: 5a84a5912821
Create Date: 2020-10-06 22:55:39.747160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2bc164d0809'
down_revision = '5a84a5912821'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracks', sa.Column('youtube_url', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'tracks', ['youtube_url'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tracks', type_='unique')
    op.drop_column('tracks', 'youtube_url')
    # ### end Alembic commands ###
