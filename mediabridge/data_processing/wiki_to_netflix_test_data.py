EXPECTED_SPARQL_QUERY = """
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
        """

WIKIDATA_RESPONSE_THE_ROOM = {
    "head": {
        "vars": [
            "item",
            "releaseDateStatement",
            "releaseDate",
            "itemLabel",
            "genre",
            "genreLabel",
            "director",
            "directorLabel",
        ]
    },
    "results": {
        "bindings": [
            {
                "item": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q533383",
                },
                "director": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q860114",
                },
                "directorLabel": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": "Tommy Wiseau",
                },
                "genre": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q1054574",
                },
                "genreLabel": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": "romance film",
                },
                "releaseDateStatement": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/statement/Q533383-EE3D4972-4B06-4B0D-869B-23504D828AE6",
                },
                "releaseDate": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "type": "literal",
                    "value": "2003-06-27T00:00:00Z",
                },
                "itemLabel": {"xml:lang": "en", "type": "literal", "value": "The Room"},
            },
            {
                "item": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q533383",
                },
                "director": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q860114",
                },
                "directorLabel": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": "Tommy Wiseau",
                },
                "genre": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q459290",
                },
                "genreLabel": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": "independent film",
                },
                "releaseDateStatement": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/statement/Q533383-EE3D4972-4B06-4B0D-869B-23504D828AE6",
                },
                "releaseDate": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "type": "literal",
                    "value": "2003-06-27T00:00:00Z",
                },
                "itemLabel": {"xml:lang": "en", "type": "literal", "value": "The Room"},
            },
            {
                "item": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q533383",
                },
                "director": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q860114",
                },
                "directorLabel": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": "Tommy Wiseau",
                },
                "genre": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q130232",
                },
                "genreLabel": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": "drama film",
                },
                "releaseDateStatement": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/statement/Q533383-EE3D4972-4B06-4B0D-869B-23504D828AE6",
                },
                "releaseDate": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "type": "literal",
                    "value": "2003-06-27T00:00:00Z",
                },
                "itemLabel": {"xml:lang": "en", "type": "literal", "value": "The Room"},
            },
        ]
    },
}
