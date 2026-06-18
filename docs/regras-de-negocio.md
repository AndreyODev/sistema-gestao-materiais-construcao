# Regras de Negocio

Este documento consolida as regras de negocio implementadas na API a partir da leitura de `app/services`, `app/schemas`, `app/core/handlers` e dos cenarios automatizados em `tests/test_system.py`.

## RN-001

**Identificador:** RN-001

**Nome:** Pedido so pode ser aprovado se possuir pelo menos um item

**Gatilho:** `POST /api/pedidos/{pedido_id}/aprovar`

**Pre-condicao:** O pedido deve existir, estar em `RASCUNHO` e possuir pelo menos um item associado.

**Acao:** O sistema altera o `status` do pedido para `APROVADO`.

**Violacao:**

- Se o pedido nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Pedido nao encontrado.",
  "details": {
    "id": "<pedido_id>"
  }
}
```

- Se o pedido nao possuir itens, a API retorna HTTP `400`, codigo interno `ORDER_WITHOUT_ITEMS` e payload:

```json
{
  "error": "ORDER_WITHOUT_ITEMS",
  "message": "Um pedido so pode ser aprovado se possuir pelo menos um item.",
  "details": {}
}
```

- Se o pedido estiver em estado terminal (`RECEBIDO` ou `CANCELADO`), a API retorna HTTP `409`, codigo interno `INVALID_ORDER_STATUS_TRANSITION` e payload:

```json
{
  "error": "INVALID_ORDER_STATUS_TRANSITION",
  "message": "Nao e permitido alterar pedidos em estado terminal.",
  "details": {
    "current_status": "<status_atual>"
  }
}
```

- Se o pedido estiver em qualquer outro estado diferente de `RASCUNHO`, a API retorna HTTP `409`, codigo interno `INVALID_ORDER_STATUS_TRANSITION` e payload:

```json
{
  "error": "INVALID_ORDER_STATUS_TRANSITION",
  "message": "Transicao de estado invalida para aprovacao.",
  "details": {
    "current_status": "<status_atual>"
  }
}
```

## RN-002

**Identificador:** RN-002

**Nome:** Pedido recebido nao pode ser cancelado

**Gatilho:** `POST /api/pedidos/{pedido_id}/cancelar`

**Pre-condicao:** O pedido deve existir.

**Acao:** Quando o pedido estiver em `RECEBIDO`, o sistema bloqueia o cancelamento e preserva o estado atual.

**Violacao:**

- Se o pedido nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Pedido nao encontrado.",
  "details": {
    "id": "<pedido_id>"
  }
}
```

- Se o pedido ja tiver sido recebido, a API retorna HTTP `409`, codigo interno `ORDER_ALREADY_RECEIVED` e payload:

```json
{
  "error": "ORDER_ALREADY_RECEIVED",
  "message": "Nao e permitido cancelar um pedido ja recebido.",
  "details": {}
}
```

## RN-003

**Identificador:** RN-003

**Nome:** Recebimento de pedido atualiza estoque e registra movimentacao de entrada

**Gatilho:** `POST /api/pedidos/{pedido_id}/receber`

**Pre-condicao:** O pedido deve existir, estar `APROVADO` e seus itens devem referenciar materiais validos.

**Acao:** Para cada item do pedido, o sistema localiza ou cria o estoque do material, soma a quantidade recebida em `quantidade_disponivel`, atualiza `ultima_movimentacao`, registra uma `movimentacao` do tipo `ENTRADA` e, ao final, marca o pedido como `RECEBIDO`.

**Violacao:**

- Se o pedido nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Pedido nao encontrado.",
  "details": {
    "id": "<pedido_id>"
  }
}
```

- Se ocorrer falha durante a atualizacao transacional do estoque no recebimento, a API retorna HTTP `400`, codigo interno `INVALID_STOCK_UPDATE` e payload:

```json
{
  "error": "INVALID_STOCK_UPDATE",
  "message": "Falha ao atualizar o estoque durante o recebimento do pedido.",
  "details": {
    "reason": "<mensagem_da_excecao_origem>"
  }
}
```

## RN-004

**Identificador:** RN-004

**Nome:** Quantidade deve ser positiva em item de pedido e saida de estoque

**Gatilho:** `POST /api/pedidos/{pedido_id}/itens` e `POST /api/estoque/saida`

**Pre-condicao:** O campo `quantidade` deve ser maior que zero.

**Acao:** O sistema aceita a operacao somente quando a quantidade enviada e positiva.

**Violacao:**

- Se a quantidade informada for menor ou igual a zero, a API retorna HTTP `422`, codigo interno `INVALID_QUANTITY` e payload no formato abaixo. O campo `input` replica exatamente o valor invalido enviado na requisicao:

```json
{
  "error": "INVALID_QUANTITY",
  "message": "Quantidade deve ser positiva.",
  "details": {
    "rule": "RN-004",
    "errors": [
      {
        "type": "value_error",
        "loc": ["body", "quantidade"],
        "msg": "Value error, Quantidade deve ser positiva.",
        "input": -10,
        "ctx": {
          "error": "Quantidade deve ser positiva."
        },
        "url": "https://errors.pydantic.dev/2.10/v/value_error"
      }
    ]
  }
}
```

## RN-005

**Identificador:** RN-005

**Nome:** Fornecedor nao pode ser cadastrado ou atualizado com CNPJ duplicado

**Gatilho:** `POST /api/fornecedores` e `PUT /api/fornecedores/{fornecedor_id}`

**Pre-condicao:** O CNPJ informado, apos a normalizacao para somente digitos, nao pode pertencer a outro fornecedor.

**Acao:** O sistema persiste o fornecedor somente quando o CNPJ e unico.

**Violacao:**

- Se o CNPJ ja estiver associado a outro fornecedor, a API retorna HTTP `409`, codigo interno `SUPPLIER_ALREADY_EXISTS` e payload:

```json
{
  "error": "SUPPLIER_ALREADY_EXISTS",
  "message": "Ja existe fornecedor cadastrado com este CNPJ.",
  "details": {}
}
```

## RN-006

**Identificador:** RN-006

**Nome:** Saida de estoque nao pode deixar saldo negativo

**Gatilho:** `POST /api/estoque/saida`

**Pre-condicao:** O material deve existir, a quantidade deve ser positiva e o saldo atual deve ser maior ou igual a quantidade solicitada.

**Acao:** O sistema subtrai a quantidade do estoque, atualiza `ultima_movimentacao` e registra uma `movimentacao` do tipo `SAIDA`.

**Violacao:**

- Se o material nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Material nao encontrado.",
  "details": {
    "id": "<material_id>"
  }
}
```

- Se a quantidade informada for menor ou igual a zero, a API retorna HTTP `422`, codigo interno `INVALID_QUANTITY` e payload no formato abaixo. O campo `input` replica exatamente o valor invalido enviado na requisicao:

```json
{
  "error": "INVALID_QUANTITY",
  "message": "Quantidade deve ser positiva.",
  "details": {
    "rule": "RN-004",
    "errors": [
      {
        "type": "value_error",
        "loc": ["body", "quantidade"],
        "msg": "Value error, Quantidade deve ser positiva.",
        "input": 0,
        "ctx": {
          "error": "Quantidade deve ser positiva."
        },
        "url": "https://errors.pydantic.dev/2.10/v/value_error"
      }
    ]
  }
}
```

- Se a saida solicitada for maior que o saldo disponivel, a API retorna HTTP `409`, codigo interno `INSUFFICIENT_STOCK` e payload:

```json
{
  "error": "INSUFFICIENT_STOCK",
  "message": "Nao permitir movimentacao de saida que deixe o estoque negativo.",
  "details": {
    "available": "<saldo_disponivel>",
    "requested": "<quantidade_solicitada>"
  }
}
```

## RN-007

**Identificador:** RN-007

**Nome:** Valor total do pedido e calculado automaticamente pela soma dos subtotais

**Gatilho:** `POST /api/pedidos/{pedido_id}/itens`

**Pre-condicao:** O pedido deve existir, estar em `RASCUNHO`, o material deve existir e a quantidade deve ser positiva.

**Acao:** Apos a inclusao de um item, o sistema recalcula `valor_total` pela soma de todos os `subtotal` existentes no pedido.

**Violacao:**

- Se o pedido nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Pedido nao encontrado.",
  "details": {
    "id": "<pedido_id>"
  }
}
```

- Se o pedido existir, mas nao estiver em `RASCUNHO`, a API retorna HTTP `409`, codigo interno `INVALID_ORDER_STATUS_TRANSITION` e payload:

```json
{
  "error": "INVALID_ORDER_STATUS_TRANSITION",
  "message": "Apenas pedidos em rascunho podem ser alterados.",
  "details": {
    "current_status": "<status_atual>"
  }
}
```

- Se o material do item nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Material nao encontrado.",
  "details": {
    "id": "<material_id>"
  }
}
```

- Se a quantidade informada for menor ou igual a zero, a API retorna HTTP `422`, codigo interno `INVALID_QUANTITY` e payload:

```json
{
  "error": "INVALID_QUANTITY",
  "message": "Quantidade deve ser positiva.",
  "details": {
    "rule": "RN-004",
    "errors": [
      {
        "type": "value_error",
        "loc": ["body", "quantidade"],
        "msg": "Value error, Quantidade deve ser positiva.",
        "input": -10,
        "ctx": {
          "error": "Quantidade deve ser positiva."
        },
        "url": "https://errors.pydantic.dev/2.10/v/value_error"
      }
    ]
  }
}
```

## RN-008

**Identificador:** RN-008

**Nome:** Subtotal do item e calculado automaticamente como quantidade vezes preco unitario

**Gatilho:** `POST /api/pedidos/{pedido_id}/itens`

**Pre-condicao:** O pedido deve existir, estar em `RASCUNHO`, o material deve existir e a quantidade deve ser positiva.

**Acao:** Ao adicionar um item, o sistema persiste `subtotal = quantidade * preco_unitario`.

**Violacao:**

- Se o pedido nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Pedido nao encontrado.",
  "details": {
    "id": "<pedido_id>"
  }
}
```

- Se o pedido existir, mas nao estiver em `RASCUNHO`, a API retorna HTTP `409`, codigo interno `INVALID_ORDER_STATUS_TRANSITION` e payload:

```json
{
  "error": "INVALID_ORDER_STATUS_TRANSITION",
  "message": "Apenas pedidos em rascunho podem ser alterados.",
  "details": {
    "current_status": "<status_atual>"
  }
}
```

- Se o material do item nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Material nao encontrado.",
  "details": {
    "id": "<material_id>"
  }
}
```

- Se a quantidade informada for menor ou igual a zero, a API retorna HTTP `422`, codigo interno `INVALID_QUANTITY` e payload:

```json
{
  "error": "INVALID_QUANTITY",
  "message": "Quantidade deve ser positiva.",
  "details": {
    "rule": "RN-004",
    "errors": [
      {
        "type": "value_error",
        "loc": ["body", "quantidade"],
        "msg": "Value error, Quantidade deve ser positiva.",
        "input": -10,
        "ctx": {
          "error": "Quantidade deve ser positiva."
        },
        "url": "https://errors.pydantic.dev/2.10/v/value_error"
      }
    ]
  }
}
```

## RN-009

**Identificador:** RN-009

**Nome:** Pedido de compra deve ser criado com fornecedor existente e iniciar em rascunho

**Gatilho:** `POST /api/pedidos`

**Pre-condicao:** O `fornecedor_id` informado deve existir.

**Acao:** O sistema cria o pedido com `status = RASCUNHO`, `valor_total = 0.00` e `observacao` saneada pelo schema de entrada.

**Violacao:**

- Se o fornecedor nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Fornecedor nao encontrado.",
  "details": {
    "id": "<fornecedor_id>"
  }
}
```

## RN-010

**Identificador:** RN-010

**Nome:** Pedido so pode ser alterado enquanto estiver em rascunho

**Gatilho:** `PUT /api/pedidos/{pedido_id}`, `DELETE /api/pedidos/{pedido_id}` e `POST /api/pedidos/{pedido_id}/itens`

**Pre-condicao:** O pedido deve existir e estar com `status = RASCUNHO`.

**Acao:** O sistema permite atualizar, excluir ou adicionar itens apenas em pedidos em rascunho.

**Violacao:**

- Se o pedido nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Pedido nao encontrado.",
  "details": {
    "id": "<pedido_id>"
  }
}
```

- Se o pedido existir, mas nao estiver em `RASCUNHO`, a API retorna HTTP `409`, codigo interno `INVALID_ORDER_STATUS_TRANSITION` e payload:

```json
{
  "error": "INVALID_ORDER_STATUS_TRANSITION",
  "message": "Apenas pedidos em rascunho podem ser alterados.",
  "details": {
    "current_status": "<status_atual>"
  }
}
```

## RN-011

**Identificador:** RN-011

**Nome:** Pedido so pode ser recebido uma vez e somente quando estiver aprovado

**Gatilho:** `POST /api/pedidos/{pedido_id}/receber`

**Pre-condicao:** O pedido deve existir e estar com `status = APROVADO`.

**Acao:** O sistema processa o recebimento e altera o `status` do pedido para `RECEBIDO`.

**Violacao:**

- Se o pedido nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Pedido nao encontrado.",
  "details": {
    "id": "<pedido_id>"
  }
}
```

- Se o pedido ja tiver sido recebido anteriormente, a API retorna HTTP `409`, codigo interno `ORDER_ALREADY_RECEIVED` e payload:

```json
{
  "error": "ORDER_ALREADY_RECEIVED",
  "message": "Nao e permitido receber um pedido ja recebido.",
  "details": {}
}
```

- Se o pedido estiver cancelado, a API retorna HTTP `409`, codigo interno `INVALID_ORDER_STATUS_TRANSITION` e payload:

```json
{
  "error": "INVALID_ORDER_STATUS_TRANSITION",
  "message": "Nao e permitido receber um pedido cancelado.",
  "details": {
    "current_status": "CANCELADO"
  }
}
```

- Se o pedido existir, mas nao estiver aprovado, a API retorna HTTP `409`, codigo interno `INVALID_ORDER_STATUS_TRANSITION` e payload:

```json
{
  "error": "INVALID_ORDER_STATUS_TRANSITION",
  "message": "Somente pedidos aprovados podem ser recebidos.",
  "details": {
    "current_status": "<status_atual>"
  }
}
```

## RN-012

**Identificador:** RN-012

**Nome:** Material deve possuir estoque associado

**Gatilho:** `POST /api/materiais`, `GET /api/estoque/{material_id}` e `POST /api/estoque/saida`

**Pre-condicao:** O material deve existir.

**Acao:** Ao cadastrar um material, o sistema cria automaticamente um registro de estoque. Ao consultar o estoque ou registrar saida para um material existente sem estoque previo, o sistema cria o estoque com saldo inicial `0.00` antes de prosseguir.

**Violacao:**

- Se o material nao existir, a API retorna HTTP `404`, codigo interno `RESOURCE_NOT_FOUND` e payload:

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "Material nao encontrado.",
  "details": {
    "id": "<material_id>"
  }
}
```
