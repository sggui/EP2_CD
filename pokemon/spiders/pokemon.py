import scrapy

class PokemonScraper(scrapy.Spider):
    name = 'pokemon_scraper'
    start_urls = ["https://pokemondb.net/pokedex/all"]

    def parse(self, response):
        pokemons = response.css('#pokedex > tbody > tr')
        for pokemon in pokemons:
            number = pokemon.css('td.cell-num span.infocard-cell-data::text').get()
            name = pokemon.css('td.cell-name a.ent-name::text').get()
            link = pokemon.css('td.cell-name a.ent-name::attr(href)').get()
            pokemon_url = response.urljoin(link)

            types = ", ".join(pokemon.css('td.cell-icon a.type-icon::text').getall())

            yield response.follow(pokemon_url,
                                  self.parse_pokemon,
                                  meta={
                                      'number': number,
                                      'name': name,
                                      'url': pokemon_url,
                                      'types': types
                                  })

    def parse_pokemon(self, response):
        number = response.meta['number']
        name = response.meta['name']
        pokemon_url = response.meta['url']
        types = response.meta['types']

        height = response.css('.vitals-table tr:contains("Height") td::text').get().strip()
        weight = response.css('.vitals-table tr:contains("Weight") td::text').get().strip()

        # Coletar todas as próximas evoluções, filtrando "None"
        evolutions = []
        current_pokemon_found = False
        for evo in response.css('.infocard-list-evo .infocard'):
            evo_number = evo.css('.text-muted small::text').get()
            evo_name = evo.css('.ent-name::text').get()
            evo_link = response.urljoin(evo.css('a::attr(href)').get())

            if evo_name and evo_name.strip() == name.strip():
                current_pokemon_found = True
            elif current_pokemon_found and evo_name and evo_number:
                evolutions.append(f"{evo_number} - {evo_name} - {evo_link}")

        evolutions_str = "; ".join(evolutions)

        abilities = []
        for ability in response.css('.vitals-table tr:contains("Abilities") td a'):
            ability_name = ability.css('::text').get()
            ability_url = response.urljoin(ability.css('::attr(href)').get())
            if ability_name:  # Certifique-se de que a habilidade é válida
                abilities.append({'name': ability_name, 'url': ability_url})

        yield {
            'number': number,
            'name': name,
            'url': pokemon_url,
            'types': types,
            'height_cm': height,
            'weight_kg': weight,
            'next_evolutions': evolutions_str if evolutions else "",  # Retorna vazio se não houver evoluções válidas
            'abilities': abilities,
        }
