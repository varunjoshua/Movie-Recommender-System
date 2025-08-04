# recommender_models.py

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# --- Data Loading and Preprocessing ---
def load_and_preprocess_data():
    """
    Loads pre-processed ratings and movie data.
    Assumes 'movies.csv' contains a 'clean_title' column with titles
    that include the year for uniqueness (e.g., 'Sabrina (1954)').
    """
    try:
        # Load the datasets
        ratings_df = pd.read_csv('ratings.csv')
        movies_df = pd.read_csv('movies.csv') # Pre-cleaned file with clean Titles

        # Create a pivot table for the user-movie ratings
        user_movie_ratings = ratings_df.pivot_table(
            index='userId',
            columns='movieId',
            values='rating'
        ).fillna(0)

        # Get the item-item cosine similarity matrix
        item_similarity_matrix = cosine_similarity(user_movie_ratings.T)
        item_similarity_df = pd.DataFrame(
            item_similarity_matrix,
            index=user_movie_ratings.columns,
            columns=user_movie_ratings.columns
        )

        return movies_df, item_similarity_df

    except FileNotFoundError as e:
        print(f"Error: Required data file not found. Make sure 'ratings.csv' and 'movies_cleaned.csv' are in the same directory. {e}")
        return None, None

# Load data once when the module is imported
movies_df, item_similarity_df = load_and_preprocess_data()

# --- Recommendation Functions ---
def get_recommendations_from_id(movie_id, n_recs):
    """
    Recommends movies based on item-item cosine similarity using a pre-computed matrix.
    
    Args:
        movie_id (int): The ID of the movie to find similar movies for.
        n_recs (int): The number of recommendations to return.
        
    Returns:
        list: A list of recommended movie IDs.
    """
    # Check if data was loaded successfully
    if item_similarity_df is None:
        return []

    # Get the similarity scores for the given movie ID
    similar_scores = item_similarity_df[movie_id].sort_values(ascending=False)
    
    # Filter out the movie itself and get the top N recommendations
    recommended_movies_ids = similar_scores.index.tolist()[1:n_recs + 1]
    
    return recommended_movies_ids

def find_movie_id(movie_name):
    """
    Finds a movie ID by its Title.
    
    Args:
        movie_name (str): The name of the movie.
        
    Returns:
        int or None: The movie ID if found, otherwise None.
    """
    # Check if data was loaded successfully
    if movies_df is None:
        return None

    # Use the cleaned titles for lookup
    movie = movies_df[movies_df["Title"] == movie_name]
    
    if not movie.empty:
        return int(movie.iloc[0]["MovieID"])
        
    return None

