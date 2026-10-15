"""Добавление телефона читателю"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"

def upgrade():
    op.add_column("readers", sa.Column("phone", sa.String(20), nullable=True))


def downgrade():
    op.drop_column("readers", "phone")
