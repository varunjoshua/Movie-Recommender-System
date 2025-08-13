# ----- * Import necessary libraries *  -----

# Import necessary libraries
from flask import Flask, request, jsonify, render_template

# Import data and functions from the recommender module
from recommender_models import get_recommendations_from_id, movies_df

# For making external API calls
import requests

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


# --- Revised API Endpoint for Search and Autocomplete ---

@app.route('/search_movies', methods=['GET'])
def search_movies_endpoint():
    """
    This is the API for our autocomplete feature.
    It first searches our local database and then fetches
    poster images from the TMDb API for the matching movies.
    """
    # Get the search query from the URL parameters
    query = request.args.get('query', '')
    
    # If there's no query, return an empty list
    if not query:
        return jsonify({"status": "success", "movies": []})

    # 1. Search our local DataFrame for movies with matching titles
    matching_movies = movies_df[movies_df['Title'].str.lower().str.contains(query.lower())]
    matching_movies = matching_movies.head(10) # Limit to 10 results
    
    movies_with_details = []
    
    # 2. For each matching movie, fetch the poster from TMDb
    for index, movie in matching_movies.iterrows():
        tmdb_movie = search_tmdb_for_poster(movie['Title'])
        
        # Construct the response object
        movie_details = {
            'MovieID': movie['MovieID'],
            'Title': movie['Title'],
            # If a TMDb match is found, include the poster path
            'PosterPath': tmdb_movie['poster_path'] if tmdb_movie else None
        }
        movies_with_details.append(movie_details)
        
    return jsonify({"status": "success", "movies": movies_with_details})


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

def search_tmdb_for_poster(query):
    """
    Searches for a movie on TMDb and returns the first result.
    This is used to get the poster path for a movie from our local database.

    Args:
        query (str): The movie title to search for.

    Returns:
        dict: The first movie dictionary matching the query, or None.
    """
    api_key = '619800e856d7bff5b95923808928a998'
    base_url = 'https://api.themoviedb.org/3/search/movie'

    params = {
        'api_key': api_key,
        'query': query
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Return the first result, which is usually the most relevant
        if data.get('results'):
            return data['results'][0]
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during TMDb search for '{query}': {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during TMDb search: {e}")
        return None



#------- Function to get movie details by ID -------

def get_movie_details(movie_id):
    """
    Gets detailed information for a single movie from TMDb by its ID.

    Args:
        movie_id (str): The ID of the movie to fetch details for.

    Returns:
        dict: A dictionary of movie details, or None if the request fails.
    """
    api_key = '619800e856d7bff5b95923808928a998'
    base_url = f'https://api.themoviedb.org/3/movie/{movie_id}'

    params = {
        'api_key': api_key
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie details for ID {movie_id}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching details for ID {movie_id}: {e}")
        return None



# To run the application, use `flask run` in your terminal
# if __name__ == '__main__':
app.run(debug=True)