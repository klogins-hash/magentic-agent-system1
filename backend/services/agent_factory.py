"""
Agent Factory Service
Handles agent creation, code generation, and template management
"""

from typing import List, Dict, Any, Optional
import json
from ..models.database import get_db


class AgentFactoryService:
    """Service for creating and managing agents"""
    
    def __init__(self):
        self.db = None
    
    async def get_db(self):
        """Get database connection"""
        if not self.db:
            self.db = await get_db()
        return self.db
    
    async def generate_agent_code(self, agent_record) -> str:
        """Generate Python code for an agent"""
        name = agent_record["name"]
        role = agent_record["role"]
        system_message = agent_record["system_message"]
        capabilities = json.loads(agent_record["capabilities"]) if isinstance(agent_record["capabilities"], str) else agent_record["capabilities"]
        model = agent_record["model"]
        
        agent_code = f'''
# Agent: {name}
# Role: {role}
# Created by Agent Factory

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.groq import GroqChatCompletionClient
import os

# Initialize Groq model client
model_client = GroqChatCompletionClient(
    model="{model}",
    api_key=os.getenv("GROQ_API_KEY")
)

# Create the agent
{name} = AssistantAgent(
    name="{name}",
    model_client=model_client,
    system_message="""
{system_message}

Your capabilities: {", ".join(capabilities) if capabilities else "general assistance"}
""",
    description="Agent created by Self-Building Agent System"
)

# Agent metadata
agent_metadata = {{
    "id": "{agent_record['id']}",
    "name": "{name}",
    "role": "{role}",
    "capabilities": {capabilities},
    "created_by": "agent_factory"
}}

print(f"✅ Agent '{{agent_metadata['name']}}' initialized successfully")
print(f"Role: {{agent_metadata['role']}}")
print(f"Capabilities: {{agent_metadata['capabilities']}}")

# Export agent for use
__all__ = ["{name}", "agent_metadata"]
'''
        
        return agent_code
    
    async def get_templates(self) -> List[Dict[str, Any]]:
        """Get all available agent templates"""
        db = await self.get_db()
        
        query = """
            SELECT * FROM agent_templates 
            ORDER BY is_default DESC, name ASC
        """
        
        templates = await db.fetch(query)
        
        result = []
        for template in templates:
            result.append({
                "id": str(template["id"]),
                "name": template["name"],
                "role": template["role"],
                "system_message": template["system_message"],
                "capabilities": json.loads(template["capabilities"]) if isinstance(template["capabilities"], str) else template["capabilities"],
                "description": template["description"],
                "is_default": template["is_default"],
                "created_at": template["created_at"],
                "metadata": json.loads(template["metadata"]) if isinstance(template["metadata"], str) else template["metadata"]
            })
        
        return result
    
    async def get_template_by_name(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name"""
        db = await self.get_db()
        
        query = "SELECT * FROM agent_templates WHERE name = $1"
        template = await db.fetchrow(query, template_name)
        
        if not template:
            return None
        
        return {
            "id": str(template["id"]),
            "name": template["name"],
            "role": template["role"],
            "system_message": template["system_message"],
            "capabilities": json.loads(template["capabilities"]) if isinstance(template["capabilities"], str) else template["capabilities"],
            "description": template["description"],
            "is_default": template["is_default"],
            "created_at": template["created_at"],
            "metadata": json.loads(template["metadata"]) if isinstance(template["metadata"], str) else template["metadata"]
        }
    
    async def create_from_template(
        self, 
        template_name: str, 
        agent_name: str, 
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create an agent from a template"""
        template = await self.get_template_by_name(template_name)
        
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Start with template data
        agent_data = {
            "name": agent_name,
            "role": template["role"],
            "system_message": template["system_message"],
            "capabilities": template["capabilities"].copy(),
            "model": "llama-3.3-70b-versatile",
            "provider": "groq",
            "metadata": {
                "created_from_template": template_name,
                "template_id": template["id"]
            }
        }
        
        # Apply customizations if provided
        if customizations:
            if "system_message" in customizations:
                agent_data["system_message"] = customizations["system_message"]
            
            if "capabilities" in customizations:
                # Merge capabilities
                existing_caps = set(agent_data["capabilities"])
                new_caps = set(customizations["capabilities"])
                agent_data["capabilities"] = list(existing_caps.union(new_caps))
            
            if "role" in customizations:
                agent_data["role"] = customizations["role"]
            
            # Add any additional metadata
            if "metadata" in customizations:
                agent_data["metadata"].update(customizations["metadata"])
        
        return agent_data
    
    async def validate_agent_config(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent configuration"""
        errors = []
        
        # Check required fields
        required_fields = ["name", "role", "system_message"]
        for field in required_fields:
            if not agent_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate role
        valid_roles = ["assistant", "coder", "researcher", "analyst", "specialist"]
        if agent_data.get("role") and agent_data["role"] not in valid_roles:
            errors.append(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        # Validate name format (no spaces, special chars)
        name = agent_data.get("name", "")
        if name and not name.replace("_", "").replace("-", "").isalnum():
            errors.append("Agent name must contain only letters, numbers, hyphens, and underscores")
        
        # Check if name already exists
        if name:
            db = await self.get_db()
            existing = await db.fetchrow("SELECT id FROM agents WHERE name = $1", name)
            if existing:
                errors.append(f"Agent with name '{name}' already exists")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about agents"""
        db = await self.get_db()
        
        # Total agents
        total_agents = await db.fetchrow("SELECT COUNT(*) as count FROM agents")
        
        # Agents by role
        agents_by_role = await db.fetch("""
            SELECT role, COUNT(*) as count 
            FROM agents 
            GROUP BY role 
            ORDER BY count DESC
        """)
        
        # Recent agents (last 7 days)
        recent_agents = await db.fetchrow("""
            SELECT COUNT(*) as count 
            FROM agents 
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        
        return {
            "total_agents": total_agents["count"],
            "agents_by_role": [{"role": row["role"], "count": row["count"]} for row in agents_by_role],
            "recent_agents": recent_agents["count"]
        }
