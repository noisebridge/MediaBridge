import os
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()

base_dir = os.getenv('BASE_DIR')
user_agent = os.getenv('USER_AGENT')

netflix_data_path = os.path.join(base_dir, 'netflix_movies.txt')
output_csv_path = os.path.join(base_dir, 'netflix_to_wikidata.csv')

netflix_data = pd.read_csv(netflix_data_path, delimiter=',', names=['NetflixId', 'Year', 'Title'],  encoding='ISO-8859-1', on_bad_lines='skip')

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

for index, row in netflix_data.iloc[:200].iterrows():
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

df = pd.DataFrame(data)
df.to_csv(output_csv_path, index=False)
print('missing:', missing_count)
print('found:', df.shape[0])