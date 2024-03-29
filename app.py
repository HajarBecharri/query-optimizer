from flask import jsonify,Flask,render_template,request
from flask_cors import CORS,cross_origin
from flask_mysqldb import MySQL
import json
import mysql.connector
from datetime import datetime,timedelta
import oracledb
from IndexesDep import IndexQueryOptimizer, extract_values_from_index_statements
from Indexes import generate_query_with_indexes, generate_index_combinations,extract_table_name,extract_first_word
from INClauseDep import extract_and_filter, extract_columns2, separate_column_values, extract_table_names
from INclause import  extract_columns, optimize_query_with_in
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

CORS(app)
oracle_connection_string = 'SH/hajar@better-sql.francecentral.cloudapp.azure.com/FREE'
connection = oracledb.connect(oracle_connection_string)
app.config["DEBUG"]=True
# Load the pre-trained model and vectorizer
loaded_model = joblib.load('linear_regression_model.joblib')
loaded_vectorizer = joblib.load('tfidf_vectorizer.joblib')




# Route de test pour vérifier la connexion à la base de données
@app.route('/connect_test')
def test_db_connection():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COLUMN_NAME FROM USER_TAB_COLUMNS WHERE TABLE_NAME = 'CHANNELS'")

        # Fetch the results
        rows = cursor.fetchall()

        # Convert rows to a list of dictionaries
        results = []
        for row in rows:
            result_dict = {}
            for column in cursor.description:
                result_dict[column[0]] = row[cursor.description.index(column)]
            results.append(result_dict)

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Return the results as JSON
        return jsonify({'data': results})

        
    except Exception as e:
        return jsonify({"error:":str(e)}),500
@app.route('/execute_query', methods=['POST'])
def execute_query():
    try:
        query=request.json['query']
        #get the list of queries optimizes by Index optimizer
        # Suggested Indexes
        index_optimizer = IndexQueryOptimizer(query)
        
        
        suggested_indexes = index_optimizer.optimize_query()
        
        suggested_indexes = extract_values_from_index_statements(suggested_indexes)
        
        

        # Table Name
        table_name = extract_table_name(query)
        
        

        if table_name:
        # Generate index combinations
         index_combinations = generate_index_combinations(suggested_indexes, table_name)
         

        # Generate new queries with indexes
         indexes_queries = generate_query_with_indexes(query, index_combinations)
         

         
        else:
         print("Table name not found in the query.")

        #get the list of queries optimizes by Clause optimizer
        
        expressions = extract_and_filter(query)
        

        # Specify the optimization parameters
       
        column_values_to_optimize = separate_column_values(expressions)
        

        columns = extract_columns(query)
        
        # Convert QueryConditions to SQL query
        table_name = extract_table_names(query)
        optimized_query = optimize_query_with_in(query, column_values_to_optimize, table_name, columns)
        optimized_query1 = optimized_query.split(' ; ')
        
        clause_queries = [query.rstrip(';') for query in optimized_query1]
    
        # Combine the arrays into a new array
        combined_queries = clause_queries + indexes_queries + [query]
        
        
        # Vectorize the queries using the loaded vectorizer
        queries_vectorized = loaded_vectorizer.transform(combined_queries)
        
        # Predict execution times using the loaded model
        predictions = loaded_model.predict(queries_vectorized)
        

        # Find the index of the query with the minimum predicted execution time
        min_index = predictions.argmin()
        queryOptimized=combined_queries[min_index]
        
        MinPredictedExecutionTime=predictions[min_index]
        
        cursor = connection.cursor()
        cursor.execute(queryOptimized)

        results = cursor.fetchall()
        
        # Get the execution plan
        cursor = connection.cursor()
        cursor.execute("EXPLAIN PLAN FOR " + queryOptimized)
        cursor.execute("SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY)")
        plan = cursor.fetchall()
        transformed_plan = transform_execution_plan(plan)
       

        # Close cursor and connection
        cursor.close()
        connection.close()

        return jsonify({'results': results,'executionPlan':transformed_plan,'queryOptimized':queryOptimized,'excutionTime':MinPredictedExecutionTime})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
def transform_execution_plan(plan):
    formatted_execution_plan = []
    
    # Check if the plan has at least 6 rows
    if len(plan) < 6:
        print("Error: Execution plan has insufficient rows.")
        return formatted_execution_plan
    
    for row in plan[5:]:
        if '-' in row[0]:
            # If the row contains only dashes, skip it
            continue
        else:
            row_values = [value.strip() for value in row[0].split("|")]
            
            # Check if row_values has enough elements
            if len(row_values) < 8:
                print("Error: Insufficient values in row.")
                continue
            
            formatted_execution_plan.append({
                'Id': row_values[1],
                'Operation': row_values[2],
                'Name': row_values[3],
                'Rows': row_values[4],
                'Bytes': row_values[5],
                'Cost': row_values[6],
                'Time': row_values[7]
            })
    return formatted_execution_plan

@app.route('/get_columns', methods=['GET'])
def get_columns():
    try:
        # Connect to Oracle database
        cursor = connection.cursor()

        # Execute the query to retrieve column names
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM USER_TAB_COLUMNS
            WHERE TABLE_NAME = 'channels'
        """)
        
        # Fetch all column names
        columns = [row[0] for row in cursor.fetchall()]

        # Close cursor and connection
        cursor.close()
        connection.close()

        return jsonify({'columns': columns})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


app.run()

