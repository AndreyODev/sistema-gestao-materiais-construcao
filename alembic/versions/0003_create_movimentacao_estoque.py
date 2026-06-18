from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_create_movimentacao_estoque"
down_revision = "0002_add_supplier_cnpj_index"
branch_labels = None
depends_on = None

tipo_movimentacao = sa.Enum("ENTRADA", "SAIDA", name="tipo_movimentacao")


def upgrade() -> None:
    op.create_table(
        "movimentacoes_estoque",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("material_id", sa.Integer(), sa.ForeignKey("materiais.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("tipo_movimentacao", tipo_movimentacao, nullable=False),
        sa.Column("quantidade", sa.Numeric(12, 2), nullable=False),
        sa.Column("data_movimentacao", sa.DateTime(), nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("movimentacoes_estoque")
    tipo_movimentacao.drop(op.get_bind(), checkfirst=True)
