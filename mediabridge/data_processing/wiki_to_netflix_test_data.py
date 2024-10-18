EXPECTED_SPARQL_QUERY ='''
        SELECT * WHERE {
            SERVICE wikibase:mwapi {
                bd:serviceParam wikibase:api "EntitySearch" ;
                                wikibase:endpoint "www.wikidata.org" ;
                                mwapi:search "The Room" ;
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
        
            FILTER (YEAR(?releaseDate) = 2003) .

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
    
        '''