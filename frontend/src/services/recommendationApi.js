const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetch all available movie titles from the backend
 * @returns {Promise<string[]>} Array of movie titles
 */
export const fetchAllMovies = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/movies`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const movies = await response.json();
    return movies;
  } catch (error) {
    console.error('Error fetching movies:', error);
    throw new Error('Failed to fetch movie list. Make sure the backend server is running.');
  }
};

/**
 * Get movie recommendations for a given movie title
 * @param {string} movieTitle - The title of the movie to get recommendations for
 * @returns {Promise<Object>} Recommendation response with selected movie and recommendations
 */
export const getRecommendations = async (movieTitle) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        movie_title: movieTitle,
      }),
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Movie not found in our database');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};

/**
 * Check if the backend API is healthy
 * @returns {Promise<Object>} API health status
 */
export const checkApiHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/`);
    
    if (!response.ok) {
      throw new Error('API is not responding');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API health check failed:', error);
    throw new Error('Backend API is not available. Please start the server.');
  }
};
