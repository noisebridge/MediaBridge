import pandas as pd
import zipfile
from pprint import pprint
import requests


#Reading in dataset
netflix_df = pd.read_csv("movie_titles.txt", header = None, encoding = "ISO-8859-1", delimiter = ",", on_bad_lines='skip')
netflix_df.columns = ["ID", "Year", "Title"] # renaming titles
netflix_df.Year = netflix_df.Year.astype("Int64") # removing decimal from year
sub_netflix_df = netflix_df.head(100) #working with subset of dataset for now

#Extracting movie feature info from request
def Wiki_feature_id(data, feature):
    feature_id = data[feature]['value'].split('/')[-1]
    return(feature_id)


#Getting list of movie IDs, genre IDs, and director IDs from request
def Wiki_query(dataset):
    wiki_movie_ids = []
    wiki_genres = []
    wiki_directors = []
    for index, row in dataset.iterrows():
        SPARQL = '''
        SELECT * WHERE {
          SERVICE wikibase:mwapi {
            bd:serviceParam wikibase:api "EntitySearch" ;
                            wikibase:endpoint "www.wikidata.org" ;
                            mwapi:search "%s" ;
                            wikibase:limit 1 ;
                            mwapi:language "en" .
            ?item wikibase:apiOutputItem mwapi:item .
          }
          {
            ?item wdt:P31/wdt:P279* wd:Q11424 ;
                  wdt:P577 ?releaseDate ;
                  rdfs:label ?itemLabel ;
                  OPTIONAL {?item wdt:P136 ?genreLabel.}
                  OPTIONAL {?item wdt:P57 ?directorLabel.}
            FILTER("%d-01-01"^^xsd:dateTime <= ?releaseDate && ?releaseDate < "%d-05-01"^^xsd:dateTime) .
            FILTER (lang(?itemLabel) = "en") .
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . } 
          }
        }
        LIMIT 1
        ''' % (row["Title"], row["Year"], row["Year"])

        response = requests.post('https://query.wikidata.org/sparql',
                      headers={'User-Agent': 'Noisebridge MovieBot 0.0.1/smaysen <smaysen@gmail.com>'},
                      data={
                        'query': SPARQL,
                        'format': 'json',
                      }
        )
        response.raise_for_status() 


        data = response.json()


        if len(data['results']['bindings']) < 1 or 'item' not in data['results']['bindings'][0].keys():
            wiki_movie_ids.append("NA")
        else:
            wiki_movie_ids.append(Wiki_feature_info(data['results']['bindings'][0], 'item'))


        if len(data['results']['bindings']) < 1 or 'genreLabel' not in data['results']['bindings'][0].keys():
            wiki_genres.append("NA")
        else:
            wiki_genres.append(Wiki_feature_info(data['results']['bindings'][0], 'genreLabel'))


        if len(data['results']['bindings']) < 1 or 'directorLabel' not in data['results']['bindings'][0].keys():
            wiki_directors.append("NA")
        else:
            wiki_directors.append(Wiki_feature_info(data['results']['bindings'][0], 'directorLabel'))

            
    return(wiki_movie_ids,wiki_genres, wiki_directors)

#Calling function
wiki_movie_ids_list, wiki_genres_list, wiki_directors_list = Wiki_query(sub_netflix_df)

#Adding movie, genres, and director ids to dataframe
sub_netflix_df["Movie_IDs"] = wiki_movie_ids_list
sub_netflix_df["Genre_IDs"] = wiki_genres_list
sub_netflix_df["Director_IDs"] = wiki_directors_list
