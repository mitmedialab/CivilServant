"""add twitter status table

Revision ID: 9b5335a74312
Revises: 8e190130ba36
Create Date: 2017-04-16 18:01:03.226479

"""

# revision identifiers, used by Alembic.
revision = '9b5335a74312'
down_revision = '8e190130ba36'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_development():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('twitter_statuses',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('in_reply_to_user_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('favorite_count', sa.Integer(), nullable=True),
    sa.Column('retweet_count', sa.Integer(), nullable=True),
    sa.Column('retweeted', sa.Boolean(), nullable=True),
    sa.Column('status_data', mysql.MEDIUMTEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade_development():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('twitter_statuses')
    # ### end Alembic commands ###


def upgrade_test():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('twitter_statuses',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('in_reply_to_user_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('favorite_count', sa.Integer(), nullable=True),
    sa.Column('retweet_count', sa.Integer(), nullable=True),
    sa.Column('retweeted', sa.Boolean(), nullable=True),
    sa.Column('status_data', mysql.MEDIUMTEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade_test():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('twitter_statuses')
    # ### end Alembic commands ###


def upgrade_production():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('twitter_statuses',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('in_reply_to_user_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('favorite_count', sa.Integer(), nullable=True),
    sa.Column('retweet_count', sa.Integer(), nullable=True),
    sa.Column('retweeted', sa.Boolean(), nullable=True),
    sa.Column('status_data', mysql.MEDIUMTEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade_production():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('twitter_statuses')
    # ### end Alembic commands ###

