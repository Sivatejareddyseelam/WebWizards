"""wordpress auth

Revision ID: dac16bfab08b
Revises: 7454ebe0f4a6
Create Date: 2024-08-04 16:37:12.935201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dac16bfab08b'
down_revision = '7454ebe0f4a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('wordpress_auth', sa.String(length=256), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.drop_column('wordpress_auth')

    # ### end Alembic commands ###