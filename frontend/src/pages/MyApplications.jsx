import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { applicationsAPI } from "../services/api";
import BackButton from "../components/BackButton";

function MyApplications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedApp, setExpandedApp] = useState(null);
  const [withdrawing, setWithdrawing] = useState(null);

  const [filters, setFilters] = useState({
    searchTerm: "",
    status: "all",
    matchMin: 0,
  });

  // Fetch applications from backend
  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        const response = await applicationsAPI.getMyApplications();
        setApplications(response.applications || []);
      } catch (err) {
        setError("Failed to load applications. Please try again.");
        console.error("Error fetching applications:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  const handleWithdraw = async (applicationId) => {
    if (!window.confirm("Are you sure you want to withdraw this application?")) {
      return;
    }

    try {
      setWithdrawing(applicationId);
      await applicationsAPI.withdraw(applicationId);
      // Remove from list
      setApplications((prev) =>
        prev.filter((app) => app.application_id !== applicationId)
      );
      alert("Application withdrawn successfully");
    } catch (err) {
      console.error("Error withdrawing application:", err);
      alert("Failed to withdraw application. Please try again.");
    } finally {
      setWithdrawing(null);
    }
  };

  const toggleBreakdown = (appId) => {
    setExpandedApp(expandedApp === appId ? null : appId);
  };

  const getStatusClass = (status) => {
    switch (status) {
      case "Applied":
        return "status-applied";
      case "Reviewed":
        return "status-reviewed";
      case "Shortlisted":
        return "status-shortlisted";
      case "Rejected":
        return "status-rejected";
      default:
        return "status-default";
    }
  };

  const getMatchScoreClass = (score) => {
    if (score >= 90) return "match-excellent";
    if (score >= 80) return "match-good";
    if (score >= 70) return "match-fair";
    return "match-low";
  };

  const filteredApplications = applications.filter((app) => {
    const matchesSearch =
      app.job_title.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
      app.company.toLowerCase().includes(filters.searchTerm.toLowerCase());
    const matchesStatus =
      filters.status === "all" || app.status === filters.status;
    const matchesScore = app.match_score >= filters.matchMin;
    return matchesSearch && matchesStatus && matchesScore;
  });

  return (
    <section className="jobs-section">
      <div className="jobs-container">
        <BackButton />
        
        {/* HEADER */}
        <div className="jobs-header">
          <h1>My Applications</h1>
          <p>Track your job applications and their status</p>
        </div>

        {loading && <div className="loading-message">Loading applications...</div>}

        {error && <div className="error-message">{error}</div>}

        {!loading && !error && (
          <div className="jobs-content">
            {/* SIDEBAR FILTERS */}
            <aside className="jobs-sidebar">
              <div className="filter-card">
                <h3>Filters</h3>

                <div className="filter-group">
                  <label>Search Applications</label>
                  <input
                    type="text"
                    placeholder="Job title or company..."
                    value={filters.searchTerm}
                    onChange={(e) =>
                      setFilters({ ...filters, searchTerm: e.target.value })
                    }
                  />
                </div>

                <div className="filter-group">
                  <label>Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) =>
                      setFilters({ ...filters, status: e.target.value })
                    }
                  >
                    <option value="all">All Status</option>
                    <option value="Applied">Applied</option>
                    <option value="Reviewed">Reviewed</option>
                    <option value="Shortlisted">Shortlisted</option>
                    <option value="Rejected">Rejected</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label>Min Match Score: {filters.matchMin}%</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="5"
                    value={filters.matchMin}
                    onChange={(e) =>
                      setFilters({
                        ...filters,
                        matchMin: parseInt(e.target.value),
                      })
                    }
                  />
                </div>

                <button
                  onClick={() =>
                    setFilters({
                      searchTerm: "",
                      status: "all",
                      matchMin: 0,
                    })
                  }
                  className="filter-reset-btn"
                >
                  Reset Filters
                </button>
              </div>

              <div className="stats-card">
                <h4>Application Stats</h4>
                <div className="stat-item">
                  <span className="stat-label">Total Applied</span>
                  <span className="stat-value">{applications.length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Active</span>
                  <span className="stat-value">
                    {
                      applications.filter(
                        (app) =>
                          app.status === "Applied" || app.status === "Reviewed"
                      ).length
                    }
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Shortlisted</span>
                  <span className="stat-value">
                    {
                      applications.filter(
                        (app) => app.status === "Shortlisted"
                      ).length
                    }
                  </span>
                </div>
              </div>
            </aside>

            {/* APPLICATIONS LIST */}
            <main className="jobs-list">
              {filteredApplications.length > 0 ? (
                filteredApplications.map((app) => (
                  <div key={app.application_id} className="job-card">
                    <div className="job-header">
                      <div className="job-title-section">
                        <h2 className="job-title">{app.job_title}</h2>
                        <p className="job-company">{app.company}</p>
                        <p className="application-date">
                          Applied:{" "}
                          {new Date(app.applied_at).toLocaleDateString(
                            "en-US",
                            {
                              month: "short",
                              day: "numeric",
                              year: "numeric",
                            }
                          )}
                        </p>
                      </div>
                      <div className="application-status-section">
                        <div className="job-match-badge">
                          <span
                            className={`match-percentage ${getMatchScoreClass(
                              Math.round(app.match_score)
                            )}`}
                          >
                            {Math.round(app.match_score)}%
                          </span>
                          <p>Match</p>
                        </div>
                        <span className={`status-badge ${getStatusClass(app.status)}`}>
                          {app.status}
                        </span>
                      </div>
                    </div>

                    {/* Breakdown Toggle */}
                    <button
                      className="breakdown-toggle"
                      onClick={() => toggleBreakdown(app.application_id)}
                    >
                      {expandedApp === app.application_id ? "▼" : "►"} View
                      Match Breakdown
                    </button>

                    {/* Breakdown Scores */}
                    {expandedApp === app.application_id && (
                      <div className="breakdown-section">
                        <div className="breakdown-item">
                          <span className="breakdown-label">Skills Match</span>
                          <div className="breakdown-bar">
                            <div
                              className="breakdown-fill"
                              style={{
                                width: `${app.breakdown?.skills_score || 0}%`,
                              }}
                            ></div>
                          </div>
                          <span className="breakdown-value">
                            {Math.round(app.breakdown?.skills_score || 0)}%
                          </span>
                        </div>
                        <div className="breakdown-item">
                          <span className="breakdown-label">
                            Experience Match
                          </span>
                          <div className="breakdown-bar">
                            <div
                              className="breakdown-fill"
                              style={{
                                width: `${app.breakdown?.experience_score || 0}%`,
                              }}
                            ></div>
                          </div>
                          <span className="breakdown-value">
                            {Math.round(app.breakdown?.experience_score || 0)}%
                          </span>
                        </div>
                        <div className="breakdown-item">
                          <span className="breakdown-label">
                            Education Match
                          </span>
                          <div className="breakdown-bar">
                            <div
                              className="breakdown-fill"
                              style={{
                                width: `${app.breakdown?.education_score || 0}%`,
                              }}
                            ></div>
                          </div>
                          <span className="breakdown-value">
                            {Math.round(app.breakdown?.education_score || 0)}%
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="job-actions">
                      <Link
                        to="/browse-jobs"
                        className="save-btn"
                        style={{
                          textDecoration: "none",
                          opacity: 1,
                          cursor: "pointer",
                        }}
                      >
                        View Similar Jobs
                      </Link>
                      {app.status === "Applied" && (
                        <button
                          className="withdraw-btn"
                          onClick={() => handleWithdraw(app.application_id)}
                          disabled={withdrawing === app.application_id}
                        >
                          {withdrawing === app.application_id
                            ? "Withdrawing..."
                            : "Withdraw Application"}
                        </button>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-jobs">
                  <p className="no-jobs-icon">📭</p>
                  <h3>No applications found</h3>
                  <p>
                    {applications.length === 0
                      ? "You haven't applied to any jobs yet"
                      : "Try adjusting your filters"}
                  </p>
                  {applications.length === 0 && (
                    <Link to="/browse-jobs" className="browse-jobs-link">
                      Browse Available Jobs
                    </Link>
                  )}
                </div>
              )}
            </main>
          </div>
        )}
      </div>
    </section>
  );
}

export default MyApplications;
