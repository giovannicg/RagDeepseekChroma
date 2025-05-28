from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="API de Chroma + LLAma3",
    description="Procesamiento de PDFs legales, extracción de información y chat contextual",
    version="1.0.0",
    docs_url="/docs",         # Puedes cambiar a "/swagger" si prefieres
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)