from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_tables"
down_revision = None
branch_labels = None
depends_on = None

status_pedido = sa.Enum("RASCUNHO", "APROVADO", "RECEBIDO", "CANCELADO", name="status_pedido")


def upgrade() -> None:
    op.create_table(
        "fornecedores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("razao_social", sa.String(length=160), nullable=False),
        sa.Column("cnpj", sa.String(length=14), nullable=False),
        sa.Column("telefone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "materiais",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("unidade_medida", sa.String(length=20), nullable=False),
        sa.Column("estoque_minimo", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("preco_medio", sa.Numeric(12, 2), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_materiais_nome", "materiais", ["nome"], unique=False)

    op.create_table(
        "pedidos_compra",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fornecedor_id", sa.Integer(), sa.ForeignKey("fornecedores.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("data_criacao", sa.DateTime(), nullable=False),
        sa.Column("valor_total", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("status", status_pedido, nullable=False, server_default="RASCUNHO"),
        sa.Column("observacao", sa.Text(), nullable=True),
    )

    op.create_table(
        "estoques",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("material_id", sa.Integer(), sa.ForeignKey("materiais.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantidade_disponivel", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("ultima_movimentacao", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("material_id", name="uq_estoques_material_id"),
    )

    op.create_table(
        "itens_pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedidos_compra.id", ondelete="CASCADE"), nullable=False),
        sa.Column("material_id", sa.Integer(), sa.ForeignKey("materiais.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantidade", sa.Numeric(12, 2), nullable=False),
        sa.Column("preco_unitario", sa.Numeric(12, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(14, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("itens_pedido")
    op.drop_table("estoques")
    op.drop_table("pedidos_compra")
    op.drop_index("ix_materiais_nome", table_name="materiais")
    op.drop_table("materiais")
    op.drop_table("fornecedores")
    status_pedido.drop(op.get_bind(), checkfirst=True)
