import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Connexion Neo4j
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

# Créer le serveur MCP
app = Server("movie-recommender-mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Liste des outils disponibles pour le LLM"""
    return [
        Tool(
            name="search_movies",
            description="Search for movies by genre, actor, director, or rating",
            inputSchema={
                "type": "object",
                "properties": {
                    "genre": {
                        "type": "string",
                        "description": "Genre of the movie (Sci-Fi, Action, Thriller, Drama, Comedy, Mystery)"
                    },
                    "actor": {
                        "type": "string",
                        "description": "Name of the actor"
                    },
                    "director": {
                        "type": "string",
                        "description": "Name of the director"
                    },
                    "min_rating": {
                        "type": "number",
                        "description": "Minimum rating (0-10)"
                    }
                }
            }
        ),
        Tool(
            name="get_user_preferences",
            description="Get the movies a user likes and their ratings",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_name": {
                        "type": "string",
                        "description": "Name of the user (Alice, Bob, or Charlie)"
                    }
                },
                "required": ["user_name"]
            }
        ),
        Tool(
            name="recommend_movies",
            description="Recommend movies for a user based on their preferences",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_name": {
                        "type": "string",
                        "description": "Name of the user"
                    }
                },
                "required": ["user_name"]
            }
        ),
        Tool(
            name="get_movie_details",
            description="Get detailed information about a specific movie",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the movie"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="query_graph",
            description="Execute a custom Cypher query on the graph database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Cypher query to execute"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool based on the LLM's request"""
    
    if name == "search_movies":
        # Build dynamic query based on provided filters
        conditions = []
        
        if "genre" in arguments and arguments["genre"]:
            conditions.append(f"g.name = '{arguments['genre']}'")
        if "actor" in arguments and arguments["actor"]:
            conditions.append(f"a.name CONTAINS '{arguments['actor']}'")
        if "director" in arguments and arguments["director"]:
            conditions.append(f"d.name CONTAINS '{arguments['director']}'")
        if "min_rating" in arguments and arguments["min_rating"]:
            conditions.append(f"m.rating >= {arguments['min_rating']}")
        
        where_clause = " AND ".join(conditions) if conditions else "true"
        
        query = f"""
        MATCH (m:Movie)
        OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Actor)
        OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Director)
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        WHERE {where_clause}
        RETURN DISTINCT m.title as title, 
               m.year as year, 
               m.rating as rating,
               m.description as description,
               collect(DISTINCT a.name) as actors,
               collect(DISTINCT d.name) as directors,
               collect(DISTINCT g.name) as genres
        ORDER BY m.rating DESC
        """
        
        with driver.session() as session:
            result = session.run(query)
            movies = [dict(record) for record in result]
        
        return [TextContent(
            type="text",
            text=f"Found {len(movies)} movies:\n\n" + "\n".join([
                f"• {m['title']} ({m['year']}) - Rating: {m['rating']}/10\n"
                f"  Description: {m['description']}\n"
                f"  Actors: {', '.join(m['actors']) if m['actors'] else 'N/A'}\n"
                f"  Directors: {', '.join(m['directors']) if m['directors'] else 'N/A'}\n"
                f"  Genres: {', '.join(m['genres']) if m['genres'] else 'N/A'}"
                for m in movies[:5]  # Limit to 5 for readability
            ])
        )]
    
    elif name == "get_user_preferences":
        user_name = arguments["user_name"]
        query = f"""
        MATCH (u:User {{name: '{user_name}'}})-[l:LIKES]->(m:Movie)
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        RETURN m.title as title, 
               l.rating as rating, 
               m.year as year,
               m.description as description,
               collect(DISTINCT g.name) as genres
        ORDER BY l.rating DESC
        """
        
        with driver.session() as session:
            result = session.run(query)
            preferences = [dict(record) for record in result]
        
        if not preferences:
            return [TextContent(type="text", text=f"User '{user_name}' not found or has no preferences.")]
        
        return [TextContent(
            type="text",
            text=f"{user_name}'s favorite movies:\n\n" + "\n".join([
                f"• {p['title']} ({p['year']}) - User Rating: {p['rating']}/5\n"
                f"  Genres: {', '.join(p['genres']) if p['genres'] else 'N/A'}\n"
                f"  Description: {p['description']}"
                for p in preferences
            ])
        )]
    
    elif name == "recommend_movies":
        user_name = arguments["user_name"]
        # Recommend movies based on shared genres with liked movies
        query = f"""
        MATCH (u:User {{name: '{user_name}'}})-[:LIKES]->(liked:Movie)-[:HAS_GENRE]->(g:Genre)
        <-[:HAS_GENRE]-(recommended:Movie)
        WHERE NOT (u)-[:LIKES]->(recommended)
        WITH recommended, collect(DISTINCT g.name) as shared_genres, count(DISTINCT g) as genre_match_count
        OPTIONAL MATCH (recommended)<-[:ACTED_IN]-(a:Actor)
        OPTIONAL MATCH (recommended)<-[:DIRECTED]-(d:Director)
        RETURN DISTINCT recommended.title as title, 
               recommended.rating as rating,
               recommended.year as year,
               recommended.description as description,
               shared_genres,
               genre_match_count,
               collect(DISTINCT a.name) as actors,
               collect(DISTINCT d.name) as directors
        ORDER BY genre_match_count DESC, recommended.rating DESC
        LIMIT 5
        """
        
        with driver.session() as session:
            result = session.run(query)
            recommendations = [dict(record) for record in result]
        
        if not recommendations:
            return [TextContent(type="text", text=f"No recommendations found for {user_name}.")]
        
        return [TextContent(
            type="text",
            text=f"Recommendations for {user_name}:\n\n" + "\n".join([
                f"• {r['title']} ({r['year']}) - Rating: {r['rating']}/10\n"
                f"  Why: Shares {r['genre_match_count']} genre(s) with your favorites ({', '.join(r['shared_genres'])})\n"
                f"  Description: {r['description']}\n"
                f"  Actors: {', '.join(r['actors']) if r['actors'] else 'N/A'}\n"
                f"  Directors: {', '.join(r['directors']) if r['directors'] else 'N/A'}"
                for r in recommendations
            ])
        )]
    
    elif name == "get_movie_details":
        title = arguments["title"]
        query = f"""
        MATCH (m:Movie {{title: '{title}'}})
        OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Actor)
        OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Director)
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        OPTIONAL MATCH (u:User)-[l:LIKES]->(m)
        RETURN m.title as title,
               m.year as year,
               m.rating as rating,
               m.description as description,
               collect(DISTINCT a.name) as actors,
               collect(DISTINCT d.name) as directors,
               collect(DISTINCT g.name) as genres,
               collect(DISTINCT {{user: u.name, rating: l.rating}}) as user_ratings
        """
        
        with driver.session() as session:
            result = session.run(query)
            movie = result.single()
        
        if not movie:
            return [TextContent(type="text", text=f"Movie '{title}' not found.")]
        
        user_ratings_text = "\n  ".join([
            f"{ur['user']}: {ur['rating']}/5"
            for ur in movie['user_ratings']
            if ur['user']
        ]) if movie['user_ratings'] else "No user ratings yet"
        
        return [TextContent(
            type="text",
            text=f"**{movie['title']}** ({movie['year']})\n\n"
                 f"Rating: {movie['rating']}/10\n"
                 f"Description: {movie['description']}\n\n"
                 f"Actors: {', '.join(movie['actors']) if movie['actors'] else 'N/A'}\n"
                 f"Directors: {', '.join(movie['directors']) if movie['directors'] else 'N/A'}\n"
                 f"Genres: {', '.join(movie['genres']) if movie['genres'] else 'N/A'}\n\n"
                 f"User Ratings:\n  {user_ratings_text}"
        )]
    
    elif name == "query_graph":
        query = arguments["query"]
        
        with driver.session() as session:
            result = session.run(query)
            records = [dict(record) for record in result]
        
        return [TextContent(
            type="text",
            text=f"Query results ({len(records)} rows):\n\n" + str(records)
        )]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    """Launch the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream, 
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())