"""
Agent database models and schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json


class AgentCreate(BaseModel):
    """Schema for creating a new agent"""
    name: str = Field(..., description="Unique agent name")
    role: str = Field(..., description="Agent role (assistant, coder, researcher)")
    system_message: str = Field(..., description="System message defining agent behavior")
    capabilities: List[str] = Field(default=[], description="List of agent capabilities")
    model: str = Field(default="llama-3.3-70b-versatile", description="LLM model to use")
    provider: str = Field(default="groq", description="LLM provider")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class AgentResponse(BaseModel):
    """Schema for agent responses"""
    id: str
    name: str
    role: str
    system_message: str
    capabilities: List[str]
    model: str
    provider: str
    code: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    @classmethod
    def from_orm(cls, agent_record):
        """Create response from database record"""
        return cls(
            id=str(agent_record["id"]),
            name=agent_record["name"],
            role=agent_record["role"],
            system_message=agent_record["system_message"],
            capabilities=json.loads(agent_record["capabilities"]) if isinstance(agent_record["capabilities"], str) else agent_record["capabilities"],
            model=agent_record["model"],
            provider=agent_record["provider"],
            code=agent_record.get("code"),
            status=agent_record["status"],
            created_at=agent_record["created_at"],
            updated_at=agent_record["updated_at"],
            metadata=json.loads(agent_record["metadata"]) if isinstance(agent_record["metadata"], str) else agent_record["metadata"]
        )


class Agent:
    """Agent database operations"""
    
    @staticmethod
    async def create(db, agent_data: AgentCreate):
        """Create a new agent in the database"""
        query = """
            INSERT INTO agents (name, role, system_message, capabilities, model, provider, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        
        record = await db.fetchrow(
            query,
            agent_data.name,
            agent_data.role,
            agent_data.system_message,
            json.dumps(agent_data.capabilities),
            agent_data.model,
            agent_data.provider,
            json.dumps(agent_data.metadata)
        )
        
        return record
    
    @staticmethod
    async def get_by_id(db, agent_id: str):
        """Get agent by ID"""
        query = "SELECT * FROM agents WHERE id = $1"
        return await db.fetchrow(query, uuid.UUID(agent_id))
    
    @staticmethod
    async def get_by_name(db, name: str):
        """Get agent by name"""
        query = "SELECT * FROM agents WHERE name = $1"
        return await db.fetchrow(query, name)
    
    @staticmethod
    async def list(db, skip: int = 0, limit: int = 100):
        """List agents with pagination"""
        query = """
            SELECT * FROM agents 
            ORDER BY created_at DESC 
            OFFSET $1 LIMIT $2
        """
        return await db.fetch(query, skip, limit)
    
    @staticmethod
    async def update(db, agent_id: str, updates: dict):
        """Update agent"""
        # Build dynamic update query
        set_clauses = []
        values = []
        param_count = 1
        
        for key, value in updates.items():
            if key in ["capabilities", "metadata"] and isinstance(value, (list, dict)):
                value = json.dumps(value)
            set_clauses.append(f"{key} = ${param_count}")
            values.append(value)
            param_count += 1
        
        # Add updated_at
        set_clauses.append(f"updated_at = ${param_count}")
        values.append(datetime.utcnow())
        param_count += 1
        
        # Add agent_id for WHERE clause
        values.append(uuid.UUID(agent_id))
        
        query = f"""
            UPDATE agents 
            SET {', '.join(set_clauses)}
            WHERE id = ${param_count}
            RETURNING *
        """
        
        return await db.fetchrow(query, *values)
    
    @staticmethod
    async def delete(db, agent_id: str):
        """Delete agent"""
        query = "DELETE FROM agents WHERE id = $1"
        result = await db.execute(query, uuid.UUID(agent_id))
        return result == "DELETE 1"
    
    async def save(self, db):
        """Save agent changes (for instances)"""
        # This would be used if we had an Agent instance class
        # For now, use the static update method
        pass


class AgentExecution(BaseModel):
    """Schema for agent execution tracking"""
    id: str
    agent_id: str
    task: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    status: str = "pending"
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AgentTemplate(BaseModel):
    """Schema for agent templates"""
    id: str
    name: str
    role: str
    system_message: str
    capabilities: List[str]
    description: str
    is_default: bool
    created_at: datetime
    metadata: Dict[str, Any]
