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

        ?item wdt:P31/wdt:P279* ?type .
        FILTER (?type IN (
            wd:Q11424,    # Film
            wd:Q5398426,  # Television Series
            wd:Q1259759,  # Television Miniseries
            wd:Q202866,   # Animated Film
            wd:Q24862,    # Documentary Film
            wd:Q506240,   # Short Film
            wd:Q204370,   # Television Film
            wd:Q471839,   # Animated Television Series
            wd:Q21191270, # Web Series
            wd:Q7725310,  # Reality Television Series
            wd:Q579956,   # Anthology Series
            wd:Q15416,    # Television Program
            wd:Q28018927  # Television Special
        )).

        OPTIONAL {
            ?item wdt:P577 ?releaseDate .
            FILTER (YEAR(?releaseDate) >= %d && YEAR(?releaseDate) <= %d) .
        }

        ?item rdfs:label ?itemLabel .
        FILTER (lang(?itemLabel) = "en") .

        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    }
    LIMIT 1
    ''' % (title, year - 2, year + 2)
    return query

def get_wikidata_ids(title, year):
    query = construct_query(title, year)
    resp = requests.post('https://query.wikidata.org/sparql',
        headers={'User-Agent': user_agent},
        data={
            'query': query,
            'format': 'json',
        })
    
    resp.raise_for_status()
    data = resp.json()
    ids = [d['item']['value'].split('/')[-1] for d in data['results']['bindings']]
    return ids

data = []
missing_count = 0

for index, row in netflix_data.iloc[:500].iterrows():
    title = row['Title']
    year = int(row['Year'])
    netflix_id = row['NetflixId']
    wikidata_ids = get_wikidata_ids(title, year)
    if wikidata_ids:
        print('found:', title, year)
        data.append({'netflix_id': netflix_id, 'wikidata_id': wikidata_ids[0], 'title': title, 'year': year})
    else:
        print('missing:', title, year)
        missing_count += 1

df = pd.DataFrame(data)
df.to_csv(output_csv_path, index=False)
print('missing:', missing_count)
print('found:', df.shape[0])
