from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def test_search_sci_fi():
    """Test: Search Sci-Fi movies"""
    query = """
    MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre {name: 'Sci-Fi'})
    OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Actor)
    OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Director)
    RETURN m.title, m.rating, collect(DISTINCT a.name) as actors, collect(DISTINCT d.name) as directors
    ORDER BY m.rating DESC
    """
    with driver.session() as session:
        result = session.run(query)
        print("🔍 Sci-Fi Movies:")
        for record in result:
            print(f"  • {record['m.title']} - {record['m.rating']}/10")
            print(f"    Actors: {', '.join(record['actors'])}")
            print(f"    Directors: {', '.join(record['directors'])}\n")

def test_alice_preferences():
    """Test: Alice's preferences"""
    query = """
    MATCH (u:User {name: 'Alice'})-[l:LIKES]->(m:Movie)
    RETURN m.title, l.rating
    ORDER BY l.rating DESC
    """
    with driver.session() as session:
        result = session.run(query)
        print("❤️ Alice's favorite movies:")
        for record in result:
            print(f"  • {record['m.title']} - Rating: {record['l.rating']}/5")

def test_recommendations_for_alice():
    """Test: Recommendations for Alice"""
    query = """
    MATCH (u:User {name: 'Alice'})-[:LIKES]->(liked:Movie)-[:HAS_GENRE]->(g:Genre)
    <-[:HAS_GENRE]-(recommended:Movie)
    WHERE NOT (u)-[:LIKES]->(recommended)
    WITH recommended, collect(DISTINCT g.name) as shared_genres, count(DISTINCT g) as match_count
    RETURN recommended.title, recommended.rating, shared_genres, match_count
    ORDER BY match_count DESC, recommended.rating DESC
    LIMIT 5
    """
    with driver.session() as session:
        result = session.run(query)
        print("\n✨ Recommendations for Alice:")
        for record in result:
            print(f"  • {record['recommended.title']} - {record['recommended.rating']}/10")
            print(f"    Shared genres ({record['match_count']}): {', '.join(record['shared_genres'])}\n")

if __name__ == "__main__":
    print("🧪 Testing MCP server logic locally\n")
    test_search_sci_fi()
    print("\n" + "="*50 + "\n")
    test_alice_preferences()
    print("\n" + "="*50 + "\n")
    test_recommendations_for_alice()
    print("\n✅ All tests completed!")
    driver.close()