from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)


def create_movie_database():
    """Crée une base de données complète de films"""

    with driver.session() as session:

        # 1. Nettoyer la base
        print("🧹 Nettoyage de la base...")
        session.run("MATCH (n) DETACH DELETE n")

        # 2. Créer les films
        print("🎬 Création des films...")
        session.run("""
        CREATE (inception:Movie {title: "Inception", year: 2010, rating: 8.8, description: "A thief who enters people's dreams to steal secrets"})
        CREATE (matrix:Movie {title: "The Matrix", year: 1999, rating: 8.7, description: "A hacker discovers the true nature of reality"})
        CREATE (interstellar:Movie {title: "Interstellar", year: 2014, rating: 8.6, description: "Explorers travel through a wormhole in space"})
        CREATE (blade_runner:Movie {title: "Blade Runner 2049", year: 2017, rating: 8.0, description: "A blade runner uncovers a secret"})
        CREATE (arrival:Movie {title: "Arrival", year: 2016, rating: 7.9, description: "A linguist communicates with aliens"})
        CREATE (dark_knight:Movie {title: "The Dark Knight", year: 2008, rating: 9.0, description: "Batman faces the Joker"})
        CREATE (john_wick:Movie {title: "John Wick", year: 2014, rating: 7.4, description: "An assassin comes out of retirement"})
        CREATE (mad_max:Movie {title: "Mad Max: Fury Road", year: 2015, rating: 8.1, description: "Post-apocalyptic chase through the desert"})
        CREATE (prestige:Movie {title: "The Prestige", year: 2006, rating: 8.5, description: "Rivalry between two magicians"})
        CREATE (shutter_island:Movie {title: "Shutter Island", year: 2010, rating: 8.2, description: "A marshal investigates a disappearance"})
        CREATE (fight_club:Movie {title: "Fight Club", year: 1999, rating: 8.8, description: "An insomniac office worker creates a fight club"})
        CREATE (grand_budapest:Movie {title: "The Grand Budapest Hotel", year: 2014, rating: 8.1, description: "Adventures of a legendary concierge"})
        CREATE (wolf_wall_street:Movie {title: "The Wolf of Wall Street", year: 2013, rating: 8.2, description: "Rise and fall of a stockbroker"})
        """)

        # 3. Créer les acteurs
        print("🎭 Création des acteurs...")
        session.run("""
        CREATE (leo:Actor {name: "Leonardo DiCaprio", nationality: "American"})
        CREATE (keanu:Actor {name: "Keanu Reeves", nationality: "Canadian"})
        CREATE (mcconaughey:Actor {name: "Matthew McConaughey", nationality: "American"})
        CREATE (bale:Actor {name: "Christian Bale", nationality: "British"})
        CREATE (gosling:Actor {name: "Ryan Gosling", nationality: "Canadian"})
        CREATE (adams:Actor {name: "Amy Adams", nationality: "American"})
        CREATE (hardy:Actor {name: "Tom Hardy", nationality: "British"})
        CREATE (theron:Actor {name: "Charlize Theron", nationality: "South African"})
        CREATE (jackman:Actor {name: "Hugh Jackman", nationality: "Australian"})
        CREATE (pitt:Actor {name: "Brad Pitt", nationality: "American"})
        CREATE (fiennes:Actor {name: "Ralph Fiennes", nationality: "British"})
        """)

        # 4. Créer les réalisateurs
        print("🎥 Création des réalisateurs...")
        session.run("""
        CREATE (nolan:Director {name: "Christopher Nolan"})
        CREATE (wachowski:Director {name: "Lana & Lilly Wachowski"})
        CREATE (villeneuve:Director {name: "Denis Villeneuve"})
        CREATE (fincher:Director {name: "David Fincher"})
        CREATE (scorsese:Director {name: "Martin Scorsese"})
        CREATE (anderson:Director {name: "Wes Anderson"})
        """)

        # 5. Créer les genres
        print("📁 Création des genres...")
        session.run("""
        CREATE (scifi:Genre {name: "Sci-Fi"})
        CREATE (action:Genre {name: "Action"})
        CREATE (thriller:Genre {name: "Thriller"})
        CREATE (drama:Genre {name: "Drama"})
        CREATE (comedy:Genre {name: "Comedy"})
        CREATE (mystery:Genre {name: "Mystery"})
        """)

        # 6. Créer les utilisateurs
        print("👤 Création des utilisateurs...")
        session.run("""
        CREATE (alice:User {name: "Alice", age: 28, preferences: "Sci-Fi lover"})
        CREATE (bob:User {name: "Bob", age: 35, preferences: "Action fan"})
        CREATE (charlie:User {name: "Charlie", age: 25, preferences: "Nolan enthusiast"})
        """)

        # 7. Relations acteurs -> films
        print("🔗 Création des relations acteurs-films...")
        session.run("""
        MATCH (leo:Actor {name: "Leonardo DiCaprio"}), (inception:Movie {title: "Inception"})
        CREATE (leo)-[:ACTED_IN {role: "Dom Cobb"}]->(inception)
        """)

        session.run("""
        MATCH (leo:Actor {name: "Leonardo DiCaprio"}), (wolf:Movie {title: "The Wolf of Wall Street"})
        CREATE (leo)-[:ACTED_IN {role: "Jordan Belfort"}]->(wolf)
        """)

        session.run("""
        MATCH (keanu:Actor {name: "Keanu Reeves"}), (matrix:Movie {title: "The Matrix"})
        CREATE (keanu)-[:ACTED_IN {role: "Neo"}]->(matrix)
        """)

        session.run("""
        MATCH (keanu:Actor {name: "Keanu Reeves"}), (john:Movie {title: "John Wick"})
        CREATE (keanu)-[:ACTED_IN {role: "John Wick"}]->(john)
        """)

        session.run("""
        MATCH (mcconaughey:Actor {name: "Matthew McConaughey"}), (inter:Movie {title: "Interstellar"})
        CREATE (mcconaughey)-[:ACTED_IN {role: "Cooper"}]->(inter)
        """)

        session.run("""
        MATCH (bale:Actor {name: "Christian Bale"}), (dk:Movie {title: "The Dark Knight"})
        CREATE (bale)-[:ACTED_IN {role: "Batman"}]->(dk)
        """)

        session.run("""
        MATCH (bale:Actor {name: "Christian Bale"}), (prestige:Movie {title: "The Prestige"})
        CREATE (bale)-[:ACTED_IN {role: "Alfred Borden"}]->(prestige)
        """)

        # 8. Relations réalisateurs -> films
        print("🔗 Création des relations réalisateurs-films...")
        session.run("""
        MATCH (nolan:Director {name: "Christopher Nolan"}),
              (inception:Movie {title: "Inception"}),
              (dk:Movie {title: "The Dark Knight"}),
              (prestige:Movie {title: "The Prestige"}),
              (inter:Movie {title: "Interstellar"})
        CREATE (nolan)-[:DIRECTED]->(inception)
        CREATE (nolan)-[:DIRECTED]->(dk)
        CREATE (nolan)-[:DIRECTED]->(prestige)
        CREATE (nolan)-[:DIRECTED]->(inter)
        """)

        # 9. Relations films -> genres
        print("🔗 Création des relations films-genres...")
        session.run("""
        MATCH (inception:Movie {title: "Inception"}),
              (scifi:Genre {name: "Sci-Fi"}),
              (action:Genre {name: "Action"}),
              (thriller:Genre {name: "Thriller"})
        CREATE (inception)-[:HAS_GENRE]->(scifi)
        CREATE (inception)-[:HAS_GENRE]->(action)
        CREATE (inception)-[:HAS_GENRE]->(thriller)
        """)

        session.run("""
        MATCH (matrix:Movie {title: "The Matrix"}),
              (scifi:Genre {name: "Sci-Fi"}),
              (action:Genre {name: "Action"})
        CREATE (matrix)-[:HAS_GENRE]->(scifi)
        CREATE (matrix)-[:HAS_GENRE]->(action)
        """)

        session.run("""
        MATCH (dk:Movie {title: "The Dark Knight"}),
              (action:Genre {name: "Action"}),
              (thriller:Genre {name: "Thriller"})
        CREATE (dk)-[:HAS_GENRE]->(action)
        CREATE (dk)-[:HAS_GENRE]->(thriller)
        """)

        # 10. Relations utilisateurs -> films
        print("🔗 Création des préférences utilisateurs...")
        session.run("""
        MATCH (alice:User {name: "Alice"}),
              (inception:Movie {title: "Inception"}),
              (matrix:Movie {title: "The Matrix"}),
              (inter:Movie {title: "Interstellar"})
        CREATE (alice)-[:LIKES {rating: 5}]->(inception)
        CREATE (alice)-[:LIKES {rating: 5}]->(matrix)
        CREATE (alice)-[:LIKES {rating: 4}]->(inter)
        """)

        session.run("""
        MATCH (bob:User {name: "Bob"}),
              (dk:Movie {title: "The Dark Knight"}),
              (john:Movie {title: "John Wick"})
        CREATE (bob)-[:LIKES {rating: 5}]->(dk)
        CREATE (bob)-[:LIKES {rating: 4}]->(john)
        """)

        # Statistiques
        print("\n📊 Statistiques:")
        stats = session.run("""
        MATCH (m:Movie) WITH count(m) as movies
        MATCH (a:Actor) WITH movies, count(a) as actors
        MATCH (d:Director) WITH movies, actors, count(d) as directors
        MATCH (g:Genre) WITH movies, actors, directors, count(g) as genres
        MATCH (u:User) WITH movies, actors, directors, genres, count(u) as users
        RETURN movies, actors, directors, genres, users
        """).single()

        print(f"  🎬 Films: {stats['movies']}")
        print(f"  🎭 Acteurs: {stats['actors']}")
        print(f"  🎥 Réalisateurs: {stats['directors']}")
        print(f"  📁 Genres: {stats['genres']}")
        print(f"  👤 Utilisateurs: {stats['users']}")


if __name__ == "__main__":
    print("🎬 Création de la base de données de films...\n")
    create_movie_database()
    print("\n✅ Terminé ! Va voir dans Neo4j Browser : MATCH (n) RETURN n")
    driver.close()
