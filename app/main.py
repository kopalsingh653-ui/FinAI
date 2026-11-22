from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.connection import init_db
from app.api.routes import prediction
from app.api.routes import affordability
from app.api.routes import expected_loss
from app.api.routes import credit_score
from app.api.routes import eligibility
from app.api.routes import borrowers
from app.api.routes import applications

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("=" * 55)
    print("FINAI BACKEND STARTING")
    print("=" * 55)

    print(f"Application: {settings.APP_NAME}")
    print(f"Version: {settings.APP_VERSION}")

    init_db()

    yield

    print("FINAI BACKEND SHUTTING DOWN")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Register API routes
app.include_router(prediction.router)


@app.get("/", tags=["General"])
def root():

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Welcome to the FinAI Backend",
        "status": "Running",
        "documentation": "/docs"
    }


@app.get("/api/health", tags=["System"])
def health_check():

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model_available": settings.MODEL_PATH.exists(),
        "metadata_available": settings.METADATA_PATH.exists()
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#ALL ROUTER APIS REGISTERED IN MAIN.PY TO CONNECT APPLICATION ROUTING FILES
app.include_router(prediction.router)
app.include_router(affordability.router)
app.include_router(expected_loss.router)
app.include_router(credit_score.router)
app.include_router(eligibility.router)
app.include_router(borrowers.router)
app.include_router(applications.router)