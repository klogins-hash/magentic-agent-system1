"""
Agent Factory MCP Server
Provides tools for Magentic-UI's Orchestrator to create new agents dynamically.
"""

from mcp.server.fastmcp import FastMCP
import json
import os
from pathlib import Path
from typing import List, Dict

# Initialize MCP server
mcp = FastMCP("AgentFactory")

# Ensure agents directory exists
AGENTS_DIR = Path("agents")
AGENTS_DIR.mkdir(exist_ok=True)

TEMPLATES_DIR = AGENTS_DIR / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)


@mcp.tool()
async def create_new_agent(
    name: str,
    role: str,
    system_message: str,
    capabilities: List[str] = None
) -> str:
    """
    Create a new AI agent with specified capabilities.
    
    Args:
        name: Unique agent name (e.g., "crm_specialist", "data_analyst")
        role: Agent role type - "assistant", "coder", or "researcher"
        system_message: Instructions defining agent's purpose and behavior
        capabilities: Optional list of special capabilities needed
    
    Returns:
        Python code as string that creates and registers the agent
    
    Example:
        create_new_agent(
            name="crm_specialist",
            role="assistant", 
            system_message="You are a CRM expert. Help manage customer data.",
            capabilities=["database_access", "email"]
        )
    """
    
    if capabilities is None:
        capabilities = []
    
    # Create agent configuration
    agent_config = {
        "name": name,
        "role": role,
        "system_message": system_message,
        "capabilities": capabilities,
        "model": "llama-3.3-70b-versatile",
        "provider": "groq"
    }
    
    # Save configuration for future reference
    config_path = AGENTS_DIR / f"{name}.json"
    with open(config_path, 'w') as f:
        json.dump(agent_config, f, indent=2)
    
    # Generate Python code to instantiate the agent
    # This code will be executed by Magentic-UI's Coder agent
    agent_code = f'''
# Agent: {name}
# Role: {role}
# Created by Agent Factory

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.groq import GroqChatCompletionClient
import os

# Initialize Groq model client
model_client = GroqChatCompletionClient(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Create the agent
{name} = AssistantAgent(
    name="{name}",
    model_client=model_client,
    system_message="""
{system_message}

Your capabilities: {", ".join(capabilities) if capabilities else "general assistance"}
"""
)

print(f"✅ Agent '{name}' created successfully")
print(f"Role: {role}")
print(f"Capabilities: {capabilities}")
'''
    
    return {
        "status": "success",
        "message": f"Agent '{name}' created successfully",
        "code": agent_code,
        "config_path": str(config_path)
    }


@mcp.tool()
async def list_agents() -> List[Dict]:
    """
    List all agents that have been created.
    
    Returns:
        List of agent configurations
    """
    
    agents = []
    
    # Read all agent config files
    for config_file in AGENTS_DIR.glob("*.json"):
        try:
            with open(config_file, 'r') as f:
                agent_config = json.load(f)
                agents.append({
                    "name": agent_config.get("name"),
                    "role": agent_config.get("role"),
                    "capabilities": agent_config.get("capabilities", []),
                    "created_at": config_file.stat().st_mtime
                })
        except Exception as e:
            print(f"Error reading {config_file}: {e}")
            continue
    
    return {
        "total": len(agents),
        "agents": agents
    }


@mcp.tool()
async def get_agent_code(name: str) -> str:
    """
    Retrieve the code for a previously created agent.
    
    Args:
        name: Name of the agent
        
    Returns:
        Python code to instantiate the agent
    """
    
    config_path = AGENTS_DIR / f"{name}.json"
    
    if not config_path.exists():
        return {
            "status": "error",
            "message": f"Agent '{name}' not found"
        }
    
    # Load config
    with open(config_path, 'r') as f:
        agent_config = json.load(f)
    
    # Regenerate code from config
    system_message = agent_config.get("system_message", "")
    role = agent_config.get("role", "assistant")
    capabilities = agent_config.get("capabilities", [])
    
    agent_code = f'''
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.groq import GroqChatCompletionClient
import os

model_client = GroqChatCompletionClient(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

{name} = AssistantAgent(
    name="{name}",
    model_client=model_client,
    system_message="""
{system_message}

Your capabilities: {", ".join(capabilities) if capabilities else "general assistance"}
"""
)
'''
    
    return {
        "status": "success",
        "code": agent_code,
        "config": agent_config
    }


# Create some default agent templates on startup
def create_default_templates():
    """Create default agent templates for common use cases"""
    
    templates = [
        {
            "name": "generic_assistant",
            "role": "assistant",
            "system_message": "You are a helpful AI assistant. Provide clear, accurate, and friendly responses.",
            "capabilities": []
        },
        {
            "name": "code_specialist",
            "role": "coder",
            "system_message": "You are a coding specialist. Write clean, efficient, well-documented code. Explain your implementations.",
            "capabilities": ["python", "javascript", "debugging"]
        },
        {
            "name": "research_analyst",
            "role": "researcher",
            "system_message": "You are a research analyst. Gather information, analyze data, and provide detailed insights with citations.",
            "capabilities": ["web_search", "data_analysis", "report_generation"]
        }
    ]
    
    for template in templates:
        template_path = TEMPLATES_DIR / f"{template['name']}.json"
        if not template_path.exists():
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)


# Initialize templates on startup
create_default_templates()


# Run the MCP server
if __name__ == "__main__":
    print("🚀 Agent Factory MCP Server starting...")
    print(f"📁 Agents directory: {AGENTS_DIR.absolute()}")
    print(f"📋 Templates directory: {TEMPLATES_DIR.absolute()}")
    mcp.run(transport="stdio")
