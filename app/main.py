from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, import_routes, medicos_routes, pacientes_routes, procedimentos_routes, dashboard_routes
from app.database import engine, Base

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

# Incluir rotas
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(import_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(medicos_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(pacientes_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(procedimentos_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_routes.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    """Health check"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": "0.1.0",
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get("/health")
def health():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "api": settings.PROJECT_NAME,
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
