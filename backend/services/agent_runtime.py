"""
Agent Runtime Service
Handles agent execution and task management
"""

from typing import Dict, Any, Optional
import asyncio
import json
import uuid
from datetime import datetime
from ..models.database import get_db


class AgentRuntimeService:
    """Service for executing agents and managing their runtime"""
    
    def __init__(self):
        self.db = None
        self.running_agents = {}  # Track running agent instances
    
    async def get_db(self):
        """Get database connection"""
        if not self.db:
            self.db = await get_db()
        return self.db
    
    async def execute_task(self, agent_record, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with an agent"""
        db = await self.get_db()
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        
        await db.execute("""
            INSERT INTO agent_executions (id, agent_id, task, status)
            VALUES ($1, $2, $3, $4)
        """, 
            uuid.UUID(execution_id),
            agent_record["id"],
            json.dumps(task),
            "running"
        )
        
        try:
            # Execute the task (simplified for MVP)
            result = await self._execute_agent_task(agent_record, task)
            
            # Update execution record with success
            await db.execute("""
                UPDATE agent_executions 
                SET result = $1, status = $2, completed_at = $3
                WHERE id = $4
            """,
                json.dumps(result),
                "completed",
                datetime.utcnow(),
                uuid.UUID(execution_id)
            )
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "result": result
            }
            
        except Exception as e:
            # Update execution record with error
            await db.execute("""
                UPDATE agent_executions 
                SET status = $1, error_message = $2, completed_at = $3
                WHERE id = $4
            """,
                "failed",
                str(e),
                datetime.utcnow(),
                uuid.UUID(execution_id)
            )
            
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_agent_task(self, agent_record, task: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to execute agent task"""
        # For MVP, we'll simulate agent execution
        # In production, this would integrate with AutoGen or similar framework
        
        agent_name = agent_record["name"]
        agent_role = agent_record["role"]
        system_message = agent_record["system_message"]
        
        # Simulate different responses based on agent role
        if agent_role == "assistant":
            result = await self._simulate_assistant_response(task)
        elif agent_role == "coder":
            result = await self._simulate_coder_response(task)
        elif agent_role == "researcher":
            result = await self._simulate_researcher_response(task)
        else:
            result = await self._simulate_generic_response(task)
        
        return {
            "agent_name": agent_name,
            "agent_role": agent_role,
            "task_type": task.get("type", "unknown"),
            "response": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _simulate_assistant_response(self, task: Dict[str, Any]) -> str:
        """Simulate assistant agent response"""
        # Add small delay to simulate processing
        await asyncio.sleep(0.5)
        
        task_content = task.get("content", "")
        return f"As your assistant, I've processed your request: '{task_content}'. I'm ready to help with any follow-up questions or tasks you might have."
    
    async def _simulate_coder_response(self, task: Dict[str, Any]) -> str:
        """Simulate coder agent response"""
        await asyncio.sleep(1.0)
        
        task_content = task.get("content", "")
        return f"I've analyzed your coding request: '{task_content}'. Here's a structured approach I would take: 1) Understand requirements, 2) Design solution, 3) Implement code, 4) Test and validate. Would you like me to proceed with any specific part?"
    
    async def _simulate_researcher_response(self, task: Dict[str, Any]) -> str:
        """Simulate researcher agent response"""
        await asyncio.sleep(1.5)
        
        task_content = task.get("content", "")
        return f"I've initiated research on: '{task_content}'. My research methodology includes: gathering sources, analyzing data, synthesizing findings, and providing citations. I'll deliver comprehensive insights based on available information."
    
    async def _simulate_generic_response(self, task: Dict[str, Any]) -> str:
        """Simulate generic agent response"""
        await asyncio.sleep(0.8)
        
        task_content = task.get("content", "")
        return f"I've received your task: '{task_content}'. I'm processing this request according to my capabilities and will provide the best possible response."
    
    async def get_execution_history(self, agent_id: str, limit: int = 10) -> list:
        """Get execution history for an agent"""
        db = await self.get_db()
        
        query = """
            SELECT * FROM agent_executions 
            WHERE agent_id = $1 
            ORDER BY started_at DESC 
            LIMIT $2
        """
        
        executions = await db.fetch(query, uuid.UUID(agent_id), limit)
        
        result = []
        for execution in executions:
            result.append({
                "id": str(execution["id"]),
                "task": json.loads(execution["task"]) if execution["task"] else {},
                "result": json.loads(execution["result"]) if execution["result"] else None,
                "status": execution["status"],
                "started_at": execution["started_at"],
                "completed_at": execution["completed_at"],
                "error_message": execution["error_message"]
            })
        
        return result
    
    async def get_runtime_stats(self) -> Dict[str, Any]:
        """Get runtime statistics"""
        db = await self.get_db()
        
        # Total executions
        total_executions = await db.fetchrow("SELECT COUNT(*) as count FROM agent_executions")
        
        # Executions by status
        executions_by_status = await db.fetch("""
            SELECT status, COUNT(*) as count 
            FROM agent_executions 
            GROUP BY status
        """)
        
        # Recent executions (last 24 hours)
        recent_executions = await db.fetchrow("""
            SELECT COUNT(*) as count 
            FROM agent_executions 
            WHERE started_at >= NOW() - INTERVAL '24 hours'
        """)
        
        # Average execution time (for completed executions)
        avg_execution_time = await db.fetchrow("""
            SELECT AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_seconds
            FROM agent_executions 
            WHERE status = 'completed' AND completed_at IS NOT NULL
        """)
        
        return {
            "total_executions": total_executions["count"],
            "executions_by_status": [{"status": row["status"], "count": row["count"]} for row in executions_by_status],
            "recent_executions": recent_executions["count"],
            "average_execution_time_seconds": float(avg_execution_time["avg_seconds"]) if avg_execution_time["avg_seconds"] else 0
        }
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        db = await self.get_db()
        
        # Update execution status to cancelled
        result = await db.execute("""
            UPDATE agent_executions 
            SET status = 'cancelled', completed_at = $1
            WHERE id = $2 AND status = 'running'
        """,
            datetime.utcnow(),
            uuid.UUID(execution_id)
        )
        
        return result == "UPDATE 1"
