import { useState, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { authAPI } from "../services/api";

function ResetPassword() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const token = searchParams.get("token");

    const [formData, setFormData] = useState({
        password: "",
        confirmPassword: "",
    });
    const [loading, setLoading] = useState(false);
    const [verifying, setVerifying] = useState(true);
    const [tokenValid, setTokenValid] = useState(false);
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);

    // Verify token on load
    useEffect(() => {
        const verifyToken = async () => {
            if (!token) {
                setError("No reset token provided. Please request a new password reset.");
                setVerifying(false);
                return;
            }

            try {
                const response = await authAPI.verifyResetToken(token);
                setTokenValid(true);
                setEmail(response.email);
            } catch (err) {
                setError("This reset link is invalid or has expired. Please request a new one.");
                setTokenValid(false);
            } finally {
                setVerifying(false);
            }
        };

        verifyToken();
    }, [token]);

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

        // Validate passwords match
        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        // Validate password strength
        if (formData.password.length < 6) {
            setError("Password must be at least 6 characters long");
            return;
        }

        setLoading(true);

        try {
            await authAPI.resetPassword(token, formData.password);
            setSuccess(true);

            // Redirect to login after 3 seconds
            setTimeout(() => {
                navigate("/login");
            }, 3000);
        } catch (err) {
            setError(err.message || "Failed to reset password. Please try again.");
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
                            <span className="benefit-icon">🔒</span>
                            <p>Create a strong, unique password</p>
                        </div>
                        <div className="benefit-item">
                            <span className="benefit-icon">✓</span>
                            <p>Minimum 6 characters required</p>
                        </div>
                        <div className="benefit-item">
                            <span className="benefit-icon">🔐</span>
                            <p>Your password is securely encrypted</p>
                        </div>
                    </div>
                </div>

                <div className="auth-right">
                    <div className="auth-card">
                        {verifying ? (
                            <div className="loading-state">
                                <div className="spinner"></div>
                                <p>Verifying reset link...</p>
                            </div>
                        ) : success ? (
                            <div className="success-message">
                                <div className="success-icon">✅</div>
                                <h2>Password Reset Successful!</h2>
                                <p>
                                    Your password has been reset successfully.
                                </p>
                                <p>Redirecting to login...</p>
                                <Link to="/login" className="auth-submit" style={{ display: 'inline-block', marginTop: '16px', textDecoration: 'none' }}>
                                    Go to Login
                                </Link>
                            </div>
                        ) : !tokenValid ? (
                            <div className="error-state">
                                <div className="error-icon">❌</div>
                                <h2>Invalid Reset Link</h2>
                                <p>{error}</p>
                                <Link to="/forgot-password" className="auth-submit" style={{ display: 'inline-block', marginTop: '16px', textDecoration: 'none' }}>
                                    Request New Reset Link
                                </Link>
                            </div>
                        ) : (
                            <>
                                <h2>Reset Your Password</h2>
                                <p className="auth-subtitle">
                                    Enter a new password for <strong>{email}</strong>
                                </p>

                                {error && <div className="auth-error">{error}</div>}

                                <form onSubmit={handleSubmit} className="auth-form">
                                    <div className="form-group">
                                        <label htmlFor="password">New Password</label>
                                        <input
                                            type="password"
                                            id="password"
                                            name="password"
                                            placeholder="Enter new password"
                                            value={formData.password}
                                            onChange={handleChange}
                                            required
                                            minLength={6}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="confirmPassword">Confirm Password</label>
                                        <input
                                            type="password"
                                            id="confirmPassword"
                                            name="confirmPassword"
                                            placeholder="Confirm new password"
                                            value={formData.confirmPassword}
                                            onChange={handleChange}
                                            required
                                            minLength={6}
                                        />
                                    </div>

                                    <button type="submit" className="auth-submit" disabled={loading}>
                                        {loading ? "Resetting..." : "Reset Password"}
                                    </button>
                                </form>
                            </>
                        )}

                        <div className="auth-divider"></div>

                        <div className="auth-links">
                            <p>
                                Remember your password?{" "}
                                <Link to="/login" className="auth-link">
                                    Back to Login
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
        .loading-state, .error-state, .success-message {
          text-align: center;
          padding: 20px 0;
        }
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #1e3a5f;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 16px;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .success-icon, .error-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }
        .success-message h2 {
          color: #28a745;
          margin-bottom: 12px;
        }
        .error-state h2 {
          color: #dc3545;
          margin-bottom: 12px;
        }
        .success-message p, .error-state p {
          color: #666;
          margin-bottom: 8px;
        }
      `}</style>
        </section>
    );
}

export default ResetPassword;
