import pprint
import re

from fuzzywuzzy import fuzz, process
from googlesearch import search
from googletrans import Translator


def init_database(categories: list) -> dict:
    """
    Initialises database of normalised entities.

    :param categories: set of entity categories present in the database
    :return kb: database dictionary of categories, where each category is itself a dictionary
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


def normalise(entity: str, database: dict, category: str = "companies") -> None:
    """
    Normalise links a set of entities to their respective (approximate) Wikipedia articles
    :param entity: list of entities to be linked
    :param database: dictionary containing known entities and their Wikipedia instances
    :param category: category in database to which items in entity_list belong to
    """
    # If category not in database, raise ValueError
    if category not in database.keys():
        raise ValueError("Category of", category, "not in database!")

    # Translate entity_list to english text
    translation = translator.translate(entity, dest="en")

    # If API limit reached
    if str(translation._response) == "<Response [429 Too Many Requests]>":
        print("WARNING: Too Many Requests to Google Translator API. Translation functionality deactivated.")

    # Else...
    # If category is empty, create a database entry with first Wikipedia candidate
    if not bool(database[category].keys()):
        candidates = wikify(translation.text)
        database[category][translation.text] = candidates[0]
        print(f"{translation.origin} [{translation.src}] ({translation.text}, [{translation.dest}]) "
              f"has been added to the {category} database with value: {candidates[0]}")
    else:  # If category is not empty
        for key in database[category].keys():
            # Check if company is in database under different name
            if translation.text.lower() in key.lower() or key.lower() in translation.text.lower():
                # Add repeated occurrence as new key, but pointing to same entity value
                database[category][translation.text] = database[category][key]
                print(f"{translation.origin} [{translation.src}] ({translation.text}, [{translation.dest}]) "
                      f"is in the {category} database under different name: {key} ({database[category][key]})")
                break
            # Check if company is in database under same name
            elif translation.text == key:
                print(f"{translation.origin} [{translation.src}] ({translation.text}, [{translation.dest}]) "
                      f"is already in the {category} database")
                break
        # If not in database, create a database entry with first Wikipedia candidate
        if translation.text not in database[category].keys():
            candidates = wikify(translation.text)
            database[category][translation.text] = candidates[0]
            print(f"{translation.origin} [{translation.src}] ({translation.text}, [{translation.dest}]) "
                  f"has been added to the {category} database with value: {candidates[0]}")


def group_by_value(database):
    reversed_database = {}
    for key in database.keys():
        # If category is empty, create an entry with first database item
        if not bool(reversed_database.keys()):
            val = database[key]
            reversed_database[val] = [key]
        else:  # If category is not empty...
            val = database[key]
            # ...check if entity is already in category
            if val in reversed_database.keys():
                # If instance of entity is NOT already in the list
                if key not in reversed_database[val]:
                    reversed_database[val].append(key)
            #  if entity is not already in category
            else:
                reversed_database[val] = [key]
    return reversed_database


def normalise_companies(company_list, database):
    # Part 1 - link each entity to its respective Wikipedia entry separately
    for company in company_list:
        normalise(company, database, category="companies")
    # Part 2 - group entities by their Wikipedia entries
    database["companies"] = group_by_value(database["companies"])


def normalise_products(product_list, database):
    # Part 1 - link each entity to its respective Wikipedia entry separately
    for product in product_list:
        normalise(product, database, category="products")
    # Part 2 - group entities by their Wikipedia entries
    database["products"] = group_by_value(database["products"])


def normalise_locations(location_list, database):
    # Part 1 - link each entity to its respective Wikipedia entry separately
    for location in location_list:
        normalise(location, database, category="locations")
    # Part 2 - group entities by their Wikipedia entries
    database["locations"] = group_by_value(database["locations"])


def normalise_ids(id_list, database):
    # Parts 1 & 2 combined
    # If category not in database, raise ValueError
    if "serial numbers" not in database.keys():
        raise ValueError('Category of "serial numbers" not in database!')

    for item in id_list:
        # Unify format with regex - substitute special characters with hyphen and capitalize
        id_formatted = re.sub('[^0-9a-zA-Z]+', '-', item).upper()
        if id_formatted in database["serial numbers"].keys():
            database["serial numbers"][id_formatted].append(item)
            print(item, "is already in the serial numbers database as", id_formatted)
        else:
            database["serial numbers"][id_formatted] = [item]
            print(item, "has been added to the serial numbers database under key", id_formatted)


def normalise_address(address_list,  database, threshold=90):
    # Part 1 & 2 combined
    # If category not in database, raise ValueError
    if "addresses" not in database.keys():
        raise ValueError('Category of "addresses" not in database!')

    for item in address_list:
        if bool(database["addresses"].keys()):
            candidate, similarity = process.extractOne(item, database["addresses"].keys(), scorer=fuzz.token_set_ratio)
            if similarity > threshold:
                database["addresses"][candidate].append(item)
                print(item, "is already in the addresses database with the following key:", candidate)
                continue

        address_formatted = item.upper()
        database["addresses"][address_formatted] = []
        print(item, "has been added to the serial numbers database as:", address_formatted)



if __name__ == "__main__":
    # Init the Google API translator
    translator = Translator()

    company_list = ["NVIDIA", "Microsoft Corp", "Nvidia Ireland", "M&S Ltd"]
    product_list = ["Plastic bottle", "Botella de plastico", "Пластиковая бутылка", "塑料瓶", "Transistor", "ट्रांजिस्टर", "Tanker"]
    location_list = ["London", "लंडन", "London, Eng", "Beijing", "北京", "Пекин"]
    # Assuming 'XYZ 13423 / ILD' and 'XYZ-13423-ILD' are the same
    ids = ['XYZ 13423 / ILD', 'ABC/ICL/20891NC', 'LZ548/G', 'XYZ--13423-ILD', 'ABC-ICL 20891NC', 'ABC--ICL//20891NC']
    addresses = ["44 CHINA Rd, London", "SLOUGH SE12 2XY", "44, CHINA Rd Hong Kong", "33 TIMBER YARD, LONDON, L1 8XY", "44 CHINA ROAD, KOWLOON, HONG KONG"]

    database = init_database(["companies", "products", "locations", "serial numbers", "addresses"])

    print(30*"*", "COMPANIES", 30*"*")
    normalise_companies(company_list, database)

    print(30 * "*", "PRODUCTS", 30 * "*")
    normalise_products(product_list, database)

    print(30 * "*", "LOCATIONS", 30 * "*")
    normalise_locations(location_list, database)

    print(30 * "*", "SERIAL NUMBERS", 30 * "*")
    normalise_ids(ids, database)

    print(30 * "*", "ADDRESSES", 30 * "*")
    normalise_address(addresses, database)

    print(30 * "*", "DATABASE", 30 * "*")
    pprint.pprint(database)
