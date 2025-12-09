# 🚀 GraphRAG MCP Server - Neo4j Integration

**Hackathon**: GenerationAI Paris - December 9th, 2024  
**Project**: Model Context Protocol (MCP) Server for GraphRAG with Neo4j

---

## 📝 What This Does

This MCP server acts as **the glue** between:
- **Your AI agents** (using Claude API)
- **Graph database** (Neo4j) for intelligent context retrieval
- **Persistent memory** with relationship-aware context

Instead of losing context or hallucinating, your agents can:
- 🔍 Search the graph for relevant information
- 🔗 Explore relationships between concepts
- 💾 Save conclusions persistently

**All automatically through Claude!** No manual MCP management needed.

---

## ⚡ Quick Start

### 1. Prerequisites

- Python 3.11+
- Neo4j Aura instance (or local Neo4j)
- Anthropic API key (for your agents)

### 2. Installation

```bash
# Clone and navigate to project
cd MCP\ Revisions/

# Activate virtual environment
source venv/Scripts/activate  # Git Bash
# OR
.\venv\Scripts\Activate.ps1   # PowerShell

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file:

```bash
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
ANTHROPIC_API_KEY=sk-ant-your-key  # Optional for testing
```

### 4. Launch the Server

```bash
python mcp-server.py
```

Expected output:
```
============================================================
🚀 MCP Server GraphRAG - Starting...
============================================================
✅ Connected to Neo4j!
✅ MCP Server ready!
📡 Waiting for connections...
============================================================
```

**Leave it running!** It waits for Claude to call it.

---

## 🛠️ The 3 Functions Available

### 1️⃣ `search_graph_context`

**Purpose**: Search for context in the Neo4j graph

**Usage**: Just tell Claude:
```
"Search the graph for information about X"
"Find concepts related to Y"
```

**Parameters**:
- `query` (string): Search query
- `limit` (integer, optional): Max results (default: 5)

**Returns**: Nodes with properties and types

**Example**:
```json
{
  "query": "GraphRAG",
  "found": 1,
  "results": [
    {
      "id": "4:xxx:123",
      "type": ["Concept"],
      "properties": {
        "name": "GraphRAG",
        "description": "Graph-based RAG"
      }
    }
  ]
}
```

---

### 2️⃣ `get_node_relationships`

**Purpose**: Explore relationships of a specific node

**Usage**: Tell Claude:
```
"What are the relationships of this concept?"
"Show me what's connected to node X"
```

**Parameters**:
- `node_id` (string): Node ID from search results

**Returns**: Related nodes and relationship types

**Example**:
```json
{
  "node_id": "4:xxx:123",
  "relationships": [
    {
      "type": "USES",
      "connected_node": {
        "type": ["Technology"],
        "properties": {"name": "Neo4j"}
      }
    }
  ]
}
```

**Why important?** Provides enriched context and explainability!

---

### 3️⃣ `save_graph_context`

**Purpose**: Save new context (agent conclusions, findings)

**Usage**: Tell Claude:
```
"Save this result in the graph"
"Persist this conclusion"
```

**Parameters**:
- `type` (string): Node type (e.g., "Agent_Output", "Finding")
- `properties` (object): Node properties
- `relations` (array, optional): Relations to create

**Example**:
```json
{
  "type": "Agent_Output",
  "properties": {
    "agent": "fact_checker",
    "conclusion": "verified",
    "confidence": 0.95,
    "timestamp": "2024-12-09T06:00:00Z"
  },
  "relations": [
    {
      "target_id": "4:xxx:456",
      "type": "VALIDATES"
    }
  ]
}
```

**Why crucial?** Context persistence! Your agents build knowledge over time.

---

## 💻 How Your Agents Use This

### In Your Agent Code

```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

# Just use Claude normally!
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "Search the graph for incidents related to payment service timeouts"
        }
    ]
)

print(response.content[0].text)
```

**That's it!** Claude will:
1. Automatically detect it needs graph info
2. Call `search_graph_context("payment service timeout")`
3. Receive results from Neo4j
4. Synthesize a response

**You don't manage MCP manually** - it's transparent! 🎉

---

## 🎨 Visualize Your Graph

### Neo4j Browser

1. Go to https://browser.neo4j.io/
2. Connect with your credentials
3. Run queries:

```cypher
// See everything
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 50

// Search specific concept
MATCH (n {name: "GraphRAG"})-[r]-(m)
RETURN n, r, m

// Count nodes by type
MATCH (n)
RETURN labels(n) as type, count(n) as count
```

---

## 🧪 Testing

### Test 1: Neo4j Connection

```bash
python neo4j_connector.py
```

Should output:
```
✅ Connected to Neo4j!
📝 Creating test data...
✅ Test data created!
🔍 Testing search...
{
  "query": "GraphRAG",
  "found": 1,
  ...
}
```

### Test 2: MCP Server

```bash
python mcp-server.py
```

Should show:
```
🚀 MCP Server GraphRAG - Starting...
✅ Connected to Neo4j!
✅ MCP Server ready!
```

### Test 3: Full Integration

Run your agent code. Check server logs to see Claude calling your functions!

---

## 🏗️ Architecture

```
Your Agent Code
    ↓
Claude API (LLM)
    ↓
MCP Protocol (automatic)
    ↓
mcp-server.py (THIS SERVER)
    ↓
neo4j_connector.py
    ↓
Neo4j Database (GraphRAG)
```

---

## 🚨 Troubleshooting

### "Connection refused" to Neo4j

✅ Check `.env` file has correct credentials  
✅ URI must start with `neo4j+s://`  
✅ Test connection on https://console.neo4j.io

### "Module not found" errors

✅ Activate virtual environment:
```bash
source venv/Scripts/activate
```

✅ Reinstall dependencies:
```bash
pip install -r requirements.txt
```

### Claude doesn't call the server

✅ MCP server must be running BEFORE your agent code  
✅ Check server logs for errors  
✅ Restart the server

### Query syntax errors

✅ Check Neo4j version compatibility  
✅ Verify Cypher query syntax  
✅ Check server logs for detailed error messages

---

## 📊 Use Cases

### Multi-Agent Collaboration

**Agent 1** (Fact Checker):
```
"Search the graph for known facts about X"
→ Validates information
→ Saves verification result
```

**Agent 2** (Reasoner):
```
"Get relationships of verified fact Y"
→ Explores connections
→ Builds logical conclusions
→ Saves reasoning chain
```

**Result**: Progressive knowledge graph with audit trail!

---

### Human-in-the-Loop Workflow

1. **User describes** a new incident
2. **LLM proposes** structure (via MCP read)
3. **Visualize** proposed graph
4. **User validates** or corrects
5. **Write to Neo4j** (via MCP write)

Pattern: **Proposal → Visualization → Validation → Persistence**

This ensures:
- ✅ Safe AI decisions
- ✅ Quality control
- ✅ Clear developer UX
- ✅ Explainable reasoning

---

## 📁 Project Structure

```
MCP Revisions/
├── .env                    # Credentials (DO NOT COMMIT!)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── neo4j_connector.py     # Neo4j connection + GraphRAG logic
├── mcp-server.py          # MCP server exposing functions
├── mcp-client.py          # Example usage (optional)
└── README.md              # This file
```

---

## 🎯 Key Features

### GraphRAG vs Classic RAG

**Classic RAG**:
- Vector similarity search only
- No relationship understanding
- Flat context

**GraphRAG** (this implementation):
- Relationship-aware retrieval
- Context enriched by graph structure
- Explainable reasoning paths
- Persistent memory

### Why MCP?

- ✅ Standardized LLM-to-tool communication
- ✅ Automatic function calling by Claude
- ✅ No manual prompt engineering needed
- ✅ Easy to extend with new functions

---

## 🔧 Extending the System

### Adding a New Function

1. Add to `neo4j_connector.py`:
```python
def your_new_function(self, param):
    # Your Neo4j logic
    with self.driver.session() as session:
        result = session.run("YOUR CYPHER QUERY", ...)
        return result
```

2. Expose in `mcp-server.py`:
```python
@server.list_tools()
async def list_tools():
    return [
        # ... existing tools
        Tool(
            name="your_new_function",
            description="What it does",
            inputSchema={...}
        )
    ]
```

3. Implement the handler:
```python
@server.call_tool()
async def call_tool(name, arguments):
    if name == "your_new_function":
        result = connector.your_new_function(arguments.get("param"))
        return [TextContent(type="text", text=json.dumps(result))]
```

---

## 📞 Support

**During the Hackathon**:
- Check server logs first
- Verify Neo4j connection
- Test with simple queries

**Common Issues**:
- Server not running → Start it first
- Wrong credentials → Check `.env`
- Query errors → Check Cypher syntax

---

## 🏆 Demo Tips

### What to Show

1. **The Problem**: LLMs lose context, hallucinate
2. **Your Solution**: GraphRAG + MCP for persistent, explainable memory
3. **Live Demo**:
   - Agent searches graph
   - Explores relationships
   - Saves conclusions
4. **Visualization**: Show Neo4j Browser with graph
5. **Human-in-the-Loop**: Show validation workflow (if implemented)

### Key Points to Emphasize

- ✅ Context persistence across conversations
- ✅ Relationship-aware retrieval (not just similarity)
- ✅ Explainability through graph paths
- ✅ Transparent integration (agents don't manage MCP)
- ✅ Safe AI decisions (human validation)

---

## 📚 Additional Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/)
- [Anthropic MCP Docs](https://docs.anthropic.com/en/docs/mcp)
- [Claude API Reference](https://docs.anthropic.com/en/api)

---

## ⚡ Quick Reference

### Launch Server
```bash
python mcp-server.py
```

### Test Neo4j
```bash
python neo4j_connector.py
```

### Neo4j Credentials
```
URI: Check your .env file
User: neo4j
Password: Check your .env file
```

### The 3 Functions
1. `search_graph_context(query, limit)` → Search
2. `get_node_relationships(node_id)` → Explore
3. `save_graph_context(data)` → Save

---

## 🎉 You're Ready!

Your MCP server bridges the gap between:
- **LLMs** (intelligence)
- **GraphRAG** (memory)
- **Your agents** (application)

Everything is connected, persistent, and explainable! 🚀

---

**Good luck with your demo!** 💪🔥

For questions during the hackathon, check the server logs and this README.