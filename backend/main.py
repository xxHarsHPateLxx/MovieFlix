import os
import requests
import pickle
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

load_dotenv()

# Load TMDB API key from environment (.env)
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("⚠️ API_KEY not found in environment. Create a `.env` file with `API_KEY=your_api_key` to enable poster lookups.")

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
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

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
