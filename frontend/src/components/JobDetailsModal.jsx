import React from 'react';

function JobDetailsModal({ job, onClose }) {
  if (!job) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <div className="modal-header">
          <h1 className="modal-job-title">{job.title}</h1>
          <p className="modal-job-company">{job.company}</p>
        </div>

        <div className="modal-meta">
          <span className="modal-meta-item">
            <span className="icon">📍</span> {job.location || 'Not specified'}
          </span>
          <span className="modal-meta-item">
            <span className="icon">💼</span> {job.jobType || 'Not specified'}
          </span>
          {job.numberOfOpenings && (
            <span className="modal-meta-item">
              <span className="icon">👥</span> {job.numberOfOpenings} {job.numberOfOpenings === 1 ? 'opening' : 'openings'}
            </span>
          )}
          {job.status && (
            <span className={`status-badge ${job.status.toLowerCase()}`}>
              {job.status}
            </span>
          )}
          {job.match !== undefined && (
            <span className="modal-meta-item">
              <span className="icon">✨</span> {job.match}% Match
            </span>
          )}
        </div>

        <div className="modal-section">
          <h3>📄 Original Job Posting</h3>
          <p>{job.description || 'No description available'}</p>
        </div>

        <div className="modal-section">
          <h3>✨ Key Information (AI Extracted)</h3>
          <h3>Required Skills</h3>
          <div className="modal-skills">
            {job.requiredSkills && job.requiredSkills.length > 0 ? (
              job.requiredSkills.map((skill, idx) => (
                <span key={idx} className="skill-tag">{skill}</span>
              ))
            ) : (
              <span>No required skills listed</span>
            )}
          </div>
        </div>

        {job.preferredSkills && job.preferredSkills.length > 0 && (
          <div className="modal-section">
            <h3>Preferred Skills</h3>
            <div className="modal-skills">
              {job.preferredSkills.map((skill, idx) => (
                <span key={idx} className="skill-tag skill-tag-secondary">{skill}</span>
              ))}
            </div>
          </div>
        )}

        <div className="modal-section">
          <h3>Structured Details</h3>
          <div className="modal-requirements">
            {(() => {
              // Handle both formatted (from matching API) and raw (from jobs API) data
              const experience = job.experience || 
                (job.minExperience !== undefined ? `${job.minExperience}-${job.maxExperience || job.minExperience} years` : null);
              const education = job.education || job.educationLevel;
              const salary = job.salary || 
                (job.salaryMin !== undefined ? `${job.currency || '$'}${job.salaryMin} - ${job.currency || '$'}${job.salaryMax || job.salaryMin}` : null);
              
              return (
                <>
                  {experience && (
                    <div className="requirement-item">
                      <strong>Experience:</strong> {experience}
                    </div>
                  )}
                  {education && (
                    <div className="requirement-item">
                      <strong>Education:</strong> {education}
                    </div>
                  )}
                  {salary && (
                    <div className="requirement-item">
                      <strong>Salary:</strong> {salary}
                    </div>
                  )}
                  {!experience && !education && !salary && (
                    <p>No specific requirements listed</p>
                  )}
                </>
              );
            })()}
          </div>
        </div>

        {/* {job.breakdown && (
          <div className="modal-section">
            <h3>Match Score Breakdown</h3>
            <div className="modal-requirements">
              <div className="requirement-item">
                <strong>Skills Match:</strong> {Math.round(job.breakdown.skillsScore || 0)}%
              </div>
              <div className="requirement-item">
                <strong>Experience Match:</strong> {Math.round(job.breakdown.experienceScore || 0)}%
              </div>
              <div className="requirement-item">
                <strong>Education Match:</strong> {Math.round(job.breakdown.educationScore || 0)}%
              </div>
            </div>
          </div>
        )} */}

        {job.responsibilities && (
          <div className="modal-section">
            <h3>Responsibilities</h3>
            <p>{job.responsibilities}</p>
          </div>
        )}

        {job.benefits && (
          <div className="modal-section">
            <h3>Benefits</h3>
            <p>{job.benefits}</p>
          </div>
        )}

        {job.applicationDeadline && (
          <div className="modal-section">
            <h3>Application Deadline</h3>
            <p>{new Date(job.applicationDeadline).toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}</p>
          </div>
        )}

        <div className="modal-footer">
          <p className="modal-footer-note">This is how candidates see your job posting</p>
        </div>
      </div>
    </div>
  );
}

export default JobDetailsModal;
