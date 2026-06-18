from __future__ import annotations

from alembic import op

revision = "0002_add_supplier_cnpj_index"
down_revision = "0001_initial_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_fornecedores_cnpj", "fornecedores", ["cnpj"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_fornecedores_cnpj", table_name="fornecedores")
