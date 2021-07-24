from googlesearch import search
import pprint


def init_database(categories):
    kb = {}
    for category in categories:
        kb[category] = {}
    return kb


def wikify(query: str, N_candidates: int = 1, threshold: int = 15) -> list:
    """
    Wikify performs a Google search given a query to find the first suggested Wikipedia article.
    :param query: string containing queried term
    :param N_candidates: number of candidate Wikipedia entities to be saved. Useful if context is given.
    :param threshold: number of Google results before refining search
    :return wikis: list of candidate Wikipedia entities
    """
    # Retrieve items 0 to 4 from Google search
    init = 0
    N_results = 5

    wikis = []
    while len(wikis) < N_candidates:
        # Query Google API
        results = search(query, tld="com", num=25, start=init, stop=init + N_results, pause=2)
        for direction in results:  # Fpr each result
            # If a Wikipedia url is found and that url does not correspond to a media file
            if "wikipedia" in direction and "File" not in direction:
                wikis.append(direction)  # Add candidate
                if len(wikis) == N_candidates:
                    break
        init += N_results  # If no suitable result is found, retrieve items 4-9 from Google and repeat
        if init > threshold:  # If after a threshold number of items no wikipedia article is found, modify query.
            wikify("wikipedia " + query, N_candidates, threshold)
    return wikis


def normalise(entity_list: list, database: dict, category: str = "companies") -> None:
    """
    Normalise links a set of entities to their respective (approximate) wikipedia articles
    :param entity_list: list of entities to be linked
    :param database: dictionary containing known entities and their Wikipedia instances
    :param category: category in database to which items in entity_list belong to
    """
    # If category not in database, raise ValueError
    if category not in database.keys():
        raise ValueError("Specified category not in database!")

    # Else...
    for item in entity_list:
        # If category is empty append first Wikipedia candidate
        if not bool(database[category].keys()):
            candidates = wikify(item)
            database[category][item] = candidates[0]
            print(item, "has been added to the", category, "database")
        else:
            for key in database[category].keys():
                if item.lower() in key.lower() or key.lower() in item.lower():
                    database[category][item] = database[category][key]
                    print(item, "is in the", category, "database under different name:", key)
                    break
                elif item == key:
                    print(item, "is already in the", category, "database")
                    break
            if item not in database[category].keys():
                candidates = wikify(item)
                database[category][item] = candidates[0]
                print(item, "has been added to the", category, "database")



if __name__ == "__main__":
    company_list = ["NVIDIA", "Microsoft Corp", "Nvidia Ireland", "M&S Ltd"]
    product_list = ["Plastic bottle", "Hardwood Table", "Transistor", "Computer", "Container"]
    location_list = ["London", "Hong Kong", "Beijing", "Barcelona", "San Francisco", "Cape Town"]

    database = init_database(["companies", "products", "locations"])

    # print(30*"*", "COMPANIES", 30*"*")
    # normalise(company_list, database, category="companies")

    print(30 * "*", "PRODUCTS", 30 * "*")
    normalise(product_list, database, category="products")

    print(30 * "*", "LOCATIONS", 30 * "*")
    normalise(location_list, database, category="locations")
    pprint.pprint(database)
