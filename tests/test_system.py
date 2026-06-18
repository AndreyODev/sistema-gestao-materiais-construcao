def create_supplier(client, cnpj: str = "12345678000195") -> dict:
    response = client.post(
        "/api/fornecedores",
        json={
            "razao_social": "Fornecedor Alpha",
            "cnpj": cnpj,
            "telefone": "11999999999",
            "email": "contato@alpha.com",
            "ativo": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_material(client, nome: str = "Cimento CP2") -> dict:
    response = client.post(
        "/api/materiais",
        json={
            "nome": nome,
            "descricao": "Material de construcao",
            "unidade_medida": "saco",
            "estoque_minimo": 10,
            "preco_medio": 35.5,
            "ativo": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_order(client, fornecedor_id: int) -> dict:
    response = client.post(
        "/api/pedidos",
        json={"fornecedor_id": fornecedor_id, "observacao": "Pedido inicial"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def add_item(client, pedido_id: int, material_id: int, quantidade: float = 5, preco_unitario: float = 12) -> dict:
    response = client.post(
        f"/api/pedidos/{pedido_id}/itens",
        json={
            "material_id": material_id,
            "quantidade": quantidade,
            "preco_unitario": preco_unitario,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def approve_order(client, pedido_id: int):
    return client.post(f"/api/pedidos/{pedido_id}/aprovar")


def receive_order(client, pedido_id: int):
    return client.post(f"/api/pedidos/{pedido_id}/receber")


def test_aprovacao_valida(client):
    fornecedor = create_supplier(client)
    material = create_material(client)
    pedido = create_order(client, fornecedor["id"])
    add_item(client, pedido["id"], material["id"], quantidade=3, preco_unitario=25)

    response = approve_order(client, pedido["id"])

    assert response.status_code == 200
    assert response.json()["status"] == "APROVADO"


def test_aprovacao_invalida_sem_itens(client):
    fornecedor = create_supplier(client)
    pedido = create_order(client, fornecedor["id"])

    response = approve_order(client, pedido["id"])

    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "ORDER_WITHOUT_ITEMS"


def test_adicao_item_com_quantidade_negativa_retorna_erro_de_validacao(client):
    fornecedor = create_supplier(client)
    material = create_material(client)
    pedido = create_order(client, fornecedor["id"])

    response = client.post(
        f"/api/pedidos/{pedido['id']}/itens",
        json={
            "material_id": material["id"],
            "quantidade": -10,
            "preco_unitario": 45,
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "INVALID_QUANTITY"
    assert body["details"]["rule"] == "RN-004"
    assert any(error["loc"][-1] == "quantidade" for error in body["details"]["errors"])


def test_cancelamento_valido(client):
    fornecedor = create_supplier(client)
    pedido = create_order(client, fornecedor["id"])

    response = client.post(f"/api/pedidos/{pedido['id']}/cancelar")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELADO"


def test_cancelamento_invalido_pedido_recebido(client):
    fornecedor = create_supplier(client)
    material = create_material(client)
    pedido = create_order(client, fornecedor["id"])
    add_item(client, pedido["id"], material["id"], quantidade=4, preco_unitario=18)
    approve_order(client, pedido["id"])
    receive_order(client, pedido["id"])

    response = client.post(f"/api/pedidos/{pedido['id']}/cancelar")

    assert response.status_code == 409
    assert response.json()["error"] == "ORDER_ALREADY_RECEIVED"


def test_recebimento_valido(client):
    fornecedor = create_supplier(client)
    material = create_material(client)
    pedido = create_order(client, fornecedor["id"])
    add_item(client, pedido["id"], material["id"], quantidade=2, preco_unitario=40)
    approve_order(client, pedido["id"])

    response = receive_order(client, pedido["id"])

    assert response.status_code == 200
    assert response.json()["status"] == "RECEBIDO"


def test_recebimento_duplicado(client):
    fornecedor = create_supplier(client)
    material = create_material(client)
    pedido = create_order(client, fornecedor["id"])
    add_item(client, pedido["id"], material["id"], quantidade=2, preco_unitario=40)
    approve_order(client, pedido["id"])
    first_receive = receive_order(client, pedido["id"])
    assert first_receive.status_code == 200

    second_receive = receive_order(client, pedido["id"])

    assert second_receive.status_code == 409
    assert second_receive.json()["error"] == "ORDER_ALREADY_RECEIVED"


def test_estoque_atualizado_apos_recebimento(client):
    fornecedor = create_supplier(client)
    material = create_material(client)
    pedido = create_order(client, fornecedor["id"])
    add_item(client, pedido["id"], material["id"], quantidade=7, preco_unitario=9)
    approve_order(client, pedido["id"])
    receive_order(client, pedido["id"])

    response = client.get(f"/api/estoque/{material['id']}")

    assert response.status_code == 200
    assert float(response.json()["quantidade_disponivel"]) == 7.0


def test_estoque_insuficiente_na_saida(client):
    material = create_material(client)

    response = client.post(
        "/api/estoque/saida",
        json={"material_id": material["id"], "quantidade": 3, "observacao": "Uso na obra"},
    )

    assert response.status_code == 409
    assert response.json()["error"] == "INSUFFICIENT_STOCK"


def test_cnpj_duplicado(client):
    create_supplier(client, cnpj="99888777000166")

    response = client.post(
        "/api/fornecedores",
        json={
            "razao_social": "Fornecedor Beta",
            "cnpj": "99.888.777/0001-66",
            "telefone": "11888888888",
            "email": "financeiro@beta.com",
            "ativo": True,
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == "SUPPLIER_ALREADY_EXISTS"


def test_calculo_de_valor_total(client):
    fornecedor = create_supplier(client)
    material_1 = create_material(client, nome="Areia")
    material_2 = create_material(client, nome="Brita")
    pedido = create_order(client, fornecedor["id"])

    primeiro = add_item(client, pedido["id"], material_1["id"], quantidade=2, preco_unitario=10)
    segundo = add_item(client, pedido["id"], material_2["id"], quantidade=1, preco_unitario=5)

    assert float(primeiro["itens"][0]["subtotal"]) == 20.0
    assert float(segundo["itens"][1]["subtotal"]) == 5.0
    assert float(segundo["valor_total"]) == 25.0
