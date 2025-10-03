"""
Database configuration and connection management
"""

import os
import asyncpg
from typing import Optional
import json
from datetime import datetime


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.database_url = os.getenv("DATABASE_URL")
        
        if not self.database_url:
            # Default to local PostgreSQL for development
            self.database_url = "postgresql://postgres:password@localhost:5432/agents_db"
    
    async def connect(self):
        """Create database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def execute(self, query: str, *args):
        """Execute a query"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch single row"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)


# Global database instance
db = Database()


async def init_db():
    """Initialize database and create tables"""
    await db.connect()
    
    # Create agents table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) UNIQUE NOT NULL,
            role VARCHAR(100) NOT NULL,
            system_message TEXT NOT NULL,
            capabilities JSONB DEFAULT '[]'::jsonb,
            model VARCHAR(100) DEFAULT 'llama-3.3-70b-versatile',
            provider VARCHAR(50) DEFAULT 'groq',
            code TEXT,
            status VARCHAR(50) DEFAULT 'created',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'::jsonb
        );
    """)
    
    # Create agent_executions table for tracking runs
    await db.execute("""
        CREATE TABLE IF NOT EXISTS agent_executions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
            task JSONB NOT NULL,
            result JSONB,
            status VARCHAR(50) DEFAULT 'pending',
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            error_message TEXT,
            metadata JSONB DEFAULT '{}'::jsonb
        );
    """)
    
    # Create agent_templates table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS agent_templates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) UNIQUE NOT NULL,
            role VARCHAR(100) NOT NULL,
            system_message TEXT NOT NULL,
            capabilities JSONB DEFAULT '[]'::jsonb,
            description TEXT,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'::jsonb
        );
    """)
    
    # Insert default templates if they don't exist
    await insert_default_templates()
    
    print("✅ Database initialized successfully")


async def insert_default_templates():
    """Insert default agent templates"""
    templates = [
        {
            "name": "generic_assistant",
            "role": "assistant",
            "system_message": "You are a helpful AI assistant. Provide clear, accurate, and friendly responses.",
            "capabilities": [],
            "description": "General purpose AI assistant for various tasks",
            "is_default": True
        },
        {
            "name": "code_specialist",
            "role": "coder",
            "system_message": "You are a coding specialist. Write clean, efficient, well-documented code. Explain your implementations.",
            "capabilities": ["python", "javascript", "debugging"],
            "description": "Specialized agent for coding and software development tasks",
            "is_default": True
        },
        {
            "name": "research_analyst",
            "role": "researcher",
            "system_message": "You are a research analyst. Gather information, analyze data, and provide detailed insights with citations.",
            "capabilities": ["web_search", "data_analysis", "report_generation"],
            "description": "Research-focused agent for analysis and information gathering",
            "is_default": True
        }
    ]
    
    for template in templates:
        # Check if template already exists
        existing = await db.fetchrow(
            "SELECT id FROM agent_templates WHERE name = $1",
            template["name"]
        )
        
        if not existing:
            await db.execute("""
                INSERT INTO agent_templates (name, role, system_message, capabilities, description, is_default)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, 
                template["name"],
                template["role"], 
                template["system_message"],
                json.dumps(template["capabilities"]),
                template["description"],
                template["is_default"]
            )


async def get_db():
    """Dependency to get database connection"""
    return db
