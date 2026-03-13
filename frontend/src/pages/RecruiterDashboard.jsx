import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { jobAPI } from "../services/api";
import JobDetailsModal from "../components/JobDetailsModal";

function RECRUITERDashboard() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [archivedJobs, setArchivedJobs] = useState([]);
  const [activeTab, setActiveTab] = useState('active'); // 'active' or 'archived'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [togglingStatus, setTogglingStatus] = useState({});
  const [archiving, setArchiving] = useState({});
  const [restoring, setRestoring] = useState({});
  const [selectedJob, setSelectedJob] = useState(null);

  // Fetch recruiter's jobs from backend
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const [activeResponse, archivedResponse] = await Promise.all([
          jobAPI.getMyJobs(),
          jobAPI.getArchivedJobs()
        ]);
        setJobs(activeResponse.jobs || []);
        setArchivedJobs(archivedResponse.jobs || []);
      } catch (err) {
        setError('Failed to load your jobs. Please try again.');
        console.error('Error fetching jobs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  const handleToggleStatus = async (jobId, currentStatus) => {
    try {
      setTogglingStatus(prev => ({ ...prev, [jobId]: true }));
      const response = await jobAPI.toggleJobStatus(jobId);
      
      // Update local state
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.jobId === jobId 
            ? { ...job, status: response.status }
            : job
        )
      );
      
      alert(`Job ${response.status === 'CLOSED' ? 'closed' : 'reopened'} successfully!`);
    } catch (err) {
      alert('Failed to update job status. Please try again.');
      console.error('Error toggling status:', err);
    } finally {
      setTogglingStatus(prev => ({ ...prev, [jobId]: false }));
    }
  };

  const handleArchiveJob = async (jobId, jobStatus) => {
    if (jobStatus !== 'Closed') {
      alert('Only closed jobs can be archived. Please close the job first.');
      return;
    }

    if (!window.confirm('Are you sure you want to archive this job? It will be hidden from your dashboard but applications will be preserved.')) {
      return;
    }

    try {
      setArchiving(prev => ({ ...prev, [jobId]: true }));
      await jobAPI.archiveJob(jobId);
      
      // Find the archived job
      const archivedJob = jobs.find(job => job.jobId === jobId);
      
      // Remove from active jobs
      setJobs(prevJobs => prevJobs.filter(job => job.jobId !== jobId));
      
      // Add to archived jobs
      if (archivedJob) {
        setArchivedJobs(prev => [archivedJob, ...prev]);
      }
      
      alert('Job archived successfully!');
    } catch (err) {
      const errorMsg = err.message || 'Failed to archive job. Please try again.';
      alert(errorMsg);
      console.error('Error archiving job:', err);
    } finally {
      setArchiving(prev => ({ ...prev, [jobId]: false }));
    }
  };

  const handleRestoreJob = async (jobId) => {
    if (!window.confirm('Are you sure you want to restore this job? It will appear in your active jobs.')) {
      return;
    }

    try {
      setRestoring(prev => ({ ...prev, [jobId]: true }));
      await jobAPI.restoreJob(jobId);
      
      // Move from archived to active
      const restoredJob = archivedJobs.find(job => job.jobId === jobId);
      setArchivedJobs(prev => prev.filter(job => job.jobId !== jobId));
      if (restoredJob) {
        setJobs(prev => [restoredJob, ...prev]);
      }
      
      alert('Job restored successfully!');
    } catch (err) {
      const errorMsg = err.message || 'Failed to restore job. Please try again.';
      alert(errorMsg);
      console.error('Error restoring job:', err);
    } finally {
      setRestoring(prev => ({ ...prev, [jobId]: false }));
    }
  };

  const handleEditJob = (jobId) => {
    navigate(`/edit-job/${jobId}`);
  };

  const handleViewDetails = (job) => {
    setSelectedJob(job);
  };

  const handleCloseModal = () => {
    setSelectedJob(null);
  };

  // Calculate total applicants from all jobs
  const totalApplicants = jobs.reduce((sum, job) => sum + (job.applicantCount || 0), 0);
  const avgApplicants = jobs.length > 0 ? Math.round(totalApplicants / jobs.length) : 0;

  // Get current tab jobs
  const currentJobs = activeTab === 'active' ? jobs : archivedJobs;

  return (
    <section className="jobs-section">
      <div className="jobs-container">
        <div className="jobs-header">
          <div className="header-content">
            <div>
              <h1>RECRUITER Dashboard</h1>
              <p>Manage your job postings and review top candidates quickly.</p>
            </div>
            <Link to="/post-job" className="apply-btn header-cta-btn">
              ➕ Post New Job
            </Link>
          </div>
        </div>

        {loading && (
          <div className="loading-message">Loading your jobs...</div>
        )}

        {error && (
          <div className="error-message">{error}</div>
        )}

        {!loading && !error && (
          <div className="jobs-content">
          <aside className="jobs-sidebar">
            <div className="filter-card">
              <h3>Quick Links</h3>
              <Link to="/profile" className="cta-btn cta-btn-secondary">My Profile</Link>
            </div>

            <div className="stats-card">
              <h4>Hiring Stats</h4>
              <div className="stat-item">
                <span className="stat-label">Jobs Posted</span>
                <span className="stat-value">{jobs.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Total Applicants</span>
                <span className="stat-value">{totalApplicants}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Avg Applicants/Job</span>
                <span className="stat-value">{avgApplicants}</span>
              </div>
            </div>
          </aside>

          <main className="jobs-list">
            {/* Tabs */}
            <div className="jobs-tabs">
              <button 
                className={`tab-btn ${activeTab === 'active' ? 'active' : ''}`}
                onClick={() => setActiveTab('active')}
              >
                Active Jobs ({jobs.length})
              </button>
              <button 
                className={`tab-btn ${activeTab === 'archived' ? 'active' : ''}`}
                onClick={() => setActiveTab('archived')}
              >
                Archived Jobs ({archivedJobs.length})
              </button>
            </div>

            {/* Jobs List */}
            <h2 className="section-title">
              {activeTab === 'active' ? 'Active Job Postings' : 'Archived Jobs'}
            </h2>
            {currentJobs.length > 0 ? (
              currentJobs.map((job) => (
                <div key={job.jobId} className="job-card">
                  <div className="job-header">
                    <div className="job-title-section">
                      <h2 className="job-title">{job.title}</h2>
                      <p className="job-company">{job.company}</p>
                    </div>
                    <div className="job-meta">
                      <span className="job-meta-item">
                        <span className="icon">📍</span> {job.location}
                      </span>
                      <span className="job-meta-item">
                        <span className="icon">💼</span> {job.jobType}
                      </span>
                      <span className="job-meta-item">
                        <span className="icon">👥</span> {job.applicantCount || 0} Applicant{job.applicantCount !== 1 ? 's' : ''}
                      </span>
                      <span className="job-meta-item">
                        <span className={`status-badge ${job.status.toLowerCase()}`}>
                          {job.status}
                        </span>
                      </span>
                    </div>
                  </div>

                  <p className="job-description">{job.description.substring(0, 100)}...</p>

                  <div className="job-skills">
                    {job.requiredSkills.slice(0, 5).map((skill, idx) => (
                      <span key={idx} className="skill-tag">
                        {skill}
                      </span>
                    ))}
                  </div>

                  <div className="job-actions">
                    <button 
                      className="apply-btn view-details-btn" 
                      onClick={() => handleViewDetails(job)}
                    >
                      View Details
                    </button>
                    
                    {activeTab === 'active' ? (
                      <>
                        <Link to={`/view-applicants/${job.jobId}`} className="save-btn">View Applicants</Link>
                        <button 
                          className="save-btn" 
                          onClick={() => handleEditJob(job.jobId)}
                        >
                          Edit
                        </button>
                        <button 
                          className={`status-toggle-btn ${job.status === 'Open' ? 'close' : 'reopen'}`}
                          onClick={() => handleToggleStatus(job.jobId, job.status)}
                          disabled={togglingStatus[job.jobId]}
                        >
                          {togglingStatus[job.jobId] 
                            ? 'Updating...' 
                            : job.status === 'Open' ? 'Close' : 'Reopen'}
                        </button>
                        {job.status === 'Closed' && (
                          <button 
                            className="archive-btn"
                            onClick={() => handleArchiveJob(job.jobId, job.status)}
                            disabled={archiving[job.jobId]}
                          >
                            {archiving[job.jobId] ? 'Archiving...' : '🗄️ Archive'}
                          </button>
                        )}
                      </>
                    ) : (
                      <button 
                        className="restore-btn"
                        onClick={() => handleRestoreJob(job.jobId)}
                        disabled={restoring[job.jobId]}
                      >
                        {restoring[job.jobId] ? 'Restoring...' : '↺ Restore'}
                      </button>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="no-jobs">
                <p className="no-jobs-icon">📋</p>
                <h3>No jobs posted yet</h3>
                <p>Create your first job posting to start receiving applications</p>
                <Link to="/post-job" className="apply-btn" style={{ marginTop: '20px' }}>Post a Job</Link>
              </div>
            )}
          </main>
        </div>
        )}
      </div>

      {/* Job Details Modal */}
      {selectedJob && (
        <JobDetailsModal job={selectedJob} onClose={handleCloseModal} />
      )}
    </section>
  );
}

export default RECRUITERDashboard;
