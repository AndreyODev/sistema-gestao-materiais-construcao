from fastapi import FastAPI

from app.core.handlers import register_exception_handlers
from app.routers.estoque import router as estoque_router
from app.routers.fornecedor import router as fornecedor_router
from app.routers.material import router as material_router
from app.routers.movimentacao import router as movimentacao_router
from app.routers.pedido import router as pedido_router

app = FastAPI(title="Sistema de Gestao de Materiais de Construcao e Controle de Compras")
register_exception_handlers(app)

app.include_router(material_router, prefix="/api")
app.include_router(fornecedor_router, prefix="/api")
app.include_router(pedido_router, prefix="/api")
app.include_router(estoque_router, prefix="/api")
app.include_router(movimentacao_router, prefix="/api")


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": app.title}
