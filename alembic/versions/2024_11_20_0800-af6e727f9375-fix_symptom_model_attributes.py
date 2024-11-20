"""Fix Symptom model attributes

Revision ID: af6e727f9375
Revises: 7a73824e7f41
Create Date: 2024-11-20 08:00:02.138672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af6e727f9375'
down_revision = '7a73824e7f41'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('symptom', sa.Column('code', sa.String(length=100), nullable=True))
    op.add_column('symptom', sa.Column('name', sa.String(length=100), nullable=True))
    op.execute("UPDATE symptom SET code = 'DEFAULT_CODE' WHERE code IS NULL")
    op.execute("UPDATE symptom SET name = 'DEFAULT_NAME' WHERE name IS NULL")
    op.alter_column('symptom', 'code', nullable=False)
    op.alter_column('symptom', 'name', nullable=False)
    op.drop_column('symptom', 'symptom_name')
    op.drop_column('symptom', 'symptom_code')
    op.create_unique_constraint(None, 'business', ['id'])
    op.create_unique_constraint(None, 'symptom', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('symptom', sa.Column('symptom_code', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
    op.add_column('symptom', sa.Column('symptom_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'symptom', type_='unique')
    op.drop_column('symptom', 'name')
    op.drop_column('symptom', 'code')
    op.drop_constraint(None, 'business', type_='unique')
    # ### end Alembic commands ###