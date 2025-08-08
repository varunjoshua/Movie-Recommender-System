# ----- * Import necessary libraries *  -----

# Import necessary libraries
from flask import Flask, request, jsonify, render_template

# Import data and functions from the recommender module
from recommender_models import get_recommendations_from_id, movies_df


# ----- * Flask Application Setup * -----


# --- * Initialize the Flask app *  ---
app = Flask(__name__)


# --- * Route to serve the HTML file * ---
@app.route('/')
def home():
    """
    This route serves the main HTML page to the user.
    Flask automatically looks for this file in a 'templates' folder.
    """
    return render_template('index.html')


# --- API Endpoint for Search and Autocomplete ---

@app.route('/search_movies', methods=['GET'])
def search_movies():
    """
    This is the new API for our autocomplete feature.
    It takes a 'query' parameter and returns a list of matching movies from our dataset.
    """
    # Get the search query from the URL parameters
    query = request.args.get('query', '').lower()
    
    # If there's no query, return an empty list
    if not query:
        return jsonify({"status": "success", "movies": []})

    # Search for movies where the title contains the query string
    # We'll use a case-insensitive search for a better user experience
    matching_movies = movies_df[movies_df['Title'].str.lower().str.contains(query)]

    # We only want to return a maximum of 10 suggestions to keep the list clean
    matching_movies = matching_movies.head(10)
    
    # Convert the matching movies DataFrame to a list of dictionaries
    movies_list = matching_movies[['MovieID', 'Title']].to_dict('records')
    
    # Return the results as JSON
    return jsonify({"status": "success", "movies": movies_list})



# --- Recommendation Endpoint ---
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
    
@app.route('/credits')
def credits():
    return render_template('credits.html')

# To run the application, use `flask run` in your terminal
# if __name__ == '__main__':
    app.run(debug=True)
