# Personalized Movie Recommendation System

## Project Description

This project is a personalized movie recommendation system built using Python, Flask, and cloud services, and the Movie Recommender System dataset widely used by Machine Learning trainees. The datasets are given in the repo. 

The goal is to deploy a system that can accurately suggest movies according to user preferences leveraging various techniques such as Pearson Correlation, Cosine Similarity, Nearest Neighbors and Matrix Factorization.

This repository contains the backend API for the recommendation system, which will be deployed on a cloud platform.

The following notebook contains EDA and Recommendation System Analysis: https://github.com/varunjoshua/Movie-Recommender-System/blob/main/rec_system_models.ipynb 




## Features 

### Phase 1 - Current

* **Item-Based Recommendations:**
  * To start with, API will recommend movies based on a single movie chosen by the user. Later the system will recommend movies based on multiple user selections. 

* **Cosine Similarity:** The recommendations are powered by a pre-computed item-item cosine similarity matrix.

* **RESTful API:** A simple and clean Flask API provides an endpoint to request recommendations.


### Phase 2: 

* **User-Based Recommendation System:**
  * Implement a user-based recommendation system that leverages a pre-computed user-user similarity matrix and a completed user-movie ratings dataset from Matrix Factorization.


### Phase 3: 

* **Combined Recommendation System:**
  * Enhance the recommendation quality by combining the results of multiple models (e.g., Pearson, Cosine, and Nearest Neighbors).





## Prerequisites

To run this project locally, you will need:

* Python 3.x

* Pip (Python package installer)

You also need the following data files in your project directory:

* `ratings.csv`

* `movies.csv`

