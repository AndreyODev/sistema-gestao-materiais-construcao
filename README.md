# Sistema de Gestão de Materiais de Construção e Controle de Compras

Este projeto foi desenvolvido para auxiliar no controle de materiais utilizados em obras, permitindo o gerenciamento de fornecedores, pedidos de compra, estoque e movimentações de entrada e saída de materiais.

O objetivo do sistema é garantir que o estoque seja atualizado de forma consistente, evitando compras indevidas, recebimentos duplicados e movimentações sem rastreabilidade.

A aplicação foi construída utilizando FastAPI, SQLAlchemy, PostgreSQL, Docker, Alembic e Pydantic v2, seguindo uma arquitetura em camadas para separar responsabilidades entre a API, as regras de negócio e o acesso aos dados.

# Contexto do Domínio

Em um cenário de construção civil, diversos materiais precisam ser adquiridos de fornecedores e controlados em estoque.
Para atender esse processo, o sistema permite:

- Cadastro de materiais de construção;
- Cadastro e gerenciamento de fornecedores;
- Criação de pedidos de compra contendo um ou mais itens;
- Controle do ciclo de vida dos pedidos;
- Atualização automática do estoque após o recebimento dos materiais;
- Registro das movimentações para auditoria e rastreabilidade.

O sistema foi projetado para evitar inconsistências por meio de validações e regras específicas, como:

- Bloqueio de alterações em pedidos finalizados;
- Impedimento de recebimento duplicado;
- Controle para impedir estoque negativo;
- Garantia de unicidade de fornecedores por CNPJ;
- Recalculo automático dos valores financeiros do pedido.

# Objetivos Técnicos

Além das funcionalidades do domínio, o projeto também teve como objetivo aplicar conceitos de engenharia de software:

- Arquitetura em camadas (routers → services → repositories);
- Persistência utilizando ORM SQLAlchemy;
- Controle de versão do banco com Alembic;
- Transações com commit e rollback;
- Validações utilizando Pydantic v2;
- Testes automatizados com Pytest;
- Controle de regras de negócio através de máquina de estados.

### Entidades

- Material
- Fornecedor
- Estoque
- PedidoCompra
- ItemPedido
- MovimentacaoEstoque

# Relacionamentos

- Fornecedor → PedidoCompra (1:N)
- PedidoCompra → ItemPedido (1:N)
- Material → Estoque (1:1)
- Material → MovimentacaoEstoque (1:N)

### Diagrama ER em ASCII

```text
+------------------+       +---------------------+
|   fornecedores   |1     N|   pedidos_compra    |
+------------------+-------+---------------------+
| id               |       | id                  |
| razao_social     |       | fornecedor_id (FK)  |
| cnpj             |       | data_criacao        |
| telefone         |       | valor_total         |
| email            |       | status              |
| ativo            |       | observacao          |
+------------------+       +----------+----------+
                                       |1
                                       |
                                       |N
                            +----------v----------+
                            |    itens_pedido     |
                            +---------------------+
                            | id                  |
                            | pedido_id (FK)      |
                            | material_id (FK)    |
                            | quantidade          |
                            | preco_unitario      |
                            | subtotal            |
                            +----------+----------+
                                       |
                                       |N
                                       |1
+------------------+       +----------v----------+       +---------------------------+
|    materiais     |1     1|       estoques      |       | movimentacoes_estoque     |
+------------------+-------+---------------------+-------+---------------------------+
| id               |       | id                  |1     N| id                        |
| nome             |       | material_id (FK)    |       | material_id (FK)          |
| descricao        |       | quantidade_disp.    |       | tipo_movimentacao         |
| unidade_medida   |       | ultima_movimentacao |       | quantidade                |
| estoque_minimo   |       +---------------------+       | data_movimentacao         |
| preco_medio      |                                     | observacao                |
| ativo            |                                     +---------------------------+
+------------------+
```

## Regras de negocio

- RN-001: um pedido so pode ser aprovado se possuir pelo menos um item. Erro `ORDER_WITHOUT_ITEMS`.
- RN-002: nao e permitido cancelar um pedido ja recebido. Erro `ORDER_ALREADY_RECEIVED`.
- RN-003: ao receber um pedido, o estoque e atualizado automaticamente e uma movimentacao de entrada e registrada. Erro `INVALID_STOCK_UPDATE` em falhas transacionais.
- RN-004: quantidade de `ItemPedido` deve ser positiva. Erro `INVALID_QUANTITY` representado via validacao da API.
- RN-005: nao permitir fornecedor com CNPJ duplicado. Erro `SUPPLIER_ALREADY_EXISTS`.
- RN-006: nao permitir saida que deixe estoque negativo. Erro `INSUFFICIENT_STOCK`.
- RN-007: `valor_total` do pedido e calculado automaticamente como soma dos subtotais.
- RN-008: `subtotal` do item e calculado automaticamente como `quantidade * preco_unitario`.

## Maquina de estados do pedido

- `RASCUNHO -> APROVADO`
- `APROVADO -> RECEBIDO`
- `RASCUNHO -> CANCELADO`
- `APROVADO -> CANCELADO`
- Estados terminais: `RECEBIDO`, `CANCELADO`
- Nao ha retorno a partir de estados terminais

## Cenarios de borda

- Pedido sem itens sendo aprovado retorna `ORDER_WITHOUT_ITEMS`.
- Recebimento duplicado do mesmo pedido retorna `ORDER_ALREADY_RECEIVED`.
- Saida de estoque superior ao saldo disponivel retorna `INSUFFICIENT_STOCK`.
- Todas as respostas de erro seguem o padrao:

```json
{
  "error": "ERROR_CODE",
  "message": "Mensagem",
  "details": {}
}
```

## Decisoes de design

- Arquitetura em camadas: `routers` apenas recebem requisicoes e delegam para `services`; regras de negocio ficam centralizadas em services; persistencia fica em `repositories`.
- Modelagem transacional: recebimento de pedido e saida de estoque sao operacoes transacionais com `commit` e `rollback` explicitos.
- Estoque 1:1 com material: um registro de estoque e criado automaticamente no cadastro do material.
- Auditoria: toda entrada por recebimento e toda saida manual geram registros em `movimentacoes_estoque`.
- Alembic incremental: as migrations foram separadas para atender os requisitos academicos de evolucao do schema.
- Migration 2: o indice `ix_fornecedores_cnpj` foi criado por causa da RN-005, ja que a verificacao de duplicidade consulta o CNPJ com alta frequencia.
- Banco isolado para testes: o `docker-compose` sobe um banco PostgreSQL secundario (`materials_test`) acessado por `TEST_DATABASE_URL`.
- Validacoes Pydantic v2: `field_validator` e `model_validator` foram aplicados em schemas de entrada.

## Estrutura

```text
app/
  main.py
  core/
  models/
  repositories/
  routers/
  schemas/
  services/
tests/
alembic/
Dockerfile
docker-compose.yml
README.md
```

## Endpoints

### Materiais

- `POST /api/materiais`
- `GET /api/materiais?nome=&ativo=&limit=&offset=`
- `GET /api/materiais/{id}`
- `PUT /api/materiais/{id}`
- `DELETE /api/materiais/{id}`

### Fornecedores

- `POST /api/fornecedores`
- `GET /api/fornecedores`
- `GET /api/fornecedores/{id}`
- `PUT /api/fornecedores/{id}`
- `DELETE /api/fornecedores/{id}`

### Pedidos

- `POST /api/pedidos`
- `GET /api/pedidos?status=&fornecedor_id=`
- `GET /api/pedidos/{id}`
- `PUT /api/pedidos/{id}`
- `DELETE /api/pedidos/{id}`
- `POST /api/pedidos/{id}/itens`
- `POST /api/pedidos/{id}/aprovar`
- `POST /api/pedidos/{id}/receber`
- `POST /api/pedidos/{id}/cancelar`

### Estoque

- `GET /api/estoque/{material_id}`
- `POST /api/estoque/saida`

### Movimentacoes

- `GET /api/movimentacoes`

# Como Executar

## Clonar

```bash
git clone URL_DO_REPOSITORIO
```

## Configurar ambiente

```bash
cp .env.example .env
```

## Subir aplicação

```bash
docker compose up --build
```

3. Acesse:

- API: <http://localhost:8000>
- Docs Swagger: <http://localhost:8000/docs>
- Adminer: <http://localhost:8080>

# Migrações

Aplicar:

```bash
docker compose run --rm api alembic upgrade head
```

Ver histórico:

```bash
docker compose run --rm api alembic history
```

Ver atual:

```bash
docker compose run --rm api alembic current
```

Rollback:

```bash
docker compose run --rm api alembic downgrade -1
```

# Testes

Executar:

```bash
docker compose run --rm api pytest
```

Os testes cobrem no minimo os cenarios abaixo:

- aprovacao valida
- aprovacao invalida
- cancelamento valido
- cancelamento invalido
- recebimento valido
- recebimento duplicado
- estoque atualizado apos recebimento
- estoque insuficiente
- CNPJ duplicado
- calculo de valor total

Banco de testes isolado:

```text
TEST_DATABASE_URL
```
