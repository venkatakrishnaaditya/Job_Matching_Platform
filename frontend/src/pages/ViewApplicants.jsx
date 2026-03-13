import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import BackButton from '../components/BackButton';
import { applicationsAPI } from "../services/api";

function ViewApplicants() {
  const { jobId } = useParams();
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    searchTerm: "",
    status: "all",
    matchMin: 0,
  });
  const [expandedId, setExpandedId] = useState(null);
  const [updating, setUpdating] = useState(false);

  // Fetch applicants when component mounts
  useEffect(() => {
    fetchApplicants();
  }, [jobId]);

  const fetchApplicants = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await applicationsAPI.getJobApplicants(jobId);
      setApplicants(data);
    } catch (err) {
      setError(err.message || "Failed to load applicants");
      console.error("Error fetching applicants:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (applicationId, newStatus) => {
    try {
      setUpdating(true);
      await applicationsAPI.updateStatus(applicationId, newStatus);
      // Refresh the list
      await fetchApplicants();
      alert(`Application status updated to ${newStatus}`);
    } catch (err) {
      alert(err.message || "Failed to update status");
      console.error("Error updating status:", err);
    } finally {
      setUpdating(false);
    }
  };

  const handleViewResume = (applicant) => {
    if (applicant.resumeFiles?.resumePreviewUrl) {
      applicationsAPI.previewResume(applicant.resumeFiles.resumePreviewUrl);
    } else if (applicant.resumeFiles?.resumeFileUrl) {
      applicationsAPI.previewResume(applicant.resumeFiles.resumeFileUrl);
    } else {
      alert("Resume file not available. Please ask the candidate to re-upload their resume.");
    }
  };

  const handleDownloadResume = (applicant) => {
    if (applicant.resumeFiles?.resumeDownloadUrl) {
      applicationsAPI.downloadResume(applicant.resumeFiles.resumeDownloadUrl);
    } else if (applicant.resumeFiles?.resumeFileUrl) {
      applicationsAPI.downloadResume(applicant.resumeFiles.resumeFileUrl);
    } else {
      alert("Resume file not available. Please ask the candidate to re-upload their resume.");
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "1 day ago";
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const filteredApplicants = applicants.filter((applicant) => {
    const candidateName = applicant.candidateDetails?.name || "Unknown";
    const matchesSearch = candidateName
      .toLowerCase()
      .includes(filters.searchTerm.toLowerCase());
    const matchesStatus =
      filters.status === "all" || applicant.status === filters.status;
    const matchesScore = applicant.snapshotMatchScore >= filters.matchMin;
    return matchesSearch && matchesStatus && matchesScore;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case "Shortlisted":
        return "status-shortlisted";
      case "Reviewed":
        return "status-reviewed";
      case "Applied":
        return "status-pending";
      case "Rejected":
        return "status-rejected";
      case "Withdrawn":
        return "status-withdrawn";
      default:
        return "";
    }
  };

  const getMatchColor = (match) => {
    if (match >= 90) return "match-excellent";
    if (match >= 80) return "match-good";
    return "match-fair";
  };

  return (
    <section className="applicants-section">
      <div className="applicants-container">
        <BackButton />
        {/* HEADER */}
        <div className="applicants-header">
          <h1>Job Applicants</h1>
          <p>Review and manage applications for your job postings</p>
        </div>

        {loading && (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <p>Loading applicants...</p>
          </div>
        )}

        {error && (
          <div style={{ textAlign: "center", padding: "40px", color: "red" }}>
            <p>Error: {error}</p>
            <button onClick={fetchApplicants} className="btn-primary">
              Retry
            </button>
          </div>
        )}

        {!loading && !error && (
          <>
            {/* FILTERS */}
            <div className="applicants-filters">
              <div className="filter-item">
                <input
                  type="text"
                  placeholder="Search applicants by name..."
                  value={filters.searchTerm}
                  onChange={(e) =>
                    setFilters({ ...filters, searchTerm: e.target.value })
                  }
                  className="filter-input"
                />
              </div>

              <div className="filter-item">
                <select
                  value={filters.status}
                  onChange={(e) =>
                    setFilters({ ...filters, status: e.target.value })
                  }
                  className="filter-select"
                >
                  <option value="all">All Status</option>
                  <option value="Applied">Applied</option>
                  <option value="Reviewed">Reviewed</option>
                  <option value="Shortlisted">Shortlisted</option>
                  <option value="Rejected">Rejected</option>
                  <option value="Withdrawn">Withdrawn</option>
                </select>
              </div>

              <div className="filter-item">
                <label>Min Match Score:</label>
                <select
                  value={filters.matchMin}
                  onChange={(e) =>
                    setFilters({ ...filters, matchMin: Number(e.target.value) })
                  }
                  className="filter-select"
                >
                  <option value="0">All Scores</option>
                  <option value="75">75%+</option>
                  <option value="80">80%+</option>
                  <option value="90">90%+</option>
                </select>
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

            {/* STATS */}
            <div className="applicants-stats">
              <div className="stat-box">
                <span className="stat-number">{filteredApplicants.length}</span>
                <span className="stat-label">Total Applications</span>
              </div>
              <div className="stat-box">
                <span className="stat-number">
                  {applicants.filter((a) => a.status === "Shortlisted").length}
                </span>
                <span className="stat-label">Shortlisted</span>
              </div>
              <div className="stat-box">
                <span className="stat-number">
                  {applicants.filter((a) => a.status === "Applied").length}
                </span>
                <span className="stat-label">Pending Review</span>
              </div>
              <div className="stat-box">
                <span className="stat-number">
                  {applicants.length > 0
                    ? Math.round(
                        applicants.reduce((sum, a) => sum + a.snapshotMatchScore, 0) /
                          applicants.length
                      )
                    : 0}
                  %
                </span>
                <span className="stat-label">Avg Match Score</span>
              </div>
            </div>

            {/* APPLICANTS TABLE */}
            <div className="applicants-table-wrapper">
              {filteredApplicants.length > 0 ? (
                <table className="applicants-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Experience</th>
                      <th>Skills</th>
                      <th>Match Score</th>
                      <th>Status</th>
                      <th>Applied</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredApplicants.map((applicant) => {
                      const candidateName = applicant.candidateDetails?.name || "Unknown";
                      const candidateEmail = applicant.candidateDetails?.email || "";
                      const skills = applicant.resumeSnapshot?.skills || [];
                      const exp = applicant.resumeSnapshot?.exp || 0;
                      
                      return (
                        <tr key={applicant._id}>
                          <td className="td-name">
                            <strong>{candidateName}</strong>
                            <br />
                            <small>{candidateEmail}</small>
                          </td>
                          <td className="td-experience">{exp} years</td>
                          <td className="td-skills">
                            <div className="skills-preview">
                              {skills.slice(0, 2).join(", ")}
                              {skills.length > 2 && " ..."}
                            </div>
                          </td>
                          <td className="td-match">
                            <div className={`match-score ${getMatchColor(applicant.snapshotMatchScore)}`}>
                              {Math.round(applicant.snapshotMatchScore)}%
                            </div>
                          </td>
                          <td className="td-status">
                            <span className={`status-badge ${getStatusColor(applicant.status)}`}>
                              {applicant.status}
                            </span>
                          </td>
                          <td className="td-date">{formatDate(applicant.appliedAt)}</td>
                          <td className="td-actions">
                            <button
                              className="action-btn expand-btn"
                              onClick={() =>
                                setExpandedId(
                                  expandedId === applicant._id ? null : applicant._id
                                )
                              }
                            >
                              {expandedId === applicant._id ? "−" : "+"}
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              ) : (
                <div className="no-applicants">
                  <p className="no-applicants-icon">📋</p>
                  <h3>No applicants found</h3>
                  <p>Adjust your filters to see more applicants</p>
                </div>
              )}
            </div>

            {/* EXPANDED DETAILS */}
            {expandedId && (
              <div className="applicant-details">
                {(() => {
                  const applicant = applicants.find((a) => a._id === expandedId);
                  if (!applicant) return null;
                  
                  const candidateName = applicant.candidateDetails?.name || "Unknown";
                  const candidateEmail = applicant.candidateDetails?.email || "";
                  const skills = applicant.resumeSnapshot?.skills || [];
                  const exp = applicant.resumeSnapshot?.exp || 0;
                  const edu = applicant.resumeSnapshot?.edu || "Not specified";
                  const hasResume = applicant.resumeFiles?.resumeFileUrl;
                  
                  return (
                    <div className="details-card">
                      <h3>{candidateName}</h3>
                      <div className="details-grid">
                        <div className="detail-item">
                          <label>Email</label>
                          <p>{candidateEmail}</p>
                        </div>
                        <div className="detail-item">
                          <label>Experience</label>
                          <p>{exp} years</p>
                        </div>
                        <div className="detail-item">
                          <label>Education</label>
                          <p>{edu}</p>
                        </div>
                        <div className="detail-item">
                          <label>Match Score</label>
                          <p>{Math.round(applicant.snapshotMatchScore)}%</p>
                        </div>
                        <div className="detail-item">
                          <label>Skills Score</label>
                          <p>{Math.round(applicant.snapshotBreakdown?.skillsScore || 0)}%</p>
                        </div>
                        <div className="detail-item">
                          <label>Experience Score</label>
                          <p>{Math.round(applicant.snapshotBreakdown?.experienceScore || 0)}%</p>
                        </div>
                        <div className="detail-item">
                          <label>Education Score</label>
                          <p>{Math.round(applicant.snapshotBreakdown?.educationScore || 0)}%</p>
                        </div>
                        <div className="detail-item">
                          <label>Current Status</label>
                          <p>
                            <span className={`status-badge ${getStatusColor(applicant.status)}`}>
                              {applicant.status}
                            </span>
                          </p>
                        </div>
                        <div className="detail-item full-width">
                          <label>Skills</label>
                          <div className="skills-full">
                            {skills.map((skill, idx) => (
                              <span key={idx} className="skill-tag">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="details-actions">
                        {/* Status Update Buttons */}
                        {applicant.status !== "Withdrawn" && (
                          <>
                            {applicant.status === "Applied" && (
                              <button
                                className="details-btn review-btn"
                                onClick={() => handleStatusUpdate(applicant._id, "Reviewed")}
                                disabled={updating}
                              >
                                Mark as Reviewed
                              </button>
                            )}
                            {(applicant.status === "Applied" || applicant.status === "Reviewed") && (
                              <button
                                className="details-btn shortlist-btn"
                                onClick={() => handleStatusUpdate(applicant._id, "Shortlisted")}
                                disabled={updating}
                              >
                                Shortlist Candidate
                              </button>
                            )}
                            {applicant.status !== "Rejected" && (
                              <button
                                className="details-btn reject-btn"
                                onClick={() => handleStatusUpdate(applicant._id, "Rejected")}
                                disabled={updating}
                              >
                                Reject Application
                              </button>
                            )}
                          </>
                        )}
                        
                        {/* Resume Buttons */}
                        {hasResume ? (
                          <>
                            <button
                              className="details-btn view-resume-btn"
                              onClick={() => handleViewResume(applicant)}
                            >
                              📄 View Resume
                            </button>
                            <button
                              className="details-btn download-resume-btn"
                              onClick={() => handleDownloadResume(applicant)}
                            >
                              ⬇️ Download Resume
                            </button>
                          </>
                        ) : (
                          <button className="details-btn" disabled>
                            Resume Not Available
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
}

export default ViewApplicants;
