"""initial commit

Revision ID: a1d8c19f9ba3
Revises: 
Create Date: 2024-08-11 13:46:47.823550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1d8c19f9ba3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('plan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_duration', sa.Integer(), nullable=True),
    sa.Column('plan_domain_limit', sa.Integer(), nullable=True),
    sa.Column('plan_api_call_limit', sa.Integer(), nullable=True),
    sa.Column('plan_name', sa.String(length=120), nullable=False),
    sa.Column('plan_type', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_plan_plan_name'), ['plan_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_plan_plan_type'), ['plan_type'], unique=False)

    op.create_table('customer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('customer_full_name', sa.String(length=64), nullable=False),
    sa.Column('customer_company_name', sa.String(length=64), nullable=False),
    sa.Column('customer_email', sa.String(length=120), nullable=False),
    sa.Column('customer_phone', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.Column('plan_id', sa.Integer(), nullable=True),
    sa.Column('domain_count', sa.Integer(), nullable=True),
    sa.Column('api_call_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_customer_customer_company_name'), ['customer_company_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_customer_customer_email'), ['customer_email'], unique=True)
        batch_op.create_index(batch_op.f('ix_customer_customer_full_name'), ['customer_full_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_customer_customer_phone'), ['customer_phone'], unique=True)
        batch_op.create_index(batch_op.f('ix_customer_plan_id'), ['plan_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_customer_token'), ['token'], unique=True)
        batch_op.create_index(batch_op.f('ix_customer_username'), ['username'], unique=False)

    op.create_table('domain',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain_name', sa.String(length=120), nullable=False),
    sa.Column('domain_start_date', sa.DateTime(), nullable=True),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('domain_platform', sa.Enum('wordpress', name='domain_platform'), nullable=True),
    sa.Column('domain_login_username', sa.String(length=120), nullable=True),
    sa.Column('domain_login_password', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('domain', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_domain_customer_id'), ['customer_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_domain_domain_name'), ['domain_name'], unique=True)

    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.Float(), nullable=False),
    sa.Column('payload_json', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_notification_customer_id'), ['customer_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_notification_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_notification_timestamp'), ['timestamp'], unique=False)

    op.create_table('task',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('complete', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_task_name'), ['name'], unique=False)

    op.create_table('activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('activity_name', sa.String(length=120), nullable=False),
    sa.Column('activity_msg', sa.String(length=150), nullable=False),
    sa.Column('activity_timestamp', sa.DateTime(), nullable=True),
    sa.Column('domain_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.ForeignKeyConstraint(['domain_id'], ['domain.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_activity_activity_msg'), ['activity_msg'], unique=True)
        batch_op.create_index(batch_op.f('ix_activity_activity_name'), ['activity_name'], unique=True)
        batch_op.create_index(batch_op.f('ix_activity_customer_id'), ['customer_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_activity_domain_id'), ['domain_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_activity_domain_id'))
        batch_op.drop_index(batch_op.f('ix_activity_customer_id'))
        batch_op.drop_index(batch_op.f('ix_activity_activity_name'))
        batch_op.drop_index(batch_op.f('ix_activity_activity_msg'))

    op.drop_table('activity')
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_task_name'))

    op.drop_table('task')
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notification_timestamp'))
        batch_op.drop_index(batch_op.f('ix_notification_name'))
        batch_op.drop_index(batch_op.f('ix_notification_customer_id'))

    op.drop_table('notification')
    with op.batch_alter_table('domain', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_domain_domain_name'))
        batch_op.drop_index(batch_op.f('ix_domain_customer_id'))

    op.drop_table('domain')
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_customer_username'))
        batch_op.drop_index(batch_op.f('ix_customer_token'))
        batch_op.drop_index(batch_op.f('ix_customer_plan_id'))
        batch_op.drop_index(batch_op.f('ix_customer_customer_phone'))
        batch_op.drop_index(batch_op.f('ix_customer_customer_full_name'))
        batch_op.drop_index(batch_op.f('ix_customer_customer_email'))
        batch_op.drop_index(batch_op.f('ix_customer_customer_company_name'))

    op.drop_table('customer')
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_plan_plan_type'))
        batch_op.drop_index(batch_op.f('ix_plan_plan_name'))

    op.drop_table('plan')
    # ### end Alembic commands ###