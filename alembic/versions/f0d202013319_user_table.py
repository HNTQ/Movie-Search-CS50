"""user_table

Revision ID: f0d202013319
Revises: 
Create Date: 2021-07-27 00:24:15.954038

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f0d202013319"
down_revision = None
branch_labels = None
depends_on = None

tableName = "user"


def upgrade():

    op.create_table(
        tableName,
        sa.MetaData(),
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("username", sa.String(255)),
        sa.Column("email", sa.String(255)),
        sa.Column("hash", sa.String(255)),
        sa.Column("create_time", sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column("active", sa.BOOLEAN(), server_default="0"),
    )


def downgrade():
    op.drop_table(tableName)
