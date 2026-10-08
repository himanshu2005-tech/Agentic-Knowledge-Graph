from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from .factory import create_store
from .observability import LATENCY, REQUESTS, configure_logging
from .service import RAGService
from .settings import get_settings


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=2, max_length=4000)
    entities: list[str] = Field(default_factory=list, max_length=20)


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)


class FeedbackRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    verdict: str = Field(pattern="^(correct|incorrect|incomplete)$")
    note: str = Field(default="", max_length=4000)
    fact_ids: list[str] = Field(default_factory=list, max_length=100)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    app.state.service = RAGService(settings, create_store(settings))
    yield
    app.state.service.close()


app = FastAPI(
    title="Agentic Knowledge Graph API", version="1.0.0", lifespan=lifespan,
    docs_url="/docs", redoc_url="/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in get_settings().cors_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


def service(request: Request) -> RAGService:
    return request.app.state.service


@app.get("/health/live")
def live() -> dict:
    return {"status": "alive"}


@app.get("/health/ready")
def ready(request: Request) -> dict:
    try:
        return service(request).health()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/retrieve")
def retrieve(payload: RetrieveRequest, request: Request) -> dict:
    with LATENCY.labels("retrieve").time():
        try:
            result = service(request).retrieve(payload.query, payload.entities)
            REQUESTS.labels("retrieve", "success").inc()
            return result.to_dict()
        except Exception as exc:
            REQUESTS.labels("retrieve", "error").inc()
            raise HTTPException(status_code=500, detail="Retrieval failed") from exc


@app.post("/v1/chat")
def chat(payload: ChatRequest, request: Request) -> dict:
    with LATENCY.labels("chat").time():
        try:
            response = service(request).answer(payload.question)
            REQUESTS.labels("chat", "success").inc()
            return response
        except Exception as exc:
            REQUESTS.labels("chat", "error").inc()
            raise HTTPException(status_code=500, detail="Answer generation failed") from exc


@app.post("/v1/feedback", status_code=201)
def feedback(payload: FeedbackRequest, request: Request) -> dict:
    return service(request).submit_feedback(payload.question, payload.verdict, payload.note, payload.fact_ids)


@app.get("/v1/graph")
def graph_view(
    request: Request,
    query: str = Query(default="", max_length=200),
    domain: str = Query(default="", max_length=100),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
) -> dict:
    try:
        return service(request).graph_view(query=query, domain=domain, offset=offset, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Graph visualization failed") from exc
