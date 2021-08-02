"""rates_table

Revision ID: 628277fd1cd3
Revises: b8fa6ea04422
Create Date: 2021-08-02 16:19:45.890742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '628277fd1cd3'
down_revision = 'b8fa6ea04422'
branch_labels = None
depends_on = None

tableName = "rates"

def upgrade():
    op.create_table(
        tableName,
        sa.MetaData(),
        sa.Column("id", sa.String(255), primary_key=True), 
        sa.Column("story_stars",sa.INTEGER()),
        sa.Column("actor_stars",sa.INTEGER()),
        sa.Column("sound_stars",sa.INTEGER()),
        sa.Column("univers_stars",sa.INTEGER()),
        sa.Column("movies_id",sa.String(255)),
        sa.Column("user_id",sa.String(255))
    )

def downgrade():
    op.drop_table(tableName)