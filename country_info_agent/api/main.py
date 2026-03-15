"""
FastAPI application for Country Info Agent.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from country_info_agent.config import get_settings
from country_info_agent.logging_config import setup_logging
from country_info_agent.services.agent_service import AgentService

logger = logging.getLogger(__name__)

agent_service: AgentService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global agent_service
    setup_logging()
    agent_service = AgentService()
    logger.info("Country Info Agent API started")
    logger.info(f"Health check: {agent_service.health_check()}")
    yield
    logger.info("Country Info Agent API stopped")


app = FastAPI(
    title="Country Info Agent",
    description="AI agent that answers questions about countries",
    version="1.0.0",
    lifespan=lifespan,
)


class QueryRequest(BaseModel):
    """Request model for query endpoint."""

    query: str = Field(
        ..., min_length=3, max_length=500, description="User query about a country"
    )


class QueryResponse(BaseModel):
    """Response model for query endpoint."""

    answer: str
    country: str | None = None
    fields: list[str] | None = None


class HealthResponse(BaseModel):
    status: str
    api_key_configured: bool
    config: dict


@app.get("/")
async def root():
    return {"message": "Country Info Agent API", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check endpoint."""
    if not agent_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return agent_service.health_check()


@app.post("/query", response_model=QueryResponse, tags=["Agent"])
async def query(request: QueryRequest):
    """
    Process a query about a country.

    Example: "What is the population of Germany?"
    """
    logger.info(f"Received query: {request.query}")

    result = agent_service.process_query(request.query)

    if result.get("error"):
        logger.warning(f"Query error: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])

    return QueryResponse(
        answer=result["answer"],
        country=result.get("country_name"),
        fields=result.get("requested_fields"),
    )
