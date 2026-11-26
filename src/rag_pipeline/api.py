from __future__ import annotations

import json
import logging
import queue
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from .factory import create_store
from .observability import LATENCY, REQUESTS, configure_logging
from .service import RAGService
from .settings import get_settings

logger = logging.getLogger(__name__)

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
    if settings.warmup_on_start:
        # Loading weights on a background thread crashed natively in torch_cpu.dll on Windows; keep it on the main thread.
        app.state.service.warm_up()
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


@app.post("/v1/chat/stream")
def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    """Server-sent events: one event per pipeline step, then a final 'done' event carrying the answer."""
    svc = service(request)
    events: queue.Queue[dict] = queue.Queue()

    def emit(stage: str, message: str, **data) -> None:
        events.put({"stage": stage, "message": message, **data})

    def run() -> None:
        try:
            with LATENCY.labels("chat").time():
                result = svc.answer(payload.question, emit=emit)
            REQUESTS.labels("chat", "success").inc()
            events.put({"stage": "done", "message": "Answer ready", "result": result})
        except Exception:
            logger.exception("Streaming answer generation failed")
            REQUESTS.labels("chat", "error").inc()
            events.put({"stage": "error", "message": "Answer generation failed"})

    threading.Thread(target=run, name="chat-stream", daemon=True).start()

    def stream():
        while True:
            event = events.get()
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            if event["stage"] in ("done", "error"):
                return

    return StreamingResponse(
        stream(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


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


@app.get("/v1/codevault")
def codevault_view(
    request: Request,
    query: str = Query(default="", max_length=200),
    language: str = Query(default="", max_length=50),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    try:
        return service(request).codevault_page(query, language, offset, limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Code Vault listing failed") from exc


@app.get("/v1/codevault/file")
def codevault_file(request: Request, path: str = Query(min_length=1, max_length=500)) -> dict:
    try:
        return service(request).codevault_file(path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
