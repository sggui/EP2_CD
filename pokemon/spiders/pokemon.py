import scrapy
from scrapy.http import Request

class PokemonScrapper(scrapy.Spider):
    name = 'pokemon_scrapper'
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

        height_cm = response.css('.vitals-table tr:contains("Height") td::text').get().strip()
        weight_kg = response.css('.vitals-table tr:contains("Weight") td::text').get().strip()

        evolutions = []
        current_pokemon_found = False
        for evo in response.css('.infocard-list-evo .infocard'):
            evo_number = evo.css('.text-muted small::text').get()
            evo_name = evo.css('.ent-name::text').get()
            evo_link = response.urljoin(evo.css('a::attr(href)').get())

            if evo_name and evo_name.strip() == name.strip():
                current_pokemon_found = True
            elif current_pokemon_found and evo_name and evo_number:
                evolutions.append(f"#{evo_number} - {evo_name} - {evo_link}")

        next_evolutions = "; ".join(evolutions) if evolutions else ""

        abilities = []
        ability_links = response.css('.vitals-table tr:contains("Abilities") td a::attr(href)').getall()
        ability_links = [response.urljoin(link) for link in ability_links]

        if ability_links:
            request = Request(ability_links[0], callback=self.parse_ability, dont_filter=True)
            request.meta['pending_abilities'] = ability_links[1:]
            request.meta['abilities'] = []
            request.meta['number'] = number
            request.meta['name'] = name
            request.meta['url'] = pokemon_url
            request.meta['types'] = types
            request.meta['height_cm'] = height_cm
            request.meta['weight_kg'] = weight_kg
            request.meta['next_evolutions'] = next_evolutions
            yield request
        else:
            yield {
                'number': number,
                'name': name,
                'url': pokemon_url,
                'types': types,
                'height_cm': height_cm,
                'weight_kg': weight_kg,
                'next_evolutions': next_evolutions,
                'abilities': abilities,
            }

    def parse_ability(self, response):
        ability_info = {
            'name': response.css('main > h1::text').get().strip(),
            'desc': response.css('.vitals-table > tbody > tr:nth-child(1) > td::text').get(),
            'effect': response.css('main > div > div > p').get(),
            'url': response.css('link[rel="canonical"]::attr(href)').get()  # Corrigi aqui a falta de aspas e parêntese
        }

        abilities = response.meta['abilities']
        abilities.append(ability_info)

        pending_abilities = response.meta['pending_abilities']
        if pending_abilities:
            next_request = Request(pending_abilities[0], callback=self.parse_ability, dont_filter=True)
            next_request.meta.update(response.meta)
            next_request.meta['abilities'] = abilities
            next_request.meta['pending_abilities'] = pending_abilities[1:]
            yield next_request
        else:
            yield {
                'number': response.meta['number'],
                'name': response.meta['name'],
                'url': response.meta['url'],
                'types': response.meta['types'],
                'height_cm': response.meta['height_cm'],
                'weight_kg': response.meta['weight_kg'],
                'next_evolutions': response.meta['next_evolutions'],
                'abilities': abilities,
            }
