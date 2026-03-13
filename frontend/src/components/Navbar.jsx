import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  return (
    <nav>
      <div className="nav-logo">
        <Link to={!token ? '/' : role === 'CANDIDATE' ? '/student-dashboard' : '/recruiter-dashboard'}>
          <img src="/C__2_-removebg-preview.png" alt="JobMatch" />
        </Link>
      </div>

      <div className="nav-links">
        {!token ? (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        ) : role === 'CANDIDATE' ? (
          <>
            <Link to="/browse-jobs">Browse Jobs</Link>
            <Link to="/profile">Profile</Link>
          </>
        ) : (
          <>
            <Link to="/recruiter-dashboard">My Jobs</Link>
            <Link to="/profile">Profile</Link>
          </>
        )}
      </div>

      {token && (
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      )}
    </nav>
  );
}

export default Navbar;
