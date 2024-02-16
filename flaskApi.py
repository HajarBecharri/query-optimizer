from flask import Flask, request, jsonify
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

# Load the pre-trained model and vectorizer
loaded_model = joblib.load('linear_regression_model.joblib')
loaded_vectorizer = joblib.load('tfidf_vectorizer.joblib')

@app.route('/predict_execution_time', methods=['POST'])
def predict_execution_time():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract queries from the JSON data
        queries = data.get('queries', [])

        # Vectorize the queries using the loaded vectorizer
        queries_vectorized = loaded_vectorizer.transform(queries)

        # Predict execution times using the loaded model
        predictions = loaded_model.predict(queries_vectorized)

        # Find the index of the query with the minimum predicted execution time
        min_index = predictions.argmin()

        # Create a dictionary with the query and its minimum predicted execution time
        result = {"Query": queries[min_index], "MinPredictedExecutionTime": predictions[min_index]}
        
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(port=5000)
