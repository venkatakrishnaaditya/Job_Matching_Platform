import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authAPI } from "../services/api";

function Login() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Redirect if already logged in
  useEffect(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    if (token) {
      // Already logged in, redirect to dashboard
      if (role === 'CANDIDATE') {
        navigate('/student-dashboard', { replace: true });
      } else if (role === 'RECRUITER') {
        navigate('/recruiter-dashboard', { replace: true });
      }
    }
  }, [navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Call login API
      const response = await authAPI.login({
        email: formData.email,
        password: formData.password,
      });

      // Store token and user info
      localStorage.setItem('token', response.access_token);

      // Decode token to get role (simple base64 decode of JWT payload)
      const tokenPayload = JSON.parse(atob(response.access_token.split('.')[1]));
      const userRole = tokenPayload.role;

      localStorage.setItem('role', userRole);
      localStorage.setItem('email', tokenPayload.email);

      // Navigate based on role
      if (userRole === 'CANDIDATE') {
        navigate("/student-dashboard", { replace: true });
      } else if (userRole === 'RECRUITER') {
        navigate("/recruiter-dashboard", { replace: true });
      }
    } catch (err) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-section">
      <div className="auth-container">
        <div className="auth-left">
          <div className="auth-brand">
            <h1>Connect Talent AI</h1>
            <p>AI-Powered Job Matching Platform</p>
          </div>
          <div className="auth-benefits">
            <div className="benefit-item">
              <span className="benefit-icon">✓</span>
              <p>Get matched with perfect job opportunities</p>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">✓</span>
              <p>AI-powered resume screening and ranking</p>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">✓</span>
              <p>Connect with top RECRUITERs instantly</p>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">✓</span>
              <p>Track your applications in real-time</p>
            </div>
          </div>
        </div>

        <div className="auth-right">
          <div className="auth-card">
            <h2>Login</h2>
            <p className="auth-subtitle">Welcome back! Sign in to your account</p>

            {error && <div className="auth-error">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-remember">
                <input type="checkbox" id="remember" name="remember" />
                <label htmlFor="remember">Remember me</label>
              </div>

              <button type="submit" className="auth-submit" disabled={loading}>
                {loading ? "Logging in..." : "Login"}
              </button>
            </form>

            <div className="auth-divider"></div>

            <div className="auth-links">
              <p>
                Don't have an account?{" "}
                <Link to="/register" className="auth-link">
                  Sign up here
                </Link>
              </p>
              <p>
                <Link to="/forgot-password" className="auth-link">
                  Forgot your password?
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Login;
