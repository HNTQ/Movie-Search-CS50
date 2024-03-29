"""lists_medias_table

Revision ID: e0042d1d1b53
Revises: db981cb9dfed
Create Date: 2021-08-02 16:20:28.483478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e0042d1d1b53"
down_revision = "db981cb9dfed"
branch_labels = None
depends_on = None

tableName = "lists_medias"


def upgrade():
    op.create_table(
        tableName,
        sa.MetaData(),
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("list_id", sa.String(255), sa.ForeignKey("lists.id", ondelete="CASCADE")),
        sa.Column("media_id", sa.String(255), sa.ForeignKey("medias.id", ondelete="CASCADE")),
    )


def downgrade():
    op.drop_table(tableName)
