# Self-Building Agent System MVP

A minimal system where AI agents can create other AI agents, optimized for Railway deployment.

## 🚀 Quick Start

### Local Development

#### 1. Setup Environment

```bash
# Clone or navigate to project directory
cd magentic-agent-system

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Groq API key
# Get key from: https://console.groq.com/keys
nano .env  # or use your preferred editor
```

#### 3. Launch Magentic-UI

```bash
# Load environment variables
export $(cat .env | xargs)

# Start with Groq and MCP config
magentic-ui --port 8081 --config groq_config.json --mcp-config mcp_config.json
```

#### 4. Test Agent Creation

Open browser to http://localhost:8081

Type in the interface:
```
Create a math tutor agent that helps students learn algebra and calculus
```

The system will:
1. Orchestrator receives your request
2. Calls Agent Factory MCP: create_new_agent()
3. Agent Factory generates agent code
4. Coder agent executes the code
5. New "math tutor" agent is now available!

### Railway Deployment

#### 1. Prepare for Deployment

```bash
# Ensure all files are committed to git
git init
git add .
git commit -m "Initial commit"
```

#### 2. Deploy to Railway

**Option A: Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy
railway up
```

**Option B: GitHub Integration**
1. Push code to GitHub repository
2. Connect repository to Railway at https://railway.app
3. Set environment variables in Railway dashboard:
   - `GROQ_API_KEY`: Your Groq API key
4. Deploy automatically

#### 3. Configure Environment Variables

In Railway dashboard, set:
- `GROQ_API_KEY`: Your Groq API key from https://console.groq.com/keys
- `PORT`: Automatically set by Railway
- `LOG_LEVEL`: INFO (optional)

## 🏗️ Architecture

### 2-Service Railway Architecture

```
┌─────────────────────────────────────┐
│        Railway Service 1            │
│     Main Application Service        │
│  ┌─────────────────────────────────┐ │
│  │     FastAPI Backend             │ │
│  │  ┌─────────────────────────────┐│ │
│  │  │  Agent Factory MCP Server   ││ │
│  │  │  Agent Runtime Service      ││ │
│  │  │  Magentic-UI Integration    ││ │
│  │  └─────────────────────────────┘│ │
│  └─────────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │ Private Network
               │
┌──────────────▼──────────────────────┐
│        Railway Service 2            │
│       PostgreSQL Database           │
│  ┌─────────────────────────────────┐ │
│  │     Agent Configurations        │ │
│  │     Execution History           │ │
│  │     Templates & Metadata        │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Data Flow

```
User Request → FastAPI Backend → PostgreSQL Database
     ↓              ↓                    ↓
Agent Creation → MCP Server → Agent Code Generation
     ↓              ↓                    ↓
Agent Storage → Database → Agent Execution
```

## 📁 Project Structure

```
magentic-agent-system/
├── backend/                   # FastAPI Backend Service
│   ├── main.py               # FastAPI application entry point
│   ├── models/               # Database models and schemas
│   │   ├── database.py       # Database connection and setup
│   │   └── agent.py          # Agent models and schemas
│   ├── services/             # Business logic services
│   │   ├── agent_factory.py  # Agent creation service
│   │   └── agent_runtime.py  # Agent execution service
│   └── api/                  # API route handlers
├── agent_factory_mcp.py      # MCP server (integrated with backend)
├── groq_config.json          # Groq model configuration
├── mcp_config.json           # MCP server registration
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Local development setup
├── Procfile                  # Railway deployment config
├── railway.json              # Railway deployment settings
├── .env.example              # Environment variables template
├── agents/                   # Fallback file storage
│   └── templates/            # Agent templates (fallback)
└── README.md                 # This file
```

## 🛠️ Available MCP Tools

### create_new_agent
Creates a new agent with specified capabilities.

**Parameters:**
- `name`: Unique agent name (e.g., "crm_specialist")
- `role`: Agent role type - "assistant", "coder", or "researcher"
- `system_message`: Instructions defining agent's purpose
- `capabilities`: Optional list of special capabilities

### list_agents
Lists all created agents and their configurations.

### get_agent_code
Retrieves code for a previously created agent.

## 🧪 Testing

### Basic Functionality Tests

- [ ] Magentic-UI launches without errors
- [ ] Web interface loads at localhost:8081 (or Railway URL)
- [ ] Can create a new session
- [ ] Agent Factory MCP tools appear in available tools
- [ ] Can call `list_agents()` tool
- [ ] Can call `create_new_agent()` tool
- [ ] Agent config is saved to `agents/` directory
- [ ] Generated agent code is valid Python
- [ ] Coder agent can execute generated code
- [ ] New agent responds to tasks

### Integration Tests

**Test 1: Assistant Agent**
```
Create a customer service agent that helps users with product questions and complaints.
```

**Test 2: Research Agent**
```
Create a market research agent that analyzes industry trends and competitors.
```

**Test 3: Specialized Agent**
```
Create a data analyst agent that can process CSV files and generate visualizations.
```

### Success Criteria

MVP is complete when all 5 commands work:

1. "List all available agents" → Shows default templates
2. "Create a CRM agent that manages customer contacts" → Creates agent successfully
3. "List all available agents" → Shows CRM agent
4. "Ask the CRM agent to create a sample customer record" → New agent responds
5. "Create a sales analyst agent that works with the CRM agent" → Creates coordinating agent

## 🚨 Troubleshooting

### Groq API Key Issues
```bash
echo $GROQ_API_KEY  # Verify it's set locally
# For Railway: Check environment variables in dashboard
```

### MCP Server Not Loading
- Check that `agent_factory_mcp.py` is in the same directory as `mcp_config.json`
- Verify fastmcp is installed: `pip show fastmcp`

### Magentic-UI Won't Start
```bash
# Check Python version (needs 3.10+)
python --version

# Reinstall magentic-ui
pip uninstall magentic-ui
pip install magentic-ui --upgrade
```

### Railway Deployment Issues
- Ensure `GROQ_API_KEY` is set in Railway environment variables
- Check Railway logs for startup errors
- Verify `Procfile` and `railway.json` are in root directory

## 💰 Cost Estimates

- **Groq API**: ~$0.30-0.50 per 1,000 agent interactions
- **Railway Hosting**: 
  - Hobby Plan: $5/month (512MB RAM, shared CPU)
  - Pro Plan: $20/month (8GB RAM, shared CPU)
- **Total Monthly**: ~$5-25 depending on usage

## 🔗 Resources

### Documentation
- [Magentic-UI](https://github.com/microsoft/magentic-ui)
- [AutoGen v0.4](https://microsoft.github.io/autogen/)
- [Groq API](https://console.groq.com/docs)
- [Railway Deployment](https://docs.railway.app/)
- [MCP Specification](https://modelcontextprotocol.io/)

### API Keys
- [Groq Console](https://console.groq.com/keys)
- [Railway Dashboard](https://railway.app/dashboard)

## 🚀 Next Steps

### Phase 2: Voice Interface (1-2 days)
Add Pipecat + Groq voice layer for speech interaction.

### Phase 3: Advanced Deployment (1-2 days)
- Auto-scaling configuration
- Database persistence for agent configs
- Multi-environment support

### Phase 4: Self-Expansion (Ongoing)
Tell the system: "Build a complete marketing department" and watch it create and coordinate multiple specialized agents.

## 📄 License

MIT License - See LICENSE file for details.

---

**This is a bootstrap system.** You're building just enough for agents to build the rest.

**Success = Self-building capability unlocked** 🚀
