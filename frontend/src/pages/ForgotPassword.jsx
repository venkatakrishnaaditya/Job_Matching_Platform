import { useState } from "react";
import { Link } from "react-router-dom";
import { authAPI } from "../services/api";

function ForgotPassword() {
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            await authAPI.forgotPassword(email);
            setSubmitted(true);
        } catch (err) {
            setError(err.message || "Failed to send reset email. Please try again.");
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
                            <span className="benefit-icon">🔐</span>
                            <p>Secure password reset process</p>
                        </div>
                        <div className="benefit-item">
                            <span className="benefit-icon">📧</span>
                            <p>Reset link sent to your email</p>
                        </div>
                        <div className="benefit-item">
                            <span className="benefit-icon">⏰</span>
                            <p>Link expires in 1 hour for security</p>
                        </div>
                    </div>
                </div>

                <div className="auth-right">
                    <div className="auth-card">
                        {!submitted ? (
                            <>
                                <h2>Forgot Password?</h2>
                                <p className="auth-subtitle">
                                    Enter your email and we'll send you a link to reset your password.
                                </p>

                                {error && <div className="auth-error">{error}</div>}

                                <form onSubmit={handleSubmit} className="auth-form">
                                    <div className="form-group">
                                        <label htmlFor="email">Email Address</label>
                                        <input
                                            type="email"
                                            id="email"
                                            name="email"
                                            placeholder="you@example.com"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            required
                                        />
                                    </div>

                                    <button type="submit" className="auth-submit" disabled={loading}>
                                        {loading ? "Sending..." : "Send Reset Link"}
                                    </button>
                                </form>
                            </>
                        ) : (
                            <div className="success-message">
                                <div className="success-icon">✉️</div>
                                <h2>Check Your Email</h2>
                                <p>
                                    If an account exists for <strong>{email}</strong>, you'll receive
                                    a password reset link shortly.
                                </p>
                                <p className="success-note">
                                    Don't see it? Check your spam folder.
                                </p>
                            </div>
                        )}

                        <div className="auth-divider"></div>

                        <div className="auth-links">
                            <p>
                                Remember your password?{" "}
                                <Link to="/login" className="auth-link">
                                    Back to Login
                                </Link>
                            </p>
                            <p>
                                Don't have an account?{" "}
                                <Link to="/register" className="auth-link">
                                    Sign up here
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
        .success-message {
          text-align: center;
          padding: 20px 0;
        }
        .success-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }
        .success-message h2 {
          color: #1e3a5f;
          margin-bottom: 12px;
        }
        .success-message p {
          color: #666;
          margin-bottom: 8px;
        }
        .success-note {
          font-size: 14px;
          color: #888 !important;
        }
      `}</style>
        </section>
    );
}

export default ForgotPassword;
