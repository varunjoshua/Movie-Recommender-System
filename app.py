# app.py

# Import necessary libraries
from flask import Flask, request, jsonify

# Import data and functions from the recommender module
from recommender_models import get_recommendations_from_id, movies_df

# Initialize the Flask app
app = Flask(__name__)

# --- API Endpoint ---
@app.route('/recommendations', methods=['GET'])
def recommend():
    """
    API endpoint for movie recommendations.
    Expects 'movie_id' and 'n_recs' as query parameters.
    Returns a JSON list of recommended movies, each with its ID and title.
    """
    try:
        # Get query parameters from the request
        movie_id = request.args.get('movie_id')
        if not movie_id:
            return jsonify({
                "status": "error",
                "message": "Missing 'movie_id' query parameter."
            }), 400

        # Convert the movie_id to an integer
        movie_id = int(movie_id)
        n_recs = int(request.args.get('n_recs', 10))  # Default to 10 recommendations

        # Use the recommendation function from our module
        recommended_ids = get_recommendations_from_id(movie_id, n_recs)

        # Get the corresponding movie titles and IDs from the DataFrame
        recommended_movies_details = movies_df[movies_df['MovieID'].isin(recommended_ids)][['MovieID', 'Title']].to_dict('records')
        
        # Create a response in JSON format
        return jsonify({
            "status": "success",
            "movie_id": movie_id,
            "recommended_movies": recommended_movies_details
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

# To run the application, use `flask run` in your terminal
# if __name__ == '__main__':
    app.run(debug=True)
