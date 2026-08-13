import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database.neo4j_connection import check_neo4j_connection, close_neo4j_driver
from app.api.routes import auth, chat, sessions, ingest, mutations

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("inventory_neo4j_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Inventory Neo4j Knowledge Graph Chatbot...")
    connected = check_neo4j_connection()
    if connected:
        logger.info(f"Connected to Neo4j successfully at {settings.NEO4J_URI}")
    else:
        logger.warning(f"Unable to connect to Neo4j at {settings.NEO4J_URI}. Please verify credentials.")
    yield
    logger.info("Closing Neo4j driver connection...")
    close_neo4j_driver()


app = FastAPI(
    title="Inventory Neo4j Knowledge Graph AI Chatbot API",
    description="Enterprise Knowledge Graph AI Assistant for Multi-Hop Supply Chain & Asset Reasoning",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-MS"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({process_time}ms)")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred in Neo4j service."}
    )


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "inventory-neo4j-ai-chatbot", "version": "1.0.0"}


@app.get("/ready", tags=["System"])
def readiness_check():
    is_connected = check_neo4j_connection()
    return {
        "status": "ready" if is_connected else "degraded",
        "neo4j_connection": "connected" if is_connected else "disconnected",
        "neo4j_uri": settings.NEO4J_URI.split("@")[-1] if "@" in settings.NEO4J_URI else settings.NEO4J_URI,
        "llm_configured": bool(settings.OPENAI_API_KEY)
    }


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(ingest.router)
app.include_router(mutations.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
