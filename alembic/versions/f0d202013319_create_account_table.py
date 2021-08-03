"""create account table

Revision ID: f0d202013319
Revises: 
Create Date: 2021-07-27 00:24:15.954038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0d202013319'
down_revision = None
branch_labels = None
depends_on = None
tableName = "SUPERBD"

def upgrade():
    op.create_table(
        tableName, 
        sa.Column("username",
        sa.String(255))
    )

def downgrade():
    op.drop_table(tableName)
