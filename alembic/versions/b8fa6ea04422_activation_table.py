"""activation_table

Revision ID: b8fa6ea04422
Revises: f0d202013319
Create Date: 2021-08-02 16:16:43.337397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b8fa6ea04422"
down_revision = "f0d202013319"
branch_labels = None
depends_on = None

tableName = "activation"


def upgrade():
    op.create_table(
        tableName,
        sa.MetaData(),
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("user_id", sa.String(255), sa.ForeignKey("users.id",ondelete="CASCADE")),
        sa.Column("activation_code", sa.String(8))
    )
    
def downgrade():
    op.drop_table(tableName)
