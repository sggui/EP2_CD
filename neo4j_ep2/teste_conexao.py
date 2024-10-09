from neo4j import GraphDatabase

uri = "neo4j+ssc://bed75cae.databases.neo4j.io"  # Substitua pela sua URI
usuario = "neo4j"
senha = "4ynMS_D_TNDquA_uIDA_yvWdXdNBuP-2Y5tSgFoU3iA"

driver = GraphDatabase.driver(uri, auth=(usuario, senha))

try:
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        print("Conexão bem-sucedida! Resultado do teste:",
              result.single()["test"])
except Exception as e:
    print("Erro ao conectar ao banco de dados:", e)
finally:
    driver.close()
