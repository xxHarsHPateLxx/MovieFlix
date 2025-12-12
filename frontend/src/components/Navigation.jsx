import { Link } from 'react-router-dom';

const Navigation = () => {
  return (
    <nav className='navigation'>
      <div className='nav-container'>
        <Link to="/" className='nav-logo'>
          🎬 MovieFlix
        </Link>
        <div className='nav-links'>
          <span className='nav-link active'>
            Movie Recommendations
          </span>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
