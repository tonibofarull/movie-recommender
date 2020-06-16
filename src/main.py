from neo4j import GraphDatabase
import pandas as pd

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "1234"))

k = 10 # nearest neighbors (most similar users) to consider
movies_common = 3 # how many movies in common to be consider an user similar
users_common = 2 # minimum number of similar users that have seen the movie to consider it
threshold_sim = 0.9 # threshold to consider users similar

def load_data():
    with driver.session() as session:
        session.run("""MATCH ()-[r]->() DELETE r""")
        session.run("""MATCH (r) DELETE r""")
        
        print("Loading movies...")
        
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_movies.csv" AS csv
            CREATE (:Movie {title: csv.title})
            """)
            
        print("Loading gradings...")
            
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_grade.csv" AS csv
            MERGE (m:Movie {title: csv.title}) 
            MERGE (u:User {id: toInteger(csv.user_id)})
            CREATE (u)-[:RATED {grading : toInteger(csv.grade)}]->(m)
            """)
            
        print("Loading genres...")
            
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_genre.csv" AS csv
            MERGE (m:Movie {title: csv.title})
            MERGE (g:Genre {genre: csv.genre})
            CREATE (m)-[:HAS_GENRE]->(g)
            """)
            
        print("Loading keywords...")
            
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_keyword.csv" AS csv
            MERGE (m:Movie {title: csv.title})
            MERGE (k:Keyword {keyword: csv.keyword})
            CREATE (m)-[:HAS_KEYWORD]->(k)
            """)
            
        print("Loading productors...")
            
        session.run("""
            LOAD CSV WITH HEADERS FROM "file:///out_productor.csv" AS csv
            MERGE (m:Movie {title: csv.title})
            MERGE (p:Productor {name: csv.productor})
            CREATE (m)-[:HAS_PRODUCTOR]->(p)
            """)

def queries():
    while True:
        userid = int(input("Input user: "))
        m = int(input("Number of recommendations: "))
        
        genres = []
        if int(input("Filter by genre? ")):
            with driver.session() as session:
                try:
                    q = session.run(f"""MATCH (g:Genre) RETURN g.genre AS genre""")
                    result = []
                    for i, r in enumerate(q):
                        result.append(r["genre"])
                    df = pd.DataFrame(result, columns=["genre"])
                    print()
                    print(df)
                    inp = input("Select the genres by a list of indexes: ")
                    if len(inp) != 0:
                        inp = inp.split(" ")
                        genres = [df["genre"].iloc[int(x)] for x in inp]
                except:
                    print("Error")
                    
        with driver.session() as session:
            q = session.run(f"""
                    MATCH (u1:User {{id : {userid}}})-[r:RATED]-(m:Movie)
                    RETURN m.title AS title, r.grading AS grade
                    ORDER BY grade DESC
                    """)
            
            print()
            print("Your ratings are the following:")
            
            result = []
            for r in q:
                result.append([r["title"], r["grade"]])
                
            if len(result) == 0:
                print("No ratings found")
            else:
                df = pd.DataFrame(result, columns=["title", "grade"])
                print()
                print(df.to_string(index=False))
            print()
            
            session.run(f"""
                MATCH (u1:User)-[s:SIMILARITY]-(u2:User)
                DELETE s
                """)

            session.run(f"""
                MATCH (u1:User {{id : {userid}}})-[r1:RATED]-(m:Movie)-[r2:RATED]-(u2:User)
                WITH
                    u1, u2,
                    COUNT(m) AS movies_common,
                    SUM(r1.grading * r2.grading)/(SQRT(SUM(r1.grading^2)) * SQRT(SUM(r2.grading^2))) AS sim
                WHERE movies_common >= {movies_common} AND sim > {threshold_sim}
                MERGE (u1)-[s:SIMILARITY]-(u2)
                SET s.sim = sim
                """)
                
            Q_GENRE = ""
            if (len(genres) > 0):
                Q_GENRE = "AND ((SIZE(gen) > 0) AND "
                Q_GENRE += "(ANY(x IN " + str(genres) + " WHERE x IN gen))"
                Q_GENRE += ")"

            q = session.run(f"""
                    MATCH (u1:User {{id : {userid}}})-[s:SIMILARITY]-(u2:User)
                    WITH u1, u2, s
                    ORDER BY s.sim DESC LIMIT {k}
                    MATCH (m:Movie)-[r:RATED]-(u2)
                    OPTIONAL MATCH (g:Genre)--(m)
                    WITH u1, u2, s, m, r, COLLECT(DISTINCT g.genre) AS gen
                    WHERE NOT((m)-[:RATED]-(u1)) {Q_GENRE}
                    WITH
                        m.title AS title,
                        SUM(r.grading * s.sim)/SUM(s.sim) AS grade,
                        COUNT(u2) AS num,
                        gen
                    WHERE num >= {users_common}
                    RETURN title, grade, num, gen
                    ORDER BY grade DESC, num DESC
                    LIMIT {m}
                    """)

            print("Recommended movies:")

            result = []
            for r in q:
                result.append([r["title"], r["grade"], r["num"], r["gen"]])
            if len(result) == 0:
                print("No recommendations found")
                print()
                continue
            df = pd.DataFrame(result, columns=["title", "avg grade", "num recommenders", "genres"])
            print()
            print(df.to_string(index=False))
            print()

if __name__ == "__main__":
    if int(input("Load data? ")):
        load_data()
    queries()
