from neo4j import GraphDatabase


class ConsultasPokemon:
    def __init__(self, uri, usuario, senha):
        print("Inicializando conexão com o banco de dados...")
        self.driver = GraphDatabase.driver(uri, auth=(usuario, senha))
        print("Conexão estabelecida com sucesso!")

    def fechar(self):
        print("Fechando a conexão com o banco de dados...")
        self.driver.close()
        print("Conexão fechada.")

    def consulta_pokemons_atacantes(self):
        print("Executando consulta de Pokémons que podem atacar o Pikachu por sua fraqueza (peso > 10kg)...")
        with self.driver.session() as session:
            resultado = session.execute_read(self._consulta_pikachu_fraqueza)
        print("Pokémons que podem atacar o Pikachu por sua fraqueza (peso > 10kg):")
        for registro in resultado:
            print(f"{registro['name']} - Peso: {registro['weight_kg']} kg")

    @staticmethod
    def _consulta_pikachu_fraqueza(tx):
        consulta = """
        MATCH (pikachu:Pokemon {name: 'Pikachu'})-[:TEM_TIPO]->(tipo_pikachu)-[:FRACO_CONTRA]->(tipo_forte)
        MATCH (pokemon)-[:TEM_TIPO]->(tipo_forte)
        WHERE pokemon.weight_kg > 10
        RETURN DISTINCT pokemon.name AS name, pokemon.weight_kg AS weight_kg
        ORDER BY name
        """
        resultado = tx.run(consulta)
        return [record for record in resultado]

    def consulta_evolucoes_peso(self):
        print("Executando consulta de evoluções que dobram o peso do Pokémon...")
        with self.driver.session() as session:
            total_segunda = session.execute_read(
                self._consulta_segunda_evolucao)
            total_terceira = session.execute_read(
                self._consulta_terceira_evolucao)
        print(f"Número de segundas evoluções que dobram o peso: {
              total_segunda}")
        print(f"Número de terceiras evoluções que dobram o peso: {
              total_terceira}")

    @staticmethod
    def _consulta_segunda_evolucao(tx):
        consulta = """
        MATCH (p1:Pokemon)-[:EVOLUI_PARA]->(p2:Pokemon)
        WHERE p2.weight_kg >= 2 * p1.weight_kg
        RETURN COUNT(DISTINCT p2.number) AS total
        """
        resultado = tx.run(consulta)
        return resultado.single()['total']

    @staticmethod
    def _consulta_terceira_evolucao(tx):
        consulta = """
        MATCH (p1:Pokemon)-[:EVOLUI_PARA]->(p2:Pokemon)-[:EVOLUI_PARA]->(p3:Pokemon)
        WHERE p2.weight_kg >= 2 * p1.weight_kg AND p3.weight_kg >= 2 * p2.weight_kg
        RETURN COUNT(DISTINCT p3.number) AS total
        """
        resultado = tx.run(consulta)
        return resultado.single()['total']


if __name__ == "__main__":
    # Configurações de conexão com o Neo4j
    # Substitua pela URI do seu banco de dados
    uri = "neo4j+ssc://bed75cae.databases.neo4j.io"
    usuario = "neo4j"
    # Substitua pela sua senha real
    senha = "4ynMS_D_TNDquA_uIDA_yvWdXdNBuP-2Y5tSgFoU3iA"

    # Inicializa a classe e executa as consultas
    consultas = ConsultasPokemon(uri, usuario, senha)
    consultas.consulta_pokemons_atacantes()
    consultas.consulta_evolucoes_peso()
    consultas.fechar()
    print("Consultas concluídas com sucesso.")
