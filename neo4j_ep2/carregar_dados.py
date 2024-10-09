from neo4j import GraphDatabase
import json
import re


class CarregarDadosPokemon:
    def __init__(self, uri, usuario, senha):
        print("Inicializando conexão com o banco de dados...")
        self.driver = GraphDatabase.driver(uri, auth=(usuario, senha))
        print("Conexão estabelecida com sucesso!")

    def fechar(self):
        print("Fechando a conexão com o banco de dados...")
        self.driver.close()
        print("Conexão fechada.")

    def carregar_dados(self, arquivo_json):
        print(f"Lendo dados do arquivo {arquivo_json}...")
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        print(f"{len(dados)} Pokémons carregados do JSON.")
        with self.driver.session() as session:
            print("Limpando a base de dados...")
            session.execute_write(self._limpar_base)
            print("Base de dados limpa.")
            print("Criando índices...")
            session.execute_write(self._criar_indices)
            print("Índices criados.")
            print("Inserindo Pokémons no banco de dados...")
            for idx, pokemon in enumerate(dados, start=1):
                print(f"Inserindo Pokémon {
                      idx}/{len(dados)}: {pokemon['name']}")
                session.execute_write(self._criar_pokemon, pokemon)
            print("Todos os Pokémons foram inseridos.")
            print("Criando relacionamentos de fraqueza entre tipos...")
            session.execute_write(self._criar_fraquezas_tipo)
            print("Relacionamentos de fraqueza criados.")

    @staticmethod
    def _limpar_base(tx):
        tx.run("MATCH (n) DETACH DELETE n")

    @staticmethod
    def _criar_indices(tx):
        tx.run("CREATE INDEX IF NOT EXISTS FOR (p:Pokemon) ON (p.name)")
        tx.run("CREATE INDEX IF NOT EXISTS FOR (t:Tipo) ON (t.name)")
        tx.run("CREATE INDEX IF NOT EXISTS FOR (h:Habilidade) ON (h.name)")

    @staticmethod
    def _criar_pokemon(tx, pokemon):
        # Extrair valores numéricos de height_cm e weight_kg
        height_cm = float(re.sub(r'[^\d.]+', '', pokemon['height_cm']))
        weight_kg = float(re.sub(r'[^\d.]+', '', pokemon['weight_kg']))

        # Criar nó do Pokémon
        tx.run("""
        MERGE (p:Pokemon {number: $number})
        SET p.name = $name,
            p.height_cm = $height_cm,
            p.weight_kg = $weight_kg,
            p.url = $url
        """, number=pokemon['number'], name=pokemon['name'], height_cm=height_cm,
               weight_kg=weight_kg, url=pokemon['url'])

        # Criar tipos e relacionamentos
        types = [t.strip() for t in pokemon['types'].split(',')]
        for tipo in types:
            tx.run("""
            MERGE (t:Tipo {name: $tipo})
            MERGE (p:Pokemon {number: $number})
            MERGE (p)-[:TEM_TIPO]->(t)
            """, tipo=tipo, number=pokemon['number'])

        # Criar habilidades e relacionamentos
        for habilidade in pokemon.get('abilities', []):
            tx.run("""
            MERGE (h:Habilidade {name: $name})
            SET h.description = $description,
                h.effect = $effect,
                h.url = $url
            MERGE (p:Pokemon {number: $number})
            MERGE (p)-[:TEM_HABILIDADE]->(h)
            """, name=habilidade['name'], description=habilidade['desc'], effect=habilidade['effect'],
                   url=habilidade['url'], number=pokemon['number'])

        # Criar evoluções
        for evolucao in pokemon.get('next_evolutions', []):
            tx.run("""
            MERGE (p1:Pokemon {number: $number1})
            MERGE (p2:Pokemon {number: $number2})
            MERGE (p1)-[:EVOLUI_PARA]->(p2)
            """, number1=pokemon['number'], number2=evolucao['number'])

    @staticmethod
    def _criar_fraquezas_tipo(tx):
        # Lista completa de fraquezas entre tipos (você deve completar esta lista)
        fraquezas = [
            ('Normal', 'Fighting'),
            ('Fire', 'Water'), ('Fire', 'Ground'), ('Fire', 'Rock'),
            ('Water', 'Electric'), ('Water', 'Grass'),
            ('Electric', 'Ground'),
            ('Grass', 'Fire'), ('Grass', 'Ice'), ('Grass', 'Poison'),
            ('Grass', 'Flying'), ('Grass', 'Bug'),
            # Adicione todas as combinações necessárias
        ]
        for tipo1, tipo2 in fraquezas:
            tx.run("""
            MATCH (t1:Tipo {name: $tipo1}), (t2:Tipo {name: $tipo2})
            MERGE (t1)-[:FRACO_CONTRA]->(t2)
            """, tipo1=tipo1, tipo2=tipo2)


if __name__ == "__main__":
    # Configurações de conexão com o Neo4j
    uri = "neo4j+ssc://bed75cae.databases.neo4j.io"
    usuario = "neo4j"
    senha = "4ynMS_D_TNDquA_uIDA_yvWdXdNBuP-2Y5tSgFoU3iA"

    # Caminho para o arquivo JSON com os dados dos Pokémons
    arquivo_json = "clean_pokemon.json"

    # Inicializa a classe e carrega os dados
    carregador = CarregarDadosPokemon(uri, usuario, senha)
    carregador.carregar_dados(arquivo_json)
    carregador.fechar()
    print("Carregamento dos dados concluído com sucesso.")
