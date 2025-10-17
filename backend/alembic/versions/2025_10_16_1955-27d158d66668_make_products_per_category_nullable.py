"""make_products_per_category_nullable

Revision ID: 27d158d66668
Revises: 37c6edc65f51
Create Date: 2025-10-16 19:55:09.231371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27d158d66668'
down_revision = '37c6edc65f51'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Hacer products_per_category nullable
    op.alter_column('importer_configs', 'products_per_category',
                    existing_type=sa.Integer(),
                    nullable=True,
                    existing_server_default=sa.text('100'))

    # Actualizar valores existentes de 100 a NULL para indicar "sin límite"
    # Si prefieres mantener el 100 como límite actual, comenta la siguiente línea
    op.execute("UPDATE importer_configs SET products_per_category = NULL WHERE products_per_category = 100")


def downgrade() -> None:
    # Restaurar valores NULL a 100 antes de hacer la columna NOT NULL
    op.execute("UPDATE importer_configs SET products_per_category = 100 WHERE products_per_category IS NULL")

    # Hacer products_per_category NOT NULL otra vez
    op.alter_column('importer_configs', 'products_per_category',
                    existing_type=sa.Integer(),
                    nullable=False,
                    existing_server_default=sa.text('100'))
