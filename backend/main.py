"""
FastAPI Backend for Self-Building Agent System
Provides REST API for agent management with PostgreSQL integration
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from typing import List, Optional

from .models.database import init_db, get_db
from .models.agent import Agent, AgentCreate, AgentResponse
from .services.agent_factory import AgentFactoryService
from .services.agent_runtime import AgentRuntimeService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await init_db()
    yield


# Initialize FastAPI app
app = FastAPI(
    title="Self-Building Agent System API",
    description="API for creating and managing AI agents that can create other agents",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
agent_factory = AgentFactoryService()
agent_runtime = AgentRuntimeService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Self-Building Agent System API",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check for Railway"""
    return {"status": "healthy"}


# Agent Management Endpoints

@app.post("/api/agents", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db = Depends(get_db)
):
    """Create a new agent"""
    try:
        # Create agent in database
        agent = await Agent.create(db, agent_data)
        
        # Generate agent code
        agent_code = await agent_factory.generate_agent_code(agent)
        
        # Update agent with generated code
        agent.code = agent_code
        await agent.save(db)
        
        return AgentResponse.from_orm(agent)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_db)
):
    """List all agents"""
    try:
        agents = await Agent.list(db, skip=skip, limit=limit)
        return [AgentResponse.from_orm(agent) for agent in agents]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db = Depends(get_db)
):
    """Get a specific agent"""
    try:
        agent = await Agent.get_by_id(db, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentResponse.from_orm(agent)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    db = Depends(get_db)
):
    """Delete an agent"""
    try:
        success = await Agent.delete(db, agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {"message": "Agent deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/{agent_id}/execute")
async def execute_agent(
    agent_id: str,
    task: dict,
    db = Depends(get_db)
):
    """Execute a task with a specific agent"""
    try:
        agent = await Agent.get_by_id(db, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Execute task using agent runtime
        result = await agent_runtime.execute_task(agent, task)
        
        return {"result": result}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Agent Templates Endpoints

@app.get("/api/templates")
async def list_templates():
    """List available agent templates"""
    return await agent_factory.get_templates()


@app.post("/api/agents/from-template")
async def create_agent_from_template(
    template_name: str,
    agent_name: str,
    customizations: Optional[dict] = None,
    db = Depends(get_db)
):
    """Create an agent from a template"""
    try:
        agent_data = await agent_factory.create_from_template(
            template_name, agent_name, customizations
        )
        
        # Create agent in database
        agent = await Agent.create(db, AgentCreate(**agent_data))
        
        return AgentResponse.from_orm(agent)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
