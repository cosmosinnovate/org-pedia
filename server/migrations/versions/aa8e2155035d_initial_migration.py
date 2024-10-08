"""Initial migration

Revision ID: aa8e2155035d
Revises: 
Create Date: 2024-10-03 17:39:57.868056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa8e2155035d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('display_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('photo_url', sa.String(), nullable=True),
    sa.Column('access_token', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_display_name'), ['display_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)

    op.create_table('chat_history',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('messages', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('chat_history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_chat_history_created_at'), ['created_at'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chat_history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_chat_history_created_at'))

    op.drop_table('chat_history')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_email'))
        batch_op.drop_index(batch_op.f('ix_users_display_name'))

    op.drop_table('users')
    # ### end Alembic commands ###
