"""Update Order model for Product Variable

Revision ID: 47fdea7bb183
Revises: a9d09d1645d0
Create Date: 2025-07-19 14:48:48.560739

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47fdea7bb183'
down_revision = 'a9d09d1645d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_variant_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_order_product_variant_id', 'product_variant', ['product_variant_id'], ['id'])
        batch_op.drop_column('product')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product', sa.VARCHAR(length=255), nullable=False))
        batch_op.drop_constraint('fk_order_product_variant_id', type_='foreignkey')
        batch_op.drop_column('product_variant_id')

    # ### end Alembic commands ###
