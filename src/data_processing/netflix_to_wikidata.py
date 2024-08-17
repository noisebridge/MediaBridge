# Map netflix movies to wikidata
import requests

query = '''
SELECT DISTINCT ?item ?itemLabel ?rtid WHERE {
  ?item wdt:P136 wd:Q471839.
  ?item wdt:P577 ?pubdate.
  ?item wdt:P1258 ?rtid.
  FILTER((?pubdate >= "1990-01-01T00:00:00Z"^^xsd:dateTime) && ((?pubdate < "2000-01-01T00:00:00Z"^^xsd:dateTime)))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
'''

resp = requests.post('https://query.wikidata.org/sparql',
              headers={'User-Agent': 'Noisebridge MovieBot 0.0.1/Audiodude <audiodude@gmail.com>'},
              data={
                'query': query,
                'format': 'json',
              }
)
resp.raise_for_status()

data = resp.json()
ids =[d['rtid']['value'] for d in data['results']['bindings']]