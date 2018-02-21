"""empty message

Revision ID: c5f055537ca4
Revises: 
Create Date: 2018-02-08 17:17:15.857704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5f055537ca4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('aj_table',
    sa.Column('tid', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=True),
    sa.Column('flag', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('tid'),
    sa.UniqueConstraint('name')
    )
    op.create_table('bill',
    sa.Column('bid', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('payment_mode', sa.Enum('Cash', 'Card'), nullable=False),
    sa.Column('discount', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('bid')
    )
    op.create_table('category',
    sa.Column('cid', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('cid'),
    sa.UniqueConstraint('name')
    )
    op.create_table('item',
    sa.Column('iid', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.Column('cost', sa.Integer(), nullable=False),
    sa.Column('flag', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('iid'),
    sa.UniqueConstraint('name')
    )
    op.create_table('kot',
    sa.Column('kid', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('flag', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('kid')
    )
    op.create_table('sub_item',
    sa.Column('sid', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=True),
    sa.Column('flag', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('sid'),
    sa.UniqueConstraint('name')
    )
    op.create_table('item_category',
    sa.Column('cid', sa.Integer(), nullable=False),
    sa.Column('iid', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cid'], ['category.cid'], ),
    sa.ForeignKeyConstraint(['iid'], ['item.iid'], ),
    sa.PrimaryKeyConstraint('cid', 'iid')
    )
    op.create_table('order',
    sa.Column('kid', sa.Integer(), nullable=False),
    sa.Column('tid', sa.Integer(), nullable=False),
    sa.Column('iid', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('flag', sa.Boolean(), nullable=False),
    sa.Column('message', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['iid'], ['item.iid'], ),
    sa.ForeignKeyConstraint(['kid'], ['kot.kid'], ),
    sa.ForeignKeyConstraint(['tid'], ['aj_table.tid'], ),
    sa.PrimaryKeyConstraint('kid', 'tid', 'iid')
    )
    op.create_table('sub_item_category',
    sa.Column('cid', sa.Integer(), nullable=False),
    sa.Column('sid', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['cid'], ['category.cid'], ),
    sa.ForeignKeyConstraint(['sid'], ['sub_item.sid'], ),
    sa.PrimaryKeyConstraint('cid', 'sid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sub_item_category')
    op.drop_table('order')
    op.drop_table('item_category')
    op.drop_table('sub_item')
    op.drop_table('kot')
    op.drop_table('item')
    op.drop_table('category')
    op.drop_table('bill')
    op.drop_table('aj_table')
    # ### end Alembic commands ###
