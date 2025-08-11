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


# ------------ TMDb API Integration ------------

# Import necessary libraries for TMDb API

def search_movies(query):
    """
    Searches for movies on TMDb by title.

    Args:
        query (str): The movie title to search for.

    Returns:
        list: A list of movie dictionaries matching the query,
              or an empty list if the request fails.
    """
    # Replace 'YOUR_API_KEY' with your actual TMDb API key
    api_key = '619800e856d7bff5b95923808928a998'
    base_url = 'https://api.themoviedb.org/3/search/movie'

    # Set up the parameters for the GET request
    params = {
        'api_key': api_key,
        'query': query
    }

    try:
        # Make the API call
        response = requests.get(base_url, params=params)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # The API returns a 'results' key which is a list of movies
        return data.get('results', [])

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

#--- Search API Test - delete after---

search_term = "The Matrix"
search_results = search_movies(search_term)

if search_results:
     print(f"Found {len(search_results)} results for '{search_term}':")
     for movie in search_results:
         # The 'id' and 'title' are the most important fields here
         movie_id = movie.get('id')
         title = movie.get('title')
         release_date = movie.get('release_date', 'N/A')
         print(f"  ID: {movie_id}, Title: '{title}', Release Date: {release_date}")
else:
     print(f"No results found for '{search_term}'.")




# To run the application, use `flask run` in your terminal
# if __name__ == '__main__':
    app.run(debug=True)
