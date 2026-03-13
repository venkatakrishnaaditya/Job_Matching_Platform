import { useState, useEffect } from "react";
import { matchingAPI, applicationsAPI } from "../services/api";
import BackButton from '../components/BackButton';
import JobDetailsModal from '../components/JobDetailsModal';

function BrowseJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [filters, setFilters] = useState({
    searchTerm: "",
    matchMin: 0,
    jobType: "all",
  });

  const [appliedJobs, setAppliedJobs] = useState(new Set());
  const [selectedJob, setSelectedJob] = useState(null);

  // Fetch ranked jobs with match scores from backend
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const response = await matchingAPI.getRankedJobs(0);
        if (response && response.matches) {
          // Transform API response to include match scores
          const transformedJobs = response.matches.map(match => ({
            jobId: match.jobId,
            title: match.title,
            company: match.company || 'Company Name',
            location: match.location,
            jobType: match.jobType,
            workplaceType: match.workplaceType || 'On-site',
            description: match.description,
            requiredSkills: match.requiredSkills || [],
            status: match.status,
            matchScore: Math.round(match.matchScore),
            match: Math.round(match.matchScore),
            salaryMin: match.salaryMin,
            salaryMax: match.salaryMax,
            currency: match.currency || 'USD',
            salary: match.salary,
            experience: match.experience,
            education: match.education,
            breakdown: match.breakdown
          }));
          setJobs(transformedJobs);
        }
      } catch (err) {
        setError('Failed to load jobs. Please try again.');
        console.error('Error fetching jobs:', err);
      } finally {
        setLoading(false);
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
          setAppliedJobs(appliedJobIds);
        }
      } catch (err) {
        console.error('Error fetching applications:', err);
      }
    };

    fetchExistingApplications();
  }, []);

  const handleApply = async (jobId) => {
    try {
      await applicationsAPI.apply(jobId);
      setAppliedJobs((prev) => new Set(prev).add(jobId));
      alert('Application submitted successfully!');
    } catch (err) {
      console.error('Error applying:', err);
      alert('Failed to apply. Please try again.');
    }
  };

   const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      job.title.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
      job.company.toLowerCase().includes(filters.searchTerm.toLowerCase());
    const matchesScore = job.matchScore >= filters.matchMin;
    const matchesType =
      filters.jobType === "all" || job.jobType === filters.jobType;
    return matchesSearch && matchesScore && matchesType;
  });

  return (
    <section className="jobs-section">
      <div className="jobs-container">
        <BackButton />
        {/* HEADER */}
        <div className="jobs-header">
          <h1>Explore Job Opportunities</h1>
          <p>AI-matched positions tailored to your skills and experience</p>
        </div>

        {loading && (
          <div className="loading-message">Loading jobs...</div>
        )}

        {error && (
          <div className="error-message">{error}</div>
        )}

        {!loading && !error && (
          <div className="jobs-content">
          {/* SIDEBAR FILTERS */}
          <aside className="jobs-sidebar">
            <div className="filter-card">
              <h3>Filters</h3>

              <div className="filter-group">
                <label>Search Jobs</label>
                <input
                  type="text"
                  placeholder="Job title or company"
                  value={filters.searchTerm}
                  onChange={(e) =>
                    setFilters({ ...filters, searchTerm: e.target.value })
                  }
                  className="filter-input"
                />
              </div>

              <div className="filter-group">
                <label>Minimum Match Score</label>
                <div className="match-slider-container">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={filters.matchMin}
                    onChange={(e) =>
                      setFilters({ ...filters, matchMin: Number(e.target.value) })
                    }
                    className="match-slider"
                  />
                  <span className="match-value">{filters.matchMin}%</span>
                </div>
              </div>

              <div className="filter-group">
                <label>Job Type</label>
                <select
                  value={filters.jobType}
                  onChange={(e) =>
                    setFilters({ ...filters, jobType: e.target.value })
                  }
                  className="filter-select"
                >
                  <option value="all">All Types</option>
                  <option value="Full-time">Full-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Part-time">Part-time</option>
                </select>
              </div>

              <button
                onClick={() =>
                  setFilters({
                    searchTerm: "",
                    matchMin: 75,
                    jobType: "all",
                  })
                }
                className="filter-reset-btn"
              >
                Reset Filters
              </button>
            </div>

            <div className="stats-card">
              <h4>Your Stats</h4>
              <div className="stat-item">
                <span className="stat-label">Jobs Applied</span>
                <span className="stat-value">{appliedJobs.size}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Jobs Available</span>
                <span className="stat-value">{filteredJobs.length}</span>
              </div>
                <div className="stat-item">
                <span className="stat-label">Avg Match Score</span>
                <span className="stat-value">
                  {filteredJobs.length > 0 
                    ? Math.round(filteredJobs.reduce((sum, job) => sum + job.matchScore, 0) / filteredJobs.length)
                    : 0}%
                </span>
              </div>
            </div>
          </aside>

          {/* JOBS LIST */}
          <main className="jobs-list">
            {filteredJobs.length > 0 ? (
              filteredJobs.map((job) => (
                <div key={job.jobId} className="job-card">
                  <div className="job-header">
                    <div className="job-title-section">
                      <h2 className="job-title">{job.title}</h2>
                      <p className="job-company">{job.company}</p>
                    </div>
                      <div className="job-match-badge">
                      <span className="match-percentage">{job.matchScore}%</span>
                      <p>Match</p>
                    </div>
                  </div>

                  <div className="job-meta">
                    <span className="job-meta-item">
                      <span className="icon">📍</span> {job.location}
                    </span>
                    <span className="job-meta-item">
                      <span className="icon">💼</span> {job.jobType}
                    </span>
                    <span className="job-meta-item">
                      <span className="icon">🏢</span> {job.workplaceType}
                    </span>
                    {job.salaryMin && job.salaryMax && (
                      <span className="job-meta-item">
                        <span className="icon">💰</span> {job.currency} {job.salaryMin.toLocaleString()} - {job.salaryMax.toLocaleString()}
                      </span>
                    )}
                  </div>

                  <p className="job-description">
                    {job.description ? job.description.substring(0, 150) + '...' : 'No description available'}
                  </p>

                  <div className="job-skills">
                    {job.requiredSkills && job.requiredSkills.length > 0 ? (
                      job.requiredSkills.map((skill, idx) => (
                        <span key={idx} className="skill-tag">
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span className="skill-tag">No skills listed</span>
                    )}
                  </div>

                  <div className="job-actions">
                    {appliedJobs.has(job.jobId) ? (
                      <button className="apply-btn applied" disabled>
                        ✓ Applied
                      </button>
                     ) : (
                      <button
                        className="apply-btn"
                        onClick={() => handleApply(job.jobId)}
                      >
                        Apply Now
                      </button>
                    )}
                    <button onClick={() => setSelectedJob(job)} className="save-btn">View Details</button>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-jobs">
                <p className="no-jobs-icon">🔍</p>
                <h3>No jobs found</h3>
                <p>Try adjusting your filters to see more opportunities</p>
              </div>
            )}
          </main>
        </div>
        )}
      </div>

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

export default BrowseJobs;
