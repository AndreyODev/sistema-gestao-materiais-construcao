import json

def test_dump_payloads(client):
    response = client.post(
        '/api/fornecedores',
        json={
            'razao_social': 'Fornecedor Alpha',
            'cnpj': '12345678000195',
            'telefone': '11999999999',
            'email': 'contato@alpha.com',
            'ativo': True,
        },
    )
    supplier = response.json()

    response = client.post(
        '/api/materiais',
        json={
            'nome': 'Cimento CP2',
            'descricao': 'Material de construcao',
            'unidade_medida': 'saco',
            'estoque_minimo': 10,
            'preco_medio': 35.5,
            'ativo': True,
        },
    )
    material = response.json()

    response = client.post('/api/pedidos', json={'fornecedor_id': supplier['id'], 'observacao': 'Pedido inicial'})
    pedido = response.json()

    results = {}

    def capture(name, response):
        results[name] = {'status_code': response.status_code, 'body': response.json()}

    capture('ORDER_WITHOUT_ITEMS', client.post(f"/api/pedidos/{pedido['id']}/aprovar"))
    capture('INVALID_QUANTITY', client.post(
        f"/api/pedidos/{pedido['id']}/itens",
        json={'material_id': material['id'], 'quantidade': -10, 'preco_unitario': 45},
    ))
    capture('INSUFFICIENT_STOCK', client.post(
        '/api/estoque/saida',
        json={'material_id': material['id'], 'quantidade': 3, 'observacao': 'Uso na obra'},
    ))
    capture('SUPPLIER_ALREADY_EXISTS', client.post(
        '/api/fornecedores',
        json={
            'razao_social': 'Fornecedor Beta',
            'cnpj': '12.345.678/0001-95',
            'telefone': '11888888888',
            'email': 'financeiro@beta.com',
            'ativo': True,
        },
    ))

    client.post(f"/api/pedidos/{pedido['id']}/itens", json={'material_id': material['id'], 'quantidade': 2, 'preco_unitario': 40})
    client.post(f"/api/pedidos/{pedido['id']}/aprovar")
    client.post(f"/api/pedidos/{pedido['id']}/receber")
    capture('ORDER_ALREADY_RECEIVED_CANCEL', client.post(f"/api/pedidos/{pedido['id']}/cancelar"))
    capture('ORDER_ALREADY_RECEIVED_RECEBER', client.post(f"/api/pedidos/{pedido['id']}/receber"))

    with open(r'c:\sistema-gestao-materiais\tmp_rule_payloads.json', 'w', encoding='utf-8') as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
