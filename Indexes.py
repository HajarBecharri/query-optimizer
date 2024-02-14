from itertools import combinations
import re



def extract_first_word(query):
    return query.split()[0].upper()

def extract_table_name(query):
    match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        return None

def generate_index_combinations(columns, table_name):
    index_combinations = []

    for i in range(1, len(columns) + 1):
        for subset in combinations(columns, i):
            index_combination = f"INDEX({table_name} {', '.join(subset)})"
            index_combinations.append(index_combination)

    return index_combinations

def generate_query_with_indexes(original_query, index_combinations):
    first_word = extract_first_word(original_query)

    return [
        f"{first_word} /*+ {indexes} */ {original_query[len(first_word):].rstrip(';').lstrip()}"
        for indexes in index_combinations
    ]





