try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")


def init_kb(categories):
    kb = {}
    for category in categories:
        kb[category] = {}
    return kb

def wikify(query, N_candidates=3):
    # Get the first 20 results
    init = 0
    N_results = 20

    # If no wikipedia articles found
    wikis = []
    while len(wikis) < N_candidates:
        results = search(query, tld="com", num=25, start=init, stop=init + N_results, pause=2)
        for direction in results:
            if "wikipedia" in direction:
                wikis.append(direction)
        init += N_results
    return wikis


def company_normalise(company_name, kb):
    candidates = wikify(company_name)
    kb["companies"][candidates[0]] = []


def product_normalise(product, kb):
    candidates = wikify(company_name)
    kb = {wikis[0]: query}


def location_normalise(location, kb):
    candidates = wikify(company_name)
    kb = {wikis[0]: query}


if __name__ = "__main__":
    kb = init_kb(["companies", "products"])
