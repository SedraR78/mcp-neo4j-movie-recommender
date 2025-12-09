"""
MCP SERVER - GraphRAG avec Neo4j
=================================

CE FICHIER = LA GLUE ENTRE TES COLLÈGUES ET NEO4J

Tes collègues appellent Claude → Claude appelle ce serveur → Tu queries Neo4j
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
from neo4j_connector import Neo4jConnector
import json
import asyncio

# Créer le serveur MCP
server = Server("graphrag-neo4j-server")

# Connexion Neo4j globale
neo4j_conn = None

def get_connector():
    """Récupère ou crée la connexion Neo4j"""
    global neo4j_conn
    if neo4j_conn is None:
        neo4j_conn = Neo4jConnector()
        neo4j_conn.connect()
    return neo4j_conn

# ============================================================================
# DÉFINIR LES OUTILS DISPONIBLES POUR LE LLM
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Liste les 3 fonctions principales que tes collègues peuvent utiliser
    """
    return [
        Tool(
            name="search_graph_context",
            description="Recherche du contexte dans le graph Neo4j. Utilise cette fonction pour trouver des informations pertinentes basées sur une requête. Retourne des nœuds avec leurs propriétés et types.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La requête de recherche (mots-clés, concepts, etc.)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Nombre maximum de résultats (défaut: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        
        Tool(
            name="get_node_relationships",
            description="Récupère les relations d'un nœud spécifique. Utilise cette fonction pour explorer les connexions et le contexte enrichi autour d'un concept ou entité.",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "L'ID du nœud (obtenu via search_graph_context)"
                    }
                },
                "required": ["node_id"]
            }
        ),
        
        Tool(
            name="save_graph_context",
            description="Sauvegarde du nouveau contexte dans le graph. Utilise cette fonction pour persister des informations découvertes ou générées par l'agent.",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "Type du nœud (ex: Concept, Entity, Context, Agent_Output)"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Propriétés du nœud (ex: {name: 'xxx', description: 'yyy'})"
                    },
                    "relations": {
                        "type": "array",
                        "description": "Relations à créer (ex: [{target_id: 'xxx', type: 'RELATED_TO'}])",
                        "items": {
                            "type": "object"
                        }
                    }
                },
                "required": ["type", "properties"]
            }
        )
    ]

# ============================================================================
# IMPLÉMENTER LES FONCTIONS
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Cette fonction est appelée automatiquement par Claude
    quand il veut utiliser un de tes outils
    """
    
    connector = get_connector()
    
    try:
        # FONCTION 1: Recherche de contexte
        if name == "search_graph_context":
            query = arguments.get("query")
            limit = arguments.get("limit", 5)
            
            print(f"🔍 Recherche: '{query}' (limit: {limit})")
            
            result = connector.search_context(query, limit)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]
        
        # FONCTION 2: Récupérer les relations
        elif name == "get_node_relationships":
            node_id = arguments.get("node_id")
            
            print(f"🔗 Relations du nœud: {node_id}")
            
            result = connector.get_relationships(node_id)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]
        
        # FONCTION 3: Sauvegarder du contexte
        elif name == "save_graph_context":
            data = {
                "type": arguments.get("type"),
                "properties": arguments.get("properties"),
                "relations": arguments.get("relations", [])
            }
            
            print(f"💾 Sauvegarde: {data['type']}")
            
            result = connector.save_context(data)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]
        
        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Outil inconnu: {name}",
                        "status": "error"
                    })
                )
            ]
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "status": "error"
                })
            )
        ]

# ============================================================================
# DÉMARRAGE DU SERVEUR
# ============================================================================

async def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("🚀 MCP Server GraphRAG - Démarrage...")
    print("=" * 60)
    
    # Initialiser Neo4j
    connector = get_connector()
    
    # Optionnel: créer des données de test
    # connector.init_sample_data()
    
    print("\n✅ Serveur MCP prêt!")
    print("📡 En attente de connexions...")
    print("=" * 60)
    
    # Lancer le serveur MCP
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Serveur arrêté")
        if neo4j_conn:
            neo4j_conn.close()