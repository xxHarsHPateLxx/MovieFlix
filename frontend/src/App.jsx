import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation.jsx';
import RecommendationsPage from './pages/RecommendationsPage.jsx';

const App = () => {
  return (
    <Router>
      <main>
        <div className='pattern'/>
        <div className='wrapper'>
          <Navigation />
          <Routes>
            <Route path="/" element={<RecommendationsPage />} />
          </Routes>
        </div>
      </main>
    </Router>
  );
}

export default App;
