"""movies_table

Revision ID: db981cb9dfed
Revises: 24dfa943a7d2
Create Date: 2021-08-02 16:20:10.919320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "db981cb9dfed"
down_revision = "24dfa943a7d2"
branch_labels = None
depends_on = None

tableName = "movies"


def upgrade():
    op.create_table(
        tableName,
        sa.MetaData(),
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("movie_tmdb_id", sa.INTEGER()),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.String(255)),
        sa.Column("duration", sa.String(80)),
        sa.Column("poster", sa.String(255)),
    )


def downgrade():
    op.drop_table(tableName)
