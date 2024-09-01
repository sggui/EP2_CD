import pandas as pd
import json
import re
import os

# Caminho do arquivo de entrada
input_file_path = os.path.join(os.path.dirname(__file__), 'file.json')

with open(input_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)

def convert_height(height):
    height_clean = re.sub(r'\(.*?\)', '', height).strip()
    height_clean = re.sub(r'[^\d.]+', '', height_clean)
    try:
        meters = float(height_clean)
    except ValueError:
        meters = 0
    centimeters = meters * 100
    return f"{centimeters:.1f} cm"

def convert_weight(weight):
    weight_clean = re.sub(r'\(.*?\)', '', weight).strip()
    weight_clean = weight_clean.replace('Â', '').replace('\u00a0', ' ')
    return weight_clean

def remove_duplicates(items):
    seen = set()
    result = []
    for item in items:
        item_tuple = tuple(item.items())
        if item_tuple not in seen:
            seen.add(item_tuple)
            result.append(item)
    return result

def clean_html_tags(text):
    if text is None:
        return ""
    clean_text = re.sub(r'<.*?>', '', text)  # Remove todas as tags HTML
    return clean_text

def clean_abilities(abilities):
    cleaned_abilities = []
    for ability in abilities:
        ability['effect'] = clean_html_tags(ability.get('effect', ''))
        ability['desc'] = ability['desc'] if ability['desc'] is not None else 'N/A'  # Substitui desc nulo por 'N/A'
        cleaned_abilities.append(ability)
    return cleaned_abilities

df['height_cm'] = df['height_cm'].apply(convert_height)
df['weight_kg'] = df['weight_kg'].apply(convert_weight)
df['abilities'] = df['abilities'].apply(remove_duplicates)
df['abilities'] = df['abilities'].apply(clean_abilities)
df['number'] = pd.to_numeric(df['number'])
df = df.sort_values(by='number')

# Caminho dos arquivos de saída
output_csv_path = os.path.join(os.path.dirname(__file__), 'clean_pokemon.csv')
output_json_path = os.path.join(os.path.dirname(__file__), 'clean_pokemon.json')

# Salvando os resultados
df.to_csv(output_csv_path, index=False)
data_list = df.to_dict(orient='records')

with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(data_list, f, ensure_ascii=False, indent=4)

print("Processamento concluído e arquivos gerados.")
