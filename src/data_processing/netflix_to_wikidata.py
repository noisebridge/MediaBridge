import os
from dotenv import load_dotenv
import requests
import csv

load_dotenv()

base_dir = 'src/data'
user_agent = 'Noisebridge MovieBot 0.0.1/Audiodude <audiodude@gmail.com>'

netflix_data_path = os.path.join(base_dir, 'netflix_movies.txt')
output_csv_path = os.path.join(base_dir, 'netflix_to_wikidata.csv')

netflix_data = []

with open(netflix_data_path, mode='r', encoding='ISO-8859-1') as file:
    reader = csv.reader(file, delimiter=',')
    for row in reader:
        if len(row) == 3: 
            netflix_data.append({
                'NetflixId': row[0],
                'Year': row[1],
                'Title': row[2]
            })


def construct_query(title, year):
    query = '''
    SELECT * WHERE {
        SERVICE wikibase:mwapi {
            bd:serviceParam wikibase:api "EntitySearch" ;
                            wikibase:endpoint "www.wikidata.org" ;
                            mwapi:search "%s" ;
                            wikibase:limit 1 ;
                            mwapi:language "en" .
            ?item wikibase:apiOutputItem mwapi:item .
        }

        ?item wdt:P31/wdt:P279* wd:Q11424 .

        ?item wdt:P577 ?releaseDate .
        FILTER (YEAR(?releaseDate) >= %d && YEAR(?releaseDate) <= %d) .
        

        OPTIONAL {
            ?item wdt:P136 ?genre .
            ?genre rdfs:label ?genreLabel .
            FILTER (lang(?genreLabel) = "en") .
        }

        ?item rdfs:label ?itemLabel .
        FILTER (lang(?itemLabel) = "en") .

        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    }
    LIMIT 1
    ''' % (title, year - 2, year + 2)
    return query

def get_wikidata_data(title, year):
    query = construct_query(title, year)
    resp = requests.post('https://query.wikidata.org/sparql',
        headers={'User-Agent': user_agent},
        data={
            'query': query,
            'format': 'json',
        })
    
    resp.raise_for_status()
    data = resp.json()

    if not data['results']['bindings']:
        return None, None

    wikidata_id = data['results']['bindings'][0]['item']['value'].split('/')[-1]

    genres = [d['genreLabel']['value'] for d in data['results']['bindings'] if 'genreLabel' in d]

    return wikidata_id, genres

data = []
missing_count = 0
num_rows = 200

for row in netflix_data[:num_rows]:
    title = row['Title']
    year = int(row['Year'])
    netflix_id = row['NetflixId']
    wikidata_id, genres = get_wikidata_data(title, year)
    if wikidata_id:
        print(f'found: {title} ({year})')
        data.append({
            'netflix_id': netflix_id,
            'wikidata_id': wikidata_id,
            'title': title,
            'year': year,
            'genres': ', '.join(genres) if genres else 'None'
        })
    else:
        print(f'missing: {title} ({year})')
        missing_count += 1


with open(output_csv_path, mode='w', newline='', encoding='ISO-8859-1') as file:
    writer = csv.DictWriter(file, fieldnames=['netflix_id', 'wikidata_id', 'title', 'year', 'genres'])
    writer.writeheader()
    writer.writerows(data)

print('missing:', missing_count)
print('found:', num_rows - missing_count)