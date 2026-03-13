import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

function Landing() {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  // Redirect logged-in users to their dashboard
  useEffect(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    
    if (token) {
      // User is logged in, redirect to dashboard
      if (role === 'CANDIDATE') {
        navigate('/student-dashboard', { replace: true });
      } else if (role === 'RECRUITER') {
        navigate('/recruiter-dashboard', { replace: true });
      }
    }
  }, [navigate]);

  const handleScroll = () => {
    setScrolled(window.scrollY > 50);
  };

  window.addEventListener("scroll", handleScroll);

  return (
    <>
      {/* HERO SECTION */}
      <section className="landing-hero">
        <div className="landing-hero-content">
          <div className="landing-left">
            <h1>Fill Your Career With Opportunities</h1>
            <p>
              Connect Talent AI helps CANDIDATEs get matched with the right jobs
              and enables RECRUITERs to hire smarter using AI-powered screening.
            </p>
            <div className="cta-buttons">
              <Link to="/login" className="cta-btn">
                Get Started
              </Link>
              <Link to="/register" className="cta-btn cta-btn-secondary">
                Learn More
              </Link>
            </div>
          </div>

          <div className="landing-right">
            <img 
              src="/C__2_-removebg-preview.png" 
              alt="AI-powered job matching illustration" 
            />
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section className="landing-features">
        <div className="feature-box">
          <div className="feature-icon">📊</div>
          <h3>300+ Jobs</h3>
          <p>AI-matched job opportunities tailored to your skills</p>
        </div>

        <div className="feature-box">
          <div className="feature-icon">👥</div>
          <h3>1000+ CANDIDATEs</h3>
          <p>Actively using our platform to advance their careers</p>
        </div>

        <div className="feature-box">
          <div className="feature-icon">🤖</div>
          <h3>AI Matching</h3>
          <p>Smart resume screening and candidate ranking</p>
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section className="landing-how-it-works">
        <div className="how-it-works-container">
          <h2>How It Works</h2>
          <div className="steps-grid">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Create Your Profile</h3>
              <p>Sign up and upload your resume in seconds</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>AI Analysis</h3>
              <p>Our AI analyzes your skills and preferences</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Get Matched</h3>
              <p>Receive job recommendations perfectly suited for you</p>
            </div>
            <div className="step">
              <div className="step-number">4</div>
              <h3>Apply & Succeed</h3>
              <p>Apply to matched jobs and land your dream role</p>
            </div>
          </div>
        </div>
      </section>

      {/* CALL TO ACTION SECTION */}
      <section className="landing-cta-final">
        <div className="cta-final-content">
          <h2>Ready to Find Your Perfect Job Match?</h2>
          <p>Join hundreds of CANDIDATEs who've already found their dream jobs</p>
          <Link to="/register" className="cta-btn cta-btn-large">
            Start Your Journey Today
          </Link>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>Connect Talent AI</h4>
            <p>Revolutionizing recruitment through artificial intelligence</p>
          </div>
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li><Link to="/login">Login</Link></li>
              <li><Link to="/register">Register</Link></li>
              <li><Link to="/">Home</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>For RECRUITERs</h4>
            <ul>
              <li><a href="#hiring">Start Hiring</a></li>
              <li><a href="#pricing">View Pricing</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 Connect Talent AI. All rights reserved.</p>
        </div>
      </footer>
    </>
  );
}

export default Landing;
