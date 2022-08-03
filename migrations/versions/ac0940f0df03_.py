"""empty message

Revision ID: ac0940f0df03
Revises: 12442bde4f2b
Create Date: 2022-08-03 15:45:20.589491

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac0940f0df03'
down_revision = '12442bde4f2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'Venue', 'Genres', ['genres_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Venue', type_='foreignkey')
    op.drop_column('Venue', 'genres_id')
    # ### end Alembic commands ###
