"""
Neo4j Connector - Connexion et queries GraphRAG
================================================
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import json

load_dotenv()

class Neo4jConnector:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None
        
    def connect(self):
        """Établit la connexion à Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test de connexion
            self.driver.verify_connectivity()
            print("✅ Connecté à Neo4j!")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion Neo4j: {e}")
            return False
    
    def close(self):
        """Ferme la connexion"""
        if self.driver:
            self.driver.close()
            print("🔌 Connexion Neo4j fermée")
    
    def search_context(self, query: str, limit: int = 5):
        """
        FONCTION 1 : Chercher du contexte dans le graph
        
        Args:
            query: La requête de recherche
            limit: Nombre max de résultats
            
        Returns:
            dict: Résultats structurés avec contexte et relations
        """
        with self.driver.session() as session:
            # Query Cypher pour chercher des nœuds pertinents
            # Cherche dans toutes les propriétés string des nœuds
            cypher_query = """
            MATCH (n)
            WHERE any(prop IN keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower($query))
            RETURN n, labels(n) as node_type
            LIMIT $limit
            """
            
            try:
                result = session.run(cypher_query, parameters={"query": query, "limit": limit})
                
                nodes = []
                for record in result:
                    node = record["n"]
                    node_data = {
                        "id": node.element_id,
                        "type": record["node_type"],
                        "properties": dict(node)
                    }
                    nodes.append(node_data)
                
                return {
                    "query": query,
                    "found": len(nodes),
                    "results": nodes,
                    "status": "success"
                }
            except Exception as e:
                return {
                    "query": query,
                    "error": str(e),
                    "status": "error"
                }
    
    def get_relationships(self, node_id: str):
        """
        FONCTION 2 : Récupérer les relations d'un nœud
        
        Args:
            node_id: ID du nœud
            
        Returns:
            dict: Relations et nœuds connectés
        """
        with self.driver.session() as session:
            cypher_query = """
            MATCH (n)-[r]-(connected)
            WHERE elementId(n) = $node_id
            RETURN type(r) as relation_type, 
                   connected, 
                   labels(connected) as connected_type
            LIMIT 20
            """
            
            try:
                result = session.run(cypher_query, parameters={"node_id": node_id})
                
                relationships = []
                for record in result:
                    rel_data = {
                        "type": record["relation_type"],
                        "connected_node": {
                            "type": record["connected_type"],
                            "properties": dict(record["connected"])
                        }
                    }
                    relationships.append(rel_data)
                
                return {
                    "node_id": node_id,
                    "relationships": relationships,
                    "count": len(relationships),
                    "status": "success"
                }
            except Exception as e:
                return {
                    "node_id": node_id,
                    "error": str(e),
                    "status": "error"
                }
    
    def save_context(self, data: dict):
        """
        FONCTION 3 : Sauvegarder du nouveau contexte
        
        Args:
            data: Dict avec {type, properties, relations}
            
        Returns:
            dict: Confirmation de sauvegarde
        """
        with self.driver.session() as session:
            try:
                # Créer un nœud de type Context
                node_type = data.get("type", "Context")
                properties = data.get("properties", {})
                
                cypher_query = f"""
                CREATE (n:{node_type} $props)
                RETURN elementId(n) as node_id
                """
                
                result = session.run(cypher_query, parameters={"props": properties})
                record = result.single()
                
                if record:
                    node_id = record["node_id"]
                    
                    # Créer les relations si fournies
                    relations = data.get("relations", [])
                    for rel in relations:
                        self._create_relationship(
                            session,
                            node_id,
                            rel.get("target_id"),
                            rel.get("type", "RELATED_TO")
                        )
                    
                    return {
                        "node_id": node_id,
                        "status": "success",
                        "message": f"Nœud {node_type} créé avec succès"
                    }
                    
            except Exception as e:
                return {
                    "error": str(e),
                    "status": "error"
                }
    
    def _create_relationship(self, session, from_id: str, to_id: str, rel_type: str):
        """Helper pour créer une relation"""
        cypher_query = f"""
        MATCH (a), (b)
        WHERE elementId(a) = $from_id AND elementId(b) = $to_id
        CREATE (a)-[r:{rel_type}]->(b)
        RETURN r
        """
        session.run(cypher_query, parameters={"from_id": from_id, "to_id": to_id})
    
    def init_sample_data(self):
        """Créer des données de test rapides"""
        with self.driver.session() as session:
            # Nettoyer d'abord (ATTENTION en prod!)
            session.run("MATCH (n) DETACH DELETE n")
            
            # Créer des nœuds de test
            session.run("""
            CREATE (p1:Concept {name: 'GraphRAG', description: 'Graph-based Retrieval Augmented Generation'})
            CREATE (p2:Concept {name: 'MCP', description: 'Model Context Protocol'})
            CREATE (p3:Concept {name: 'Neo4j', description: 'Graph Database'})
            CREATE (p4:Technology {name: 'Python', type: 'Programming Language'})
            
            CREATE (p1)-[:USES]->(p3)
            CREATE (p1)-[:IMPLEMENTS]->(p2)
            CREATE (p2)-[:CODED_IN]->(p4)
            """)
            
            print("✅ Données de test créées!")

# Test rapide
if __name__ == "__main__":
    connector = Neo4jConnector()
    
    if connector.connect():
        # Test 1: Créer des données
        print("\n📝 Création de données de test...")
        connector.init_sample_data()
        
        # Test 2: Recherche
        print("\n🔍 Test de recherche...")
        results = connector.search_context("GraphRAG")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # Test 3: Relations
        if results["found"] > 0:
            node_id = results["results"][0]["id"]
            print(f"\n🔗 Relations du nœud {node_id}...")
            rels = connector.get_relationships(node_id)
            print(json.dumps(rels, indent=2, ensure_ascii=False))
        
        connector.close()