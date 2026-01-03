import os
import requests
import pickle
import pandas as pd
import ast
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()


# Get the directory where the script is located
BASE_DIR = Path(__file__).parent
MOVIES_PKL = BASE_DIR / 'movie_dict.pkl'
SIMILARITY_PKL = BASE_DIR / 'similarity.pkl'
ARCHIVE_DIR = BASE_DIR / 'archive'


def convert_genres_keywords(text):
    """Convert JSON string to list of names"""
    L = []
    try:
        for i in ast.literal_eval(text):
            L.append(i['name'])
    except:
        pass
    return L


def fetch_director(text):
    """Extract director from crew JSON"""
    L = []
    try:
        for i in ast.literal_eval(text):
            if i['job'] == 'Director':
                L.append(i['name'])
    except:
        pass
    return L


def collapse_spaces(L):
    """Remove spaces from list items"""
    return [i.replace(" ", "") for i in L]


def generate_pkl_files():
    """Generate pkl files from CSV data"""
    print("📊 Generating pickle files from CSV data...")
    
    try:
        # Read CSV files
        movies_df = pd.read_csv(ARCHIVE_DIR / 'tmdb_5000_movies.csv')
        credits_df = pd.read_csv(ARCHIVE_DIR / 'tmdb_5000_credits.csv')
        
        # Merge datasets
        movies_df = movies_df.merge(credits_df, on='title')
        
        # Select relevant columns
        movies_df = movies_df[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
        
        # Remove rows with missing values
        movies_df.dropna(inplace=True)
        
        # Convert JSON columns to lists
        movies_df['genres'] = movies_df['genres'].apply(convert_genres_keywords)
        movies_df['keywords'] = movies_df['keywords'].apply(convert_genres_keywords)
        movies_df['cast'] = movies_df['cast'].apply(convert_genres_keywords)
        movies_df['cast'] = movies_df['cast'].apply(lambda x: x[0:3])
        movies_df['crew'] = movies_df['crew'].apply(fetch_director)
        
        # Remove spaces from text
        movies_df['cast'] = movies_df['cast'].apply(collapse_spaces)
        movies_df['crew'] = movies_df['crew'].apply(collapse_spaces)
        movies_df['genres'] = movies_df['genres'].apply(collapse_spaces)
        movies_df['keywords'] = movies_df['keywords'].apply(collapse_spaces)
        
        # Split overview into words
        movies_df['overview'] = movies_df['overview'].apply(lambda x: x.split())
        
        # Create tags column
        movies_df['tags'] = (movies_df['overview'] + movies_df['genres'] + 
                             movies_df['keywords'] + movies_df['cast'] + movies_df['crew'])
        
        # Keep only necessary columns
        new = movies_df[['movie_id', 'title', 'tags']].copy()
        
        # Join tags into strings
        new.loc[:, 'tags'] = new['tags'].apply(lambda x: " ".join(x))
        
        # Create feature vectors
        cv = CountVectorizer(max_features=5000, stop_words='english')
        vector = cv.fit_transform(new['tags']).toarray()
        
        # Calculate similarity matrix
        similarity = cosine_similarity(vector)
        
        # Save to pickle files
        pickle.dump(new.to_dict('list'), open(MOVIES_PKL, 'wb'))
        pickle.dump(similarity, open(SIMILARITY_PKL, 'wb'))
        
        print(f"✅ Pickle files generated successfully! ({len(new)} movies)")
        return new, similarity
        
    except Exception as e:
        print(f"❌ Error generating pickle files: {e}")
        raise


def load_or_generate_data():
    """Load existing pkl files or generate them"""
    if MOVIES_PKL.exists() and SIMILARITY_PKL.exists():
        print("📁 Loading existing pickle files...")
        movies_dict = pickle.load(open(MOVIES_PKL, 'rb'))
        movies = pd.DataFrame(movies_dict)
        similarity = pickle.load(open(SIMILARITY_PKL, 'rb'))
        return movies, similarity
    else:
        print("⚠️ Pickle files not found. Generating from CSV...")
        movies, similarity = generate_pkl_files()
        return movies, similarity


# Initialize FastAPI app
app = FastAPI(title="Movie Recommendation API", version="1.0.0")

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load movie data and similarity matrix
movies, similarity = load_or_generate_data()

# Pydantic models
class RecommendationRequest(BaseModel):
    movie_title: str

class MovieRecommendation(BaseModel):
    title: str
    movie_id: int

class RecommendationResponse(BaseModel):
    selected_movie: str
    recommendations: List[MovieRecommendation]


def get_recommendations(movie_title: str) -> tuple:
    """Get movie recommendations based on similarity"""
    # Find movie index
    movie_matches = movies[movies['title'] == movie_title]
    
    if movie_matches.empty:
        raise ValueError(f"Movie '{movie_title}' not found in database")
    
    movie_index = movie_matches.index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        
        recommended_movies.append({
            "title": title,
            "movie_id": int(movie_id)
        })
    
    return recommended_movies


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Movie Recommendation API is running",
        "total_movies": len(movies),
        "version": "1.0.0"
    }


@app.get("/api/movies", response_model=List[str])
async def get_all_movies():
    """Get list of all available movie titles for autocomplete"""
    return movies['title'].tolist()


@app.post("/api/recommend", response_model=RecommendationResponse)
async def recommend_movies(request: RecommendationRequest):
    """Get movie recommendations based on the selected movie"""
    try:
        recommendations = get_recommendations(request.movie_title)
        
        return RecommendationResponse(
            selected_movie=request.movie_title,
            recommendations=recommendations
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error in recommendation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating recommendations")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
