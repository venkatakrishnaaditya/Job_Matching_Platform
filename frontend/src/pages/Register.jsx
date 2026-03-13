import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authAPI } from "../services/api";

function Register() {
  const [userType, setUserType] = useState("CANDIDATE");
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    company: "",
    agree: false,
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
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.fullName || !formData.email || !formData.password) {
      setError("Please fill in all required fields");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!formData.agree) {
      setError("You must agree to the terms and conditions");
      return;
    }

    if (userType === "RECRUITER" && !formData.company) {
      setError("Company name is required for recruiters");
      return;
    }

    setLoading(true);

    try {
      // Map frontend fields to backend expected format
      const payload = {
        name: formData.fullName,     // fullName → name
        email: formData.email,
        password: formData.password,
        role: userType,              // userType → role
        company: formData.company    // Include company for recruiters
      };

      const response = await authAPI.register(payload);
      
      // Auto-login after successful registration
      // Store token if backend returns it, otherwise redirect to login
      if (response.access_token) {
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('role', userType);
        localStorage.setItem('email', formData.email);
        
        // Navigate to role-specific dashboard
        if (userType === 'CANDIDATE') {
          navigate("/student-dashboard", { replace: true });
        } else {
          navigate("/recruiter-dashboard", { replace: true });
        }
      } else {
        // No token returned, go to login
        navigate("/login", { replace: true });
      }
    } catch (err) {
      setError(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-section">
      <div className="auth-container">
        <div className="auth-left">
          <div className="auth-brand">
            <h1>Join Today</h1>
            <p>Start your journey with Connect Talent AI</p>
          </div>
          <div className="auth-benefits">
            <div className="benefit-item">
              <span className="benefit-icon">🎯</span>
              <p>Find your perfect job match in minutes</p>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">📈</span>
              <p>Boost your career with AI-powered insights</p>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">🤝</span>
              <p>Connect with top recruiters and companies</p>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">⚡</span>
              <p>Fast-track your hiring process</p>
            </div>
          </div>
        </div>

        <div className="auth-right">
          <div className="auth-card">
            <h2>Create Account</h2>
            <p className="auth-subtitle">Sign up and start connecting</p>

            {error && <div className="auth-error">{error}</div>}

            {/* USER TYPE SELECTOR */}
            <div className="user-type-selector">
              <label className={`user-type-option ${userType === "CANDIDATE" ? "active" : ""}`}>
                <input
                  type="radio"
                  name="userType"
                  value="CANDIDATE"
                  checked={userType === "CANDIDATE"}
                  onChange={(e) => setUserType(e.target.value)}
                />
                <span>👨‍🎓 Student</span>
              </label>
              <label className={`user-type-option ${userType === "RECRUITER" ? "active" : ""}`}>
                <input
                  type="radio"
                  name="userType"
                  value="RECRUITER"
                  checked={userType === "RECRUITER"}
                  onChange={(e) => setUserType(e.target.value)}
                />
                <span>💼 Recruiter</span>
              </label>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="fullName">Full Name *</label>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  placeholder="John Doe"
                  value={formData.fullName}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address *</label>
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

              {userType === "RECRUITER" && (
                <div className="form-group">
                  <label htmlFor="company">Company Name *</label>
                  <input
                    type="text"
                    id="company"
                    name="company"
                    placeholder="Your company name"
                    value={formData.company}
                    onChange={handleChange}
                    required={userType === "RECRUITER"}
                  />
                </div>
              )}

              <div className="form-group">
                <label htmlFor="password">Password *</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  placeholder="At least 8 characters"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password *</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-checkbox">
                <input
                  type="checkbox"
                  id="agree"
                  name="agree"
                  checked={formData.agree}
                  onChange={handleChange}
                  required
                />
                <label htmlFor="agree">
                  I agree to the Terms and Conditions
                </label>
              </div>

              <button type="submit" className="auth-submit" disabled={loading}>
                {loading ? "Creating account..." : "Create Account"}
              </button>
            </form>

            <div className="auth-divider"></div>

            <div className="auth-links">
              <p>
                Already have an account?{" "}
                <Link to="/login" className="auth-link">
                  Sign in here
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Register;
