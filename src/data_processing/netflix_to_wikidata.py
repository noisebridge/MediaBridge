# Map netflix movies to wikidata
import requests
import pandas as pd

netflix_data = pd.read_csv('../data/netflix_data.txt', delimiter=',', names=['NetflixId', 'Year', 'Title'])

def construct_query(title, year):
    query = '''
    SELECT * WHERE {
    SERVICE wikibase:mwapi {
        bd:serviceParam wikibase:api "EntitySearch" ;
                        wikibase:endpoint "www.wikidata.org" ;
                        mwapi:search %s ;
                        wikibase:limit 1 ;
                        mwapi:language "en" .
        ?item wikibase:apiOutputItem mwapi:item .
    }
    {
        ?item wdt:P31/wdt:P279* wd:Q11424 ;
            wdt:P577 ?releaseDate ;
            rdfs:label ?itemLabel .
        FILTER("%d-01-01"^^xsd:dateTime <= ?releaseDate && ?releaseDate < "%d-01-01"^^xsd:dateTime) .
        FILTER (lang(?itemLabel) = "en") .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . } 
    }
    }
    LIMIT 1
    ''' %(title, year, year + 1)
    return query

def get_wikidata_ids(title, year):
    query = construct_query(title, year)
    resp = requests.post('https://query.wikidata.org/sparql',
        headers={'User-Agent': 'Noisebridge MovieBot 0.0.1/Audiodude <audiodude@gmail.com>'},
        data={
            'query': query,
            'format': 'json',
        })
    
    resp.raise_for_status()
    data = resp.json()
    ids =[d['rtid']['value'] for d in data['results']['bindings']]
    return ids

data = []
for index, row in netflix_data.iterrows():
    title = row['Title']
    year = row['Year']
    netflix_id = row['NetflixId']
    wikidata_ids = get_wikidata_ids(title, year)
    print(title, year, wikidata_ids)
    if wikidata_ids:
        data.append({'netflix_id': netflix_id, 'wikidata_id': wikidata_ids[0],'title': title, 'year': year})

df = pd.DataFrame(data)