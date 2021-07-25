from googlesearch import search
import pprint


def init_database(categories: list) -> dict:
    """
    Initialises database of normalised entities
    :param categories: set of entity categories present in the database
    :return: database dictionary
    """
    kb = {}
    for category in categories:
        kb[category] = {}
    return kb


def wikify(query: str, N_candidates: int = 1, threshold: int = 20) -> list:
    """
    Wikify performs a Google search given a query to find the first suggested Wikipedia article.
    :param query: string containing queried term
    :param N_candidates: number of candidate Wikipedia entities to be saved. Useful if context is given.
    :param threshold: number of Google results before refining search
    :return wikis: list of candidate Wikipedia entities
    """
    # Retrieve items 0 to 4 from Google search
    init = 0
    N_results = 10

    wikis = []
    while len(wikis) < N_candidates:
        # Query Google API
        results = search(query, tld="com", num=25, start=init, stop=init + N_results, pause=2)
        for direction in results:  # For each result
            # If a Wikipedia url is found and that url does not correspond to a media file
            if "wikipedia" in direction and "File" not in direction:
                wikis.append(direction)  # Add candidate
                if len(wikis) == N_candidates:
                    break
        init += N_results  # If no suitable result is found, retrieve items 4-9 from Google and repeat
        if init > threshold:  # If after a threshold number of items no wikipedia article is found, modify query.
            wikis = wikify("wikipedia " + query, N_candidates, threshold)
    return wikis


def normalise(entity_list: list, database: dict, category: str = "companies") -> None:
    """
    Normalise links a set of entities to their respective (approximate) Wikipedia articles
    :param entity_list: list of entities to be linked
    :param database: dictionary containing known entities and their Wikipedia instances
    :param category: category in database to which items in entity_list belong to
    """
    # If category not in database, raise ValueError
    if category not in database.keys():
        raise ValueError("Category of", category, "not in database!")

    # Else...
    for item in entity_list:
        # If category is empty, create a database entry with first Wikipedia candidate
        if not bool(database[category].keys()):
            candidates = wikify(item)
            database[category][item] = candidates[0]
            print(item, "has been added to the", category, "database")
        else:  # If category is not empty
            for key in database[category].keys():
                # Check if company is in database under different name
                if item.lower() in key.lower() or key.lower() in item.lower():
                    database[category][item] = database[category][key]
                    print(item, "is in the", category, "database under different name:", key)
                    break
                # Check if company is in database under same name
                elif item == key:
                    print(item, "is already in the", category, "database")
                    break
            # If not in database, create a database entry with first Wikipedia candidate
            if item not in database[category].keys():
                candidates = wikify(item)
                database[category][item] = candidates[0]
                print(item, "has been added to the", category, "database")


def normalise_ids(id_list, database):
    # If category not in database, raise ValueError
    if "serial numbers" not in database.keys():
        raise ValueError('Category of "serial numbers" not in database!')

    for item in id_list:
        # Unify format
        id_formatted = item.replace(' ', '').upper()

        if id_formatted in database["serial numbers"].keys():
            print(item, "is already in the serial numbers database")
        else:
            database["serial numbers"][item] = []
            print(item, "has been added to the serial numbers database")



def normalise_companies(company_list, database):
    normalise(company_list, database, category="companies")


def normalise_products(product_list, database):
    normalise(product_list, database, category="products")


def normalise_locations(location_list, database):
    normalise(location_list, database, category="locations")


if __name__ == "__main__":
    company_list = ["NVIDIA", "Microsoft Corp", "Nvidia Ireland", "M&S Ltd"]
    product_list = ["Plastic bottle", "Hardwood Table", "Transistor", "Computer", "Container"]
    location_list = ["London", "Hong Kong", "Beijing", "Barcelona", "San Francisco", "Cape Town"]
    # Assuming 'XYZ 13423 / ILD' and 'XYZ-13423-ILD' are different, since formatting of serial numbers is crucial
    # and can represent multiple product specifications
    ids = ['XYZ 13423 / ILD', 'ABC/ICL/20891NC', 'LZ548/G', 'XYZ-13423-ILD']

    database = init_database(["companies", "products", "locations", "serial numbers"])

    normalise_ids(ids, database)

    # print(30*"*", "COMPANIES", 30*"*")
    # normalise_companies(company_list, database)

    # print(30 * "*", "PRODUCTS", 30 * "*")
    # normalise_products(product_list, database)

    # print(30 * "*", "LOCATIONS", 30 * "*")
    # normalise_locations(location_list, database)

    pprint.pprint(database)
