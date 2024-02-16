import re


class QueryConditions:
    def __init__(self, column_values, other_conditions=None):
        self.column_values = column_values
        self.other_conditions = other_conditions or []

    def to_sql_query(self, table_name):
        conditions = []

        for column, values in self.column_values.items():
            conditions.append(f"{table_name}.{column} IN ({', '.join(map(repr, values))})")

        conditions_str = " AND ".join(conditions)
        conditions_str = f"({conditions_str}) AND {' AND '.join(self.other_conditions)}" if self.other_conditions else conditions_str

        return f"SELECT * FROM {table_name} WHERE {conditions_str}"
    
    def to_delete_sql_query(self, table_name):
        conditions = []

        for column, values in self.column_values.items():
            conditions.append(f"{table_name}.{column} IN ({', '.join(map(repr, values))})")

        conditions_str = " AND ".join(conditions)
        conditions_str = f"({conditions_str}) AND {' AND '.join(self.other_conditions)}" if self.other_conditions else conditions_str

        return f"DELETE * FROM {table_name} WHERE {conditions_str}"

def extract_columns(query):
    # Use regular expression to find columns part after SELECT/DELETE keyword
    match = re.search(r'(SELECT|DELETE)\s+(?P<columns>.*?)\s+FROM', query, re.IGNORECASE)
    
    if match:
        columns_str = match.group('columns')
        # Split columns string by commas and remove leading/trailing whitespaces
        columns = [col.strip() for col in columns_str.split(',')]
        return columns
    else:
        return None


def optimize_query_with_in(original_query, column_values, table_name, columns):
    query_type = original_query.split()[0].upper()

    if query_type == 'SELECT':
        # Extract the JOIN, conditions, and ORDER BY clause from the original query
        join_index = original_query.find("JOIN")
        where_index = original_query.find("WHERE")
        order_by_index = original_query.find("ORDER BY")

        join_clause = original_query[join_index:where_index].strip() if join_index != -1 else ""
        conditions = original_query[where_index+5:order_by_index].strip() if where_index != -1 else ""
        order_by_clause = original_query[order_by_index:].strip() if order_by_index != -1 else ""

    elif query_type == 'DELETE':
        # Extract the conditions from the original DELETE query
        where_index = original_query.find("WHERE")
        conditions = original_query[where_index+5:].strip() if where_index != -1 else ""

    # Create a set to store unique conditions
    unique_conditions = set()

    # Process existing conditions and add them to the set
    for condition in conditions.split("AND"):
        condition = condition.strip()
        if not any(col in condition for col in column_values):
            unique_conditions.add(condition)

    # Create an optimized query using the IN clause for each specified column
    for column, values in column_values.items():
        in_clause = f"{table_name}.{column} IN ({', '.join(map(repr, values))})"
        unique_conditions.add(in_clause)

    # Combine conditions into a string
    optimized_conditions_str = " AND ".join(unique_conditions)

    # Combine optimized query with JOIN, conditions, and ORDER BY (for SELECT) or WHERE (for DELETE)
    if query_type == 'SELECT':
        if columns:
            column_str = ', '.join(columns)
            optimized_query = f"SELECT {column_str} FROM {table_name} {join_clause} WHERE {optimized_conditions_str} {order_by_clause}"
        else:
            optimized_query = f"SELECT * FROM {table_name} {join_clause} WHERE {optimized_conditions_str} {order_by_clause}"
    elif query_type == 'DELETE':
        if columns:
            column_str = ', '.join(columns)
            optimized_query = f"DELETE {column_str} FROM {table_name} WHERE {optimized_conditions_str}"
        else:
            optimized_query = f"DELETE * FROM {table_name} WHERE {optimized_conditions_str}"

    return optimized_query





