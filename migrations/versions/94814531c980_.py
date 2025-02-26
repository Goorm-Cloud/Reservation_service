"""empty message

Revision ID: 94814531c980
Revises: 
Create Date: 2025-02-26 15:47:49.477073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94814531c980'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parkinglot',
    sa.Column('parkinglot_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('parkinglot_name', sa.String(length=50), nullable=False),
    sa.Column('latitude', sa.String(length=20), nullable=False),
    sa.Column('longitude', sa.String(length=20), nullable=False),
    sa.Column('parkinglot_div', sa.Enum('public', 'private', name='parking_div_enum'), nullable=False),
    sa.Column('parkinglot_type', sa.Enum('indoor', 'outdoor', 'attached', name='parking_type_enum'), nullable=True),
    sa.Column('parkinglot_num', sa.Integer(), nullable=True),
    sa.Column('parkinglot_cost', sa.Boolean(), nullable=True),
    sa.Column('parkinglot_add', sa.String(length=100), nullable=True),
    sa.Column('parkinglot_day', sa.Enum('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', name='parking_day_enum'), nullable=True),
    sa.Column('parkinglot_time', sa.Time(), nullable=True),
    sa.PrimaryKeyConstraint('parkinglot_id', name=op.f('pk_parkinglot'))
    )
    op.create_table('user',
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('gender', sa.String(length=10), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('role', sa.Enum('admin', 'user', name='role_enum'), nullable=False),
    sa.PrimaryKeyConstraint('user_id', name=op.f('pk_user')),
    sa.UniqueConstraint('email', name=op.f('uq_user_email'))
    )
    op.create_table('reservation',
    sa.Column('reservation_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('parkinglot_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('reservation_status', sa.Enum('confirm', 'none', 'cancel', name='modified_type_enum'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(length=16), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('modified_by', sa.String(length=16), nullable=True),
    sa.ForeignKeyConstraint(['parkinglot_id'], ['parkinglot.parkinglot_id'], name=op.f('fk_reservation_parkinglot_id_parkinglot')),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name=op.f('fk_reservation_user_id_user')),
    sa.PrimaryKeyConstraint('reservation_id', name=op.f('pk_reservation'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reservation')
    op.drop_table('user')
    op.drop_table('parkinglot')
    # ### end Alembic commands ###
