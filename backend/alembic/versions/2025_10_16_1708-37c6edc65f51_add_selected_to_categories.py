"""add_selected_to_categories

Revision ID: 37c6edc65f51
Revises: a4e1a42328f3
Create Date: 2025-10-16 17:08:16.337066

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "37c6edc65f51"
down_revision = "a4e1a42328f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columna 'selected' a la tabla categories
    op.add_column(
        "categories",
        sa.Column("selected", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    # Eliminar columna 'selected' de la tabla categories
    op.drop_column("categories", "selected")
