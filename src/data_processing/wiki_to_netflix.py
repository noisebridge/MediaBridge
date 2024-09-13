import requests
import csv

base_dir = 'src/data/'
user_agent = 'Noisebridge MovieBot 0.0.1/Audiodude <audiodude@gmail.com>'

missing_count = 0
num_rows = 42

# Reading netflix text file
def read_netflix_txt(txt_file):
    with open(txt_file, "r", encoding = "ISO-8859-1") as netflix_data:
        netflix_list = [line.rstrip().split(',', 2) for line in netflix_data.readlines()[0:num_rows]]
    return(netflix_list)

# Writing netflix csv file
def create_netflix_csv(csv_name, data_list):   
    with open(csv_name, 'w') as netflix_csv:
        csv.writer(netflix_csv).writerows(data_list)

# Extracting movie info from Wiki data
def wiki_feature_info(data, key):
    if len(data['results']['bindings']) < 1 or key not in data['results']['bindings'][0]:
        return 'NA'
    else:
        return({d['genreLabel']['value'] for d in data['results']['bindings'] if 'genreLabel' in d} if key == 'genreLabel'
                else data['results']['bindings'][0][key]['value'].split('/')[-1])

# Adding movie info to netflix csv file
def add_movie_info_to_csv(data_csv, movies, genres, directors):
    with open(data_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        data_list = list(csv_reader)
        
    for i in range(0, len(data_list)-1):
        if movies[i] and genres[i] and directors[i] != "NA":
            data_list[i].extend((movies[i], genres[i], directors[i]))
            
    with open(data_csv, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(data_list)  

# Getting list of movie IDs, genre IDs, and director IDs from request
def wiki_query(data_csv, user_agent):
    wiki_movie_ids = []
    wiki_genres = []
    wiki_directors = []
    
    # csv_reader = list(csv.reader(open(data_csv)))
    
    for row in data_csv:
        if row[1] != "NULL":
            SPARQL = '''
            SELECT * WHERE {
                SERVICE wikibase:mwapi {
                    bd:serviceParam wikibase:api "EntitySearch" ;
                                    wikibase:endpoint "www.wikidata.org" ;
                                    mwapi:search "%(Title)s" ;
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
            
                FILTER (YEAR(?releaseDate) = %(Year)d) .

                ?item rdfs:label ?itemLabel .
                FILTER (lang(?itemLabel) = "en") .

                OPTIONAL {
                    ?item wdt:P136 ?genre .
                    ?genre rdfs:label ?genreLabel .
                    FILTER (lang(?genreLabel) = "en") .
                }

                OPTIONAL {?item wdt:P57 ?director.
                                ?director rdfs:label ?directorLabel.
                                FILTER (lang(?directorLabel) = "en")}

                SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
                }
        
            ''' % {'Title': row[2], 'Year': int(row[1])}

            response = requests.post('https://query.wikidata.org/sparql',
                      headers={'User-Agent': user_agent},
                      data={
                        'query': SPARQL,
                        'format': 'json',
                      }
        )
            response.raise_for_status() 
            
            data = response.json()
            
            wiki_movie_ids.append(wiki_feature_info(data, 'item'))
            wiki_genres.append(wiki_feature_info(data, 'genreLabel'))
            wiki_directors.append(wiki_feature_info(data, 'directorLabel'))
        
    return(wiki_movie_ids, wiki_genres, wiki_directors)

# Calling all functions
processed_data = []

netflix_file = read_netflix_txt(base_dir + 'netflix_movies.txt')

netflix_csv = base_dir + 'netflix_movies.csv'

wiki_movie_ids_list, wiki_directors_list, wiki_genres_list = wiki_query(netflix_file, user_agent)

for index, row in enumerate(netflix_file):
    title, year, netflix_id = row[0], int(row[1]), row[2]
    if wiki_movie_ids_list[index] == 'NA':
        missing_count += 1
    else:
        processed_data.append([title, year, netflix_id, wiki_movie_ids_list[index], wiki_genres_list[index], wiki_directors_list[index]])

create_netflix_csv(netflix_csv, processed_data)

print('missing:', missing_count, '(', missing_count / num_rows * 100, '%)')
print('found:', num_rows - missing_count, '(', (num_rows - missing_count) / num_rows * 100, '%)')
print('total:', num_rows)