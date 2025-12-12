import { useState, useEffect } from 'react';
import { fetchAllMovies, getRecommendations } from '../services/recommendationApi';
import Spinner from '../components/Spinner';
import MovieCard from '../components/MovieCard';

const API_BASE_URL = 'https://api.themoviedb.org/3';
const API_KEY = import.meta.env.VITE_TMDB_API_KEY;

const API_OPTIONS = {
  method: 'GET',
  headers: {
    accept: 'application/json',
    Authorization: `Bearer ${API_KEY}`
  }
};

const RecommendationsPage = () => {
  const [movies, setMovies] = useState([]);
  const [filteredMovies, setFilteredMovies] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMovie, setSelectedMovie] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [loadingMovies, setLoadingMovies] = useState(true);
  const [allMovies, setAllMovies] = useState([]);
  const [loadingAllMovies, setLoadingAllMovies] = useState(false);

  // Helper function to fetch poster from TMDB
  const fetchPoster = async (movieId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/movie/${movieId}?api_key=${API_KEY}`,
        API_OPTIONS
      );
      const data = await response.json();
      return data.poster_path 
        ? `https://image.tmdb.org/t/p/w500${data.poster_path}`
        : '/No-Poster.png';
    } catch (error) {
      console.error('Error fetching poster:', error);
      return '/No-Poster.png';
    }
  };

  // Fetch all movies on component mount
  useEffect(() => {
    const loadMovies = async () => {
      try {
        const movieList = await fetchAllMovies();
        setMovies(movieList);
        setLoadingMovies(false);
      } catch (err) {
        setError(err.message);
        setLoadingMovies(false);
      }
    };
    
    loadMovies();
  }, []);

  // Fetch popular movies for "All Movies" section
  useEffect(() => {
    const fetchPopularMovies = async () => {
      setLoadingAllMovies(true);
      try {
        const endpoint = `${API_BASE_URL}/discover/movie?sort_by=popularity.desc`;
        const response = await fetch(endpoint, API_OPTIONS);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setAllMovies(data.results || []);
      } catch (error) {
        console.error('Error fetching popular movies:', error);
      } finally {
        setLoadingAllMovies(false);
      }
    };
    
    fetchPopularMovies();
  }, []);

  // Filter movies based on search term
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredMovies([]);
      setShowDropdown(false);
    } else {
      const filtered = movies
        .filter(movie => 
          movie.toLowerCase().includes(searchTerm.toLowerCase())
        )
        .slice(0, 10);
      setFilteredMovies(filtered);
      setShowDropdown(true);
    }
  }, [searchTerm, movies]);

  const handleMovieSelect = (movie) => {
    setSelectedMovie(movie);
    setSearchTerm(movie);
    setShowDropdown(false);
    setFilteredMovies([]);
    setRecommendations([]);
    setError('');
  };

  const handleGetRecommendations = async () => {
    if (!selectedMovie) {
      setError('Please select a movie first');
      return;
    }

    setLoading(true);
    setError('');
    setRecommendations([]);

    try {
      const data = await getRecommendations(selectedMovie);
      
      // Fetch posters for all recommended movies
      const recommendationsWithPosters = await Promise.all(
        data.recommendations.map(async (movie) => {
          const poster_url = await fetchPoster(movie.movie_id);
          return { ...movie, poster_url };
        })
      );
      
      setRecommendations(recommendationsWithPosters);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <header>
        <img src="./hero-img.png" alt="Hero Banner" />
        <h1>Find <span className='text-gradient'>Movies</span> You'll Enjoy Without the Hassle</h1>
      
        <div className='search'>
          <div className="autocomplete-wrapper">
            <img src="search.svg" alt="search" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onFocus={() => searchTerm && setShowDropdown(true)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              placeholder="Search for a movie to get recommendations..."
              disabled={loadingMovies}
            />
            
            {showDropdown && filteredMovies.length > 0 && (
              <ul className="autocomplete-dropdown">
                {filteredMovies.map((movie, index) => (
                  <li
                    key={index}
                    onClick={() => handleMovieSelect(movie)}
                    className="autocomplete-item"
                  >
                    {movie}
                  </li>
                ))}
              </ul>
            )}

            {showDropdown && searchTerm && filteredMovies.length === 0 && (
              <div className="no-results">No movies found</div>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
          <button
            onClick={handleGetRecommendations}
            disabled={!selectedMovie || loading || loadingMovies}
            className="recommend-button"
          >
            {loading ? 'Getting Recommendations...' : 'Get Recommendations'}
          </button>
        </div>

        {error && (
          <div className="error-message" style={{ textAlign: 'center', marginTop: '15px', color: '#ff6b6b' }}>
            ⚠️ {error}
          </div>
        )}
      </header>

      {recommendations.length > 0 && (
        <section className='trending'>
          <h2>Recommended for You (Based on "{selectedMovie}")</h2>
          <ul>
            {recommendations.map((movie, index) => (
              <li key={movie.movie_id || index}>
                <p>{index + 1}</p>
                <img src={movie.poster_url || '/No-Poster.png'} alt={movie.title} />
              </li>
            ))}                  
          </ul>
        </section>
      )}

      {loading && (
        <div className="spinner-container" style={{ padding: '40px 0' }}>
          <Spinner />
        </div>
      )}

      <section className='all-movies'>
        <h2>All Movies</h2>

        {loadingAllMovies ? (
          <Spinner />
        ) : (
          <ul>
            {allMovies.map(movie => (
              <MovieCard key={movie.id} movie={movie} />
            ))}
          </ul>
        )}
      </section>
    </>
  );
};

export default RecommendationsPage;
