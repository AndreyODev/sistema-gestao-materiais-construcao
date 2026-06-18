import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app

output_path = r"c:\sistema-gestao-materiais\tmp_rule_payloads.json"
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
results = {}
with TestClient(app) as client:
    supplier = client.post('/api/fornecedores', json={
        'razao_social': 'Fornecedor Alpha',
        'cnpj': '12345678000195',
        'telefone': '11999999999',
        'email': 'contato@alpha.com',
        'ativo': True,
    }).json()
    material = client.post('/api/materiais', json={
        'nome': 'Cimento CP2',
        'descricao': 'Material de construcao',
        'unidade_medida': 'saco',
        'estoque_minimo': 10,
        'preco_medio': 35.5,
        'ativo': True,
    }).json()
    pedido = client.post('/api/pedidos', json={'fornecedor_id': supplier['id'], 'observacao': 'Pedido inicial'}).json()

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
    capture('SUPPLIER_ALREADY_EXISTS', client.post('/api/fornecedores', json={
        'razao_social': 'Fornecedor Beta',
        'cnpj': '12.345.678/0001-95',
        'telefone': '11888888888',
        'email': 'financeiro@beta.com',
        'ativo': True,
    }))

    client.post(f"/api/pedidos/{pedido['id']}/itens", json={'material_id': material['id'], 'quantidade': 2, 'preco_unitario': 40})
    client.post(f"/api/pedidos/{pedido['id']}/aprovar")
    client.post(f"/api/pedidos/{pedido['id']}/receber")
    capture('ORDER_ALREADY_RECEIVED_CANCEL', client.post(f"/api/pedidos/{pedido['id']}/cancelar"))
    capture('ORDER_ALREADY_RECEIVED_RECEBER', client.post(f"/api/pedidos/{pedido['id']}/receber"))

app.dependency_overrides.clear()
with open(output_path, 'w', encoding='utf-8') as fp:
    json.dump(results, fp, ensure_ascii=False, indent=2)
