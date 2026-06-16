from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.routes import webhooks, metrics, users
from src.auth.middleware import AuthMiddleware
from src.models.database import init_db
from src.ingestion.event_processor import start_event_processor, stop_event_processor


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await start_event_processor()
    yield
    await stop_event_processor()


app = FastAPI(
    title="Project Apex — Developer Velocity Dashboard",
    description="Internal API for tracking developer productivity signals",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(AuthMiddleware)
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(users.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "project-apex"}
