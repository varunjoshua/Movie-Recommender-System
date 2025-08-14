# app.py

# ----- * Import necessary libraries * -----
from flask import Flask, request, jsonify, render_template
import requests
import pandas as pd
from recommender_models import get_recommendations_from_id, movies_df, find_movie_id

# TMDb API key (This is a sample key and may not work)
TMDB_API_KEY = '619800e856d7bff5b95923808928a998'

# ----- * Flask Application Setup * -----
app = Flask(__name__)


# --- * Route to serve the HTML file * ---
@app.route('/')
def home():
    """
    This route serves the main HTML page to the user.
    """
    return render_template('index.html')


# ------------ TMDb API Integration Functions ------------

def get_tmdb_details_by_tmdb_id(tmdb_id):
    """
    Gets detailed information for a single movie from TMDb by its *TMDb* ID.
    This is the core function for fetching full movie details.
    
    Args:
        tmdb_id (str): The unique ID of the movie on TMDb.

    Returns:
        dict: A dictionary of movie details, or None if the request fails.
    """
    base_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}'
    params = {'api_key': TMDB_API_KEY}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie details for TMDb ID {tmdb_id}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching details for TMDb ID {tmdb_id}: {e}")
        return None


def search_tmdb_by_title(query):
    """
    Searches for a movie on TMDb and returns the full result with an exact title match.
    This is used to get the TMDb ID and poster path for a movie from our local database.
    
    Args:
        query (str): The movie title to search for.
        
    Returns:
        dict: The TMDb movie object, or None if not found.
    """
    base_url = 'https://api.themoviedb.org/3/search/movie'
    params = {'api_key': TMDB_API_KEY, 'query': query}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Iterate through results to find an exact title match
        for result in data.get('results', []):
            if result.get('title', '').lower() == query.lower():
                return result
        
        # If no exact match, return the first result if available
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


# --- API Endpoint for Search and Autocomplete ---
@app.route('/search_movies', methods=['GET'])
def search_movies_endpoint():
    """
    API for our autocomplete feature.
    It searches our local database and fetches poster images from TMDb.
    """
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({"status": "success", "movies": []})

    matching_movies = movies_df[movies_df['Title'].str.lower().str.contains(query.lower())].copy()
    
    matching_movies['relevance_score'] = 0
    matching_movies.loc[matching_movies['Title'].str.lower() == query.lower(), 'relevance_score'] = 2
    matching_movies.loc[matching_movies['Title'].str.lower().str.startswith(query.lower()), 'relevance_score'] = 1
    
    matching_movies = matching_movies.sort_values(
        by=['relevance_score', 'Title'],
        ascending=[False, True]
    ).head(10)
    
    movies_with_details = []
    
    for index, movie in matching_movies.iterrows():
        tmdb_movie_details = search_tmdb_by_title(movie['Title'])
        poster_path = tmdb_movie_details.get('poster_path') if tmdb_movie_details else None
        
        movies_with_details.append({
            "MovieID": str(movie['MovieID']),
            "Title": movie['Title'],
            "PosterPath": poster_path,
        })

    return jsonify({"status": "success", "movies": movies_with_details})


# --- Recommendation Endpoint ---
@app.route('/recommendations', methods=['GET'])
def recommend():
    """
    API endpoint for movie recommendations.
    Returns a JSON list of recommended movies with full details.
    This function now correctly fetches details using the TMDb ID.
    """
    try:
        movie_id = request.args.get('movie_id')
        if not movie_id:
            return jsonify({
                "status": "error",
                "message": "Missing 'movie_id' query parameter."
            }), 400

        movie_id = int(movie_id)
        n_recs = int(request.args.get('n_recs', 10))

        recommended_ids = get_recommendations_from_id(movie_id, n_recs)
        
        recommended_movies_details = []
        for rec_id in recommended_ids:
            # 1. Find the title from our local DataFrame using the local ID
            movie_title = movies_df[movies_df['MovieID'] == rec_id]['Title'].iloc[0]
            
            # 2. Search TMDb by title to get the TMDb ID and other basic info
            tmdb_basic_details = search_tmdb_by_title(movie_title)
            
            if tmdb_basic_details and tmdb_basic_details.get('id'):
                # 3. Use the correct TMDb ID to fetch the full details
                tmdb_details = get_tmdb_details_by_tmdb_id(tmdb_basic_details.get('id'))
                
                if tmdb_details:
                    recommended_movies_details.append({
                        "MovieID": str(rec_id),
                        "Title": tmdb_details.get('title'),
                        "PosterPath": tmdb_details.get('poster_path'),
                        "Overview": tmdb_details.get('overview'),
                        "VoteAverage": tmdb_details.get('vote_average')
                    })
        
        return jsonify({
            "status": "success",
            "movie_id": movie_id,
            "recommended_movies": recommended_movies_details
        })
    except Exception as e:
        print(f"Error in recommendations endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal error occurred."
        }), 500


# --- New Endpoint for a single movie's details ---
@app.route('/get_movie_details', methods=['GET'])
def get_movie_details_endpoint():
    """
    Endpoint to get detailed information for a single movie by its local MovieID.
    This function now correctly fetches details using the TMDb ID.
    """
    local_movie_id = request.args.get('movie_id')
    if not local_movie_id:
        return jsonify({"status": "error", "message": "Missing movie_id parameter"}), 400

    try:
        local_movie_id = int(local_movie_id)
        
        # 1. Find the title from our local DataFrame
        movie_title = movies_df[movies_df['MovieID'] == local_movie_id]['Title'].iloc[0]
        
        # 2. Search TMDb by title to get the TMDb ID
        tmdb_basic_details = search_tmdb_by_title(movie_title)
        
        if tmdb_basic_details and tmdb_basic_details.get('id'):
            tmdb_id = tmdb_basic_details.get('id')
            # 3. Use the correct TMDb ID to fetch the full details
            details = get_tmdb_details_by_tmdb_id(tmdb_id)
            
            if details:
                return jsonify({"status": "success", "details": details})
            else:
                return jsonify({"status": "error", "message": "Movie details not found"}), 404
        else:
            return jsonify({"status": "error", "message": "TMDb ID not found for movie title"}), 404

    except Exception as e:
        print(f"Error in get_movie_details endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


# --- Route for credits page ---
@app.route('/credits')
def credits():
    return render_template('credits.html')


if __name__ == '__main__':
    app.run(debug=True)
