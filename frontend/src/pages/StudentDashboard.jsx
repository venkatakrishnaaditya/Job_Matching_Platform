import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { resumeAPI, matchingAPI, applicationsAPI } from "../services/api";
import ConfirmDeleteModal from "../components/ConfirmDeleteModal";
import JobDetailsModal from "../components/JobDetailsModal";

function CANDIDATEDashboard() {
  const [jobs, setJobs] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(true);

  const [filters, setFilters] = useState({ search: "", matchMin: 0 });
  const [applied, setApplied] = useState(new Set());
  const [resumeStatus, setResumeStatus] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [loadingResume, setLoadingResume] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingResume, setDeletingResume] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [skillRecommendations, setSkillRecommendations] = useState([]);

  // Fetch ranked jobs from backend
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoadingJobs(true);
        const response = await matchingAPI.getRankedJobs(0);
        console.log('Raw API response:', response);
        if (response && response.matches) {
          // Log first match to see what fields backend is sending
          if (response.matches.length > 0) {
            console.log('First match from backend:', response.matches[0]);
          }
          // Transform API response to match UI expectations
          const transformedJobs = response.matches.map(match => ({
            id: match.jobId,
            title: match.title,
            company: match.company || 'Company Name',
            match: Math.round(match.matchScore),
            location: match.location,
            jobType: match.jobType,
            description: match.description,
            requiredSkills: match.requiredSkills || [],
            status: match.status,
            salary: match.salary,
            experience: match.experience,
            education: match.education,
            breakdown: match.breakdown
          }));
          console.log('Transformed jobs:', transformedJobs.map(j => ({ id: j.id, title: j.title })));
          console.log('First transformed job full details:', transformedJobs[0]);
          setJobs(transformedJobs);
        }
      } catch (err) {
        console.error('Error fetching jobs:', err);
      } finally {
        setLoadingJobs(false);
      }
    };

    fetchJobs();
  }, []);

  // Fetch existing applications to mark as applied
  useEffect(() => {
    const fetchExistingApplications = async () => {
      try {
        const response = await applicationsAPI.getMyApplications();
        console.log('Applications response:', response);
        if (response && response.applications && Array.isArray(response.applications)) {
          const appliedJobIds = new Set(
            response.applications.map(app => app.job_id)
          );
          console.log('Applied job IDs:', Array.from(appliedJobIds));
          setApplied(appliedJobIds);
        }
      } catch (err) {
        console.error('Error fetching applications:', err);
      }
    };

    fetchExistingApplications();
  }, []);

  // Fetch resume status from backend and localStorage
  useEffect(() => {
    const fetchResumeStatus = async () => {
      // First check localStorage for immediate display
      const storedResume = localStorage.getItem('resumeData');
      if (storedResume) {
        try {
          setResumeStatus(JSON.parse(storedResume));
        } catch (e) {
          console.error('Error parsing stored resume:', e);
        }
      }

      // Then fetch from backend to verify/update
      try {
        const response = await resumeAPI.getStatus();
        if (response && response.resume) {
          const backendResume = {
            filename: response.resume.filename || response.resume.original_filename,
            uploadDate: response.resume.uploaded_at || response.resume.createdAt,
            resumeUrl: response.resume.resume_url || response.resume.url
          };
          setResumeStatus(backendResume);
          // Sync localStorage with backend
          localStorage.setItem('resumeData', JSON.stringify(backendResume));
        }
      } catch (err) {
        console.log('No resume found or error fetching:', err.message);
        // Keep localStorage data if backend fails
      }
      
      // Fetch parsed data for name and experience
      try {
        const parsedResponse = await resumeAPI.getParsedData();
        if (parsedResponse && parsedResponse.data) {
          setParsedData(parsedResponse.data);
        }
      } catch (err) {
        console.log('No parsed data found:', err.message);
      } finally {
        setLoadingResume(false);
      }

    };

    fetchResumeStatus();
  }, []);

  // Fetch skill recommendations
  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const response = await matchingAPI.getSkillRecommendations();
        setSkillRecommendations(response.recommendations || []);
      } catch (err) {
        console.error('Failed to fetch skill recommendations:', err);
      }
    };
    
    fetchRecommendations();
  }, []);

  const filtered = jobs.filter(
    (j) =>
      j.match >= filters.matchMin &&
      (j.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        j.company.toLowerCase().includes(filters.search.toLowerCase()))
  );

   const handleApply = async (jobId) => {
    try {
      await applicationsAPI.apply(jobId);
      setApplied((prev) => new Set(prev).add(jobId));
      alert('Application submitted successfully!');
    } catch (err) {
      console.error('Error applying:', err);
      alert('Failed to apply. Please try again.');
    }
  };

  const handleDeleteResume = async () => {
    try {
      setDeletingResume(true);
      await resumeAPI.deleteResume();
      
      // Clear localStorage
      localStorage.removeItem('resumeData');
      
      // Update state
      setResumeStatus(null);
      setShowDeleteModal(false);
      
      alert('Resume deleted successfully');
    } catch (err) {
      alert('Failed to delete resume. Please try again.');
      console.error('Error deleting resume:', err);
    } finally {
      setDeletingResume(false);
    }
  };

  return (
    <section className="jobs-section">
      <div className="jobs-container">
        <div className="jobs-header">
          <div className="dashboard-header-content">
            <div>
              <h1>CANDIDATE Dashboard</h1>
              {parsedData?.candidateName && (
                <p className="candidate-header-name">👤 {parsedData.candidateName}</p>
              )}
              {parsedData?.totalExperienceYears !== null && parsedData?.totalExperienceYears !== undefined ? (
                <span className="candidate-experience-badge">
                  {parsedData.totalExperienceYears > 0 
                    ? `📊 ${parsedData.totalExperienceYears} Years Experience` 
                    : '📊 Fresher'}
                </span>
              ) : parsedData && (
                <span className="candidate-experience-badge">📊 Fresher</span>
              )}
            </div>
          </div>
        </div>

        <div className="jobs-content">
          <aside className="jobs-sidebar">
            {/* Resume Status Card */}
            <div className="resume-status-card">
              <h3>📄 Resume Status</h3>
              {resumeStatus ? (
                <div className="resume-uploaded">
                  <div className="resume-info">
                    <span className="resume-icon">✅</span>
                    <div className="resume-details">
                      <p className="resume-filename">{resumeStatus.filename || 'Your Resume '}</p>
                      <p className="resume-date">
                        {resumeStatus.uploadDate 
                          ? new Date(resumeStatus.uploadDate).toLocaleDateString('en-US', { 
                              month: 'short', 
                              day: 'numeric', 
                              year: 'numeric' 
                            })
                          : 'Recently uploaded'
                        }
                      </p>
                    </div>
                  </div>
                  <div className="resume-actions">
                    <Link to="/upload-resume" className="update-resume-btn">
                      Update Resume
                    </Link>
                    <button 
                      onClick={() => setShowDeleteModal(true)} 
                      className="remove-resume-btn"
                      disabled={deletingResume}
                    >
                      Remove Resume
                    </button>
                  </div>
                </div>
              ) : (
                <div className="resume-not-uploaded">
                  <span className="resume-icon-empty">📋</span>
                  <p className="resume-empty-text">No resume uploaded</p>
                  <Link to="/upload-resume" className="upload-resume-btn">
                    Upload Resume
                  </Link>
                </div>
              )}
            </div>

            {/* Quick Links */}
            <div className="filter-card">
              <h3>Quick Actions</h3>
              <Link to="/browse-jobs" className="cta-btn">Browse Jobs</Link>
              <Link to="/my-applications" className="cta-btn">My Applications</Link>
              <Link to="/profile" className="cta-btn cta-btn-secondary">My Profile</Link>
            </div>

            <div className="filter-card">
              <h3>Filters</h3>
              <div className="filter-group">
                <label>Search</label>
                <input
                  className="filter-input"
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  placeholder="Job title or company"
                />
              </div>

              <div className="filter-group">
                <label>Minimum Match</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={filters.matchMin}
                  onChange={(e) => setFilters({ ...filters, matchMin: Number(e.target.value) })}
                />
                <div className="match-value">{filters.matchMin}%</div>
              </div>
            </div>

            <div className="stats-card">
              <h4>Your Stats</h4>
              <div className="stat-item">
                <span className="stat-label">Jobs Applied</span>
                <span className="stat-value">{applied.size}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Recommendations</span>
                <span className="stat-value">{filtered.length}</span>
              </div>
            </div>
          </aside>

            <main className="jobs-list">
            {loadingJobs ? (
              <div className="loading">Loading job recommendations...</div>
            ) : (
              <>
            {/* Quick Action Cards */}
            <div className="dashboard-action-cards">
              <Link to="/browse-jobs" className="action-card">
                <span className="action-card-icon">🔍</span>
                <h3>Browse Jobs</h3>
                <p>Explore job opportunities</p>
              </Link>
              

              <Link to="/my-applications" className="action-card">
                <span className="action-card-icon">📋</span>
                <h3>My Applications</h3>
                <p className="applications-count">
                  {applied.size} {applied.size === 1 ? 'application' : 'applications'} tracked
                </p>
              </Link>

              <Link to="/profile" className="action-card">
                <span className="action-card-icon">👤</span>
                <h3>My Profile</h3>
                <p>Update your information</p>
              </Link>
            </div>

            {/* Skill Recommendations Section */}
            {skillRecommendations.length > 0 && parsedData?.skills?.length > 0 && (
              <div className="skill-recommendations-section">
                <div className="recommendations-header">
                  <h3 className="recommendations-title">
                    🎯 Skills to Improve Your Job Matches
                  </h3>
                  <p className="recommendations-subtitle">
                    Learn these skills to unlock more job opportunities
                  </p>
                </div>
                
                <div className="skill-cards-grid">
                  {skillRecommendations.map((rec, idx) => (
                    <div key={idx} className="skill-recommendation-card">
                      <div className="skill-icon">💡</div>
                      <h4 className="skill-name">{rec.skill}</h4>
                      <p className="skill-impact">+{rec.jobCount} jobs</p>
                    </div>
                  ))}
                </div>
              </div>
            )}


            {/* Job Recommendations */}
            <div className="sample-data-banner">
            🔄 <strong>AI Recommendations</strong> - Powered by AI Matching
            </div>
            <h2 className="section-title">Recommended Jobs</h2>
            {filtered.map((job) => (
              <div key={job.id} className="job-card">
                <div className="job-header">
                  <div className="job-title-section">
                    <h2 className="job-title">{job.title}</h2>
                    <p className="job-company">{job.company}</p>
                  </div>
                  <div className="job-match-badge">
                    <span className="match-percentage">{job.match}%</span>
                    <p>Match</p>
                  </div>
                </div>

                  <div className="job-actions">
                  {(() => {
                    const isApplied = applied.has(job.id);
                    console.log(`Job ${job.title} (${job.id}): isApplied=${isApplied}, appliedSet has:`, Array.from(applied));
                    return isApplied;
                  })() ? (
                    <button className="apply-btn applied" disabled>✓ Applied</button>
                  ) : (
                    <button 
                      className="apply-btn"
                      onClick={() => handleApply(job.id)}
                    >
                      Apply Now
                    </button>
                  )}
                  <button onClick={() => {
                    console.log('Opening modal for job:', job);
                    setSelectedJob(job);
                  }} className="save-btn">View Details</button>
                </div>
              </div>
            ))}
            </>
            )}
          </main>
        </div>
      </div>

      {/* Confirm Delete Modal */}
      <ConfirmDeleteModal 
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDeleteResume}
        itemName={resumeStatus?.filename || 'your resume'}
      />

      {/* Job Details Modal */}
      {selectedJob && (
        <JobDetailsModal 
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
        />
      )}
    </section>
  );
}

export default CANDIDATEDashboard;
