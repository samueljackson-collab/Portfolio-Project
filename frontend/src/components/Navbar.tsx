import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear auth state and return the visitor to the marketing view.
    logout();
    navigate('/');
  };

  return (
    <header className="bg-white shadow">
      <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-semibold text-primary">
          Portfolio Dashboard
        </Link>
        <nav className="space-x-4">
          <Link to="/" className="text-sm font-medium hover:text-primary">
            Home
          </Link>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="text-sm font-medium hover:text-primary">
                Dashboard
              </Link>
              <button onClick={handleLogout} className="text-sm font-medium text-red-500">
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="text-sm font-medium text-primary">
              Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Navbar;
