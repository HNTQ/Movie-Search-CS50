"""lists_table

Revision ID: 24dfa943a7d2
Revises: 628277fd1cd3
Create Date: 2021-08-02 16:19:57.356476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24dfa943a7d2'
down_revision = '628277fd1cd3'
branch_labels = None
depends_on = None

tableName = "lists"

def upgrade():
    op.create_table(
        tableName,
        sa.MetaData(),
        sa.Column("id", sa.String(255), primary_key=True), 
        sa.Column("name",sa.String(40)),
        sa.Column("category",sa.String(40)),
        sa.Column("user_id",sa.String(255))        
    )

def downgrade():
    op.drop_table(tableName)