from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches

app = Flask(__name__)
CORS(app)  

movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")

movies = movies.merge(credits, left_on='id', right_on='movie_id', how='inner').drop(columns=['movie_id'])


movies = movies[['id', 'original_title', 'genres', 'keywords', 'overview', 'cast', 'crew']]
movies.dropna(inplace=True)

def convert(text):
    try:
        data = ast.literal_eval(text)
        return [i['name'] for i in data] if isinstance(data, list) else []
    except (ValueError, SyntaxError):
        return []

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(lambda x: convert(x)[:3])

def fetch_director(text):
    try:
        data = ast.literal_eval(text)
        return [i['name'] for i in data if isinstance(i, dict) and i.get('job') == 'Director']
    except (ValueError, SyntaxError):
        return []

movies['crew'] = movies['crew'].apply(fetch_director)

movies['tags'] = movies['overview'].fillna('') + movies['genres'].apply(lambda x: ' '.join(x)) + \
                 movies['keywords'].apply(lambda x: ' '.join(x)) + \
                 movies['cast'].apply(lambda x: ' '.join(x)) + \
                 movies['crew'].apply(lambda x: ' '.join(x))

new = movies[['id', 'original_title', 'tags']].copy()
new['original_title'] = new['original_title'].str.lower()

# Text vectorization
cv = CountVectorizer(max_features=3000, stop_words='english')
vector = cv.fit_transform(new['tags']).toarray()
similarity = cosine_similarity(vector)

@app.route('/recommend', methods=['GET'])
def recommend():
    movie = request.args.get('movie', '').lower()

    closest_match = get_close_matches(movie, new['original_title'].tolist(), n=1, cutoff=0.6)
    
    if not closest_match:
        return jsonify({"error": "Movie not found. Try another movie!"})

    matched_movie = closest_match[0]  
    index = new[new['original_title'] == matched_movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommendations = [new.iloc[i[0]].original_title.title() for i in distances[1:6]]

    return jsonify({"recommendations": recommendations, "matched_movie": matched_movie.title()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

