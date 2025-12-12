# Movie Recommendation System

A full-stack movie recommendation application that uses machine learning to suggest similar movies based on user selection.

## 📖 Overview
This project consists of a backend built with FastAPI that serves movie recommendations based on content similarity using a pre-trained model. The frontend is developed using React and Vite, providing a user-friendly interface for searching movies and viewing recommendations along with their posters fetched from the TMDB API.

## 🚀 Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your TMDB API key (if not already present):
   ```
   API_KEY=your_tmdb_api_key_here
   ```

5. Start the backend server:
   ```bash
   uvicorn app:app --reload
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file with your TMDB API key:
   ```
   VITE_TMDB_API_KEY=your_tmdb_api_bearer_token_here
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

## 🎯 Features

- **Movie Search**: Autocomplete search for movies from the TMDB dataset
- **ML-Powered Recommendations**: Get 5 similar movie recommendations based on content similarity
- **Movie Posters**: Dynamic poster fetching from TMDB API
- **Popular Movies**: Browse popular movies from TMDB
- **Responsive Design**: Modern UI that works on all devices

## 🛠️ Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **Pandas**: Data manipulation
- **Scikit-learn**: Machine learning (cosine similarity)
- **Pickle**: Model serialization
- **TMDB API**: Movie metadata and posters

### Frontend
- **React**: UI library
- **Vite**: Build tool and dev server
- **React Router**: Navigation
- **CSS**: Styling

## 📝 API Endpoints

- `GET /` - Health check
- `GET /api/movies` - Get list of all movie titles
- `POST /api/recommend` - Get recommendations for a movie
  ```json
  {
    "movie_title": "The Amazing Spider-Man"
  }
  ```

## 🔑 Environment Variables

### Backend (.env)
- `API_KEY`: TMDB API key (optional, used for poster fetching on backend if needed)

### Frontend (.env.local)
- `VITE_TMDB_API_KEY`: TMDB API bearer token for fetching movie posters

## 📦 Dependencies

See `backend/requirements.txt` and `frontend/package.json` for complete dependency lists.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for any improvements.

## 📄 License

This project is open source and available under the MIT License.
