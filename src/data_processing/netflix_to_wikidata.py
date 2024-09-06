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
    for line in file:
        row = line.split(',', 2)
        netflix_data.append({
            'NetflixId': row[0].strip(),
            'Year': row[1].strip(),
            'Title': row[2].strip()
        })


def construct_query(title, year):
    query = '''
    SELECT * WHERE {
        SERVICE wikibase:mwapi {
            bd:serviceParam wikibase:api "EntitySearch" ;
                            wikibase:endpoint "www.wikidata.org" ;
                            mwapi:search "%(search_term)s" ;
                            mwapi:language "en" .
            ?item wikibase:apiOutputItem mwapi:item .
        }

        ?item wdt:P31/wdt:P279* wd:Q11424 .
        
        {
            # Get US release date
            ?item p:P577 ?releaseDateStatement .
            ?releaseDateStatement ps:P577 ?releaseDate .
            ?releaseDateStatement pq:P291 wd:Q30 .  
        }
        UNION
        {
            # Get unspecified release date
            ?item p:P577 ?releaseDateStatement .
            ?releaseDateStatement ps:P577 ?releaseDate .
            FILTER NOT EXISTS { ?releaseDateStatement pq:P291 ?country }
        }
       
        FILTER (YEAR(?releaseDate) = %(release_year)d) .
        
        OPTIONAL {
            ?item wdt:P136 ?genre .
            ?genre rdfs:label ?genreLabel .
            FILTER (lang(?genreLabel) = "en") .
        }

        ?item rdfs:label ?itemLabel .
        FILTER (lang(?itemLabel) = "en") .

        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    }
    ''' % {"search_term": title, "release_year": year}
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
        return None, None, None

    wikidata_id = data['results']['bindings'][0]['item']['value'].split('/')[-1]

    genres = {d['genreLabel']['value'] for d in data['results']['bindings'] if 'genreLabel' in d}

    print(data)

    return wikidata_id, genres, main_subjects

data = []
missing_count = 0
num_rows = 420

for row in netflix_data[:num_rows]:
    title = row['Title']
    year = int(row['Year'])
    netflix_id = row['NetflixId']
    wikidata_id, genres, main_subjects = get_wikidata_data(title, year)
    if wikidata_id:
        print(f'found: {title} ({year})')
        data.append({
            'netflix_id': netflix_id,
            'wikidata_id': wikidata_id,
            'title': title,
            'year': year,
            'genres': list(genres),
        })
    else:
        print(f'missing: {title} ({year})')
        missing_count += 1


with open(output_csv_path, mode='w', newline='', encoding='ISO-8859-1') as file:
    writer = csv.DictWriter(file, fieldnames=['netflix_id', 'wikidata_id', 'title', 'year', 'genres', 'main_subjects'])
    writer.writeheader()
    writer.writerows(data)

print('missing:', missing_count, '(', missing_count / num_rows * 100, '%)')
print('found:', num_rows - missing_count, '(', (num_rows - missing_count) / num_rows * 100, '%)')
print('total:', num_rows)